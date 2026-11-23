package org.afev.proofs;

import java.nio.file.*;
import java.util.*;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.eclipse.core.resources.*;
import org.eclipse.core.runtime.*;
import org.eclipse.core.runtime.jobs.Job;
import org.rodinp.core.*;
import org.eventb.core.*;
import org.eventb.core.pm.*;
import org.eventb.core.seqprover.*;

/** Importa una copia aislada, construye, prueba y exporta evidencia nativa. */
public class VerificarM1 implements IApplication {
    public Object start(IApplicationContext context) throws Exception {
        String[] args = (String[]) context.getArguments().get(IApplicationContext.APPLICATION_ARGS);
        String objetivo = args.length > 2 ? args[2] : "M1";
        boolean replay = args.length > 3 && args[3].equals("--replay");
        String[] modelos = objetivo.equals("M2")
                ? new String[] {"C0", "M0", "C1", "M1", "C2", "M2"}
                : new String[] {"C0", "M0", "C1", "M1"};
        Set<String> componentes = Set.of(modelos);
        java.nio.file.Path fuente = Paths.get(args[0]);
        java.nio.file.Path evidencia = Paths.get(args[1]);
        Files.createDirectories(evidencia);
        IWorkspace ws = ResourcesPlugin.getWorkspace();
        IWorkspaceDescription descripcion = ws.getDescription();
        descripcion.setAutoBuilding(false);
        ws.setDescription(descripcion);
        IProject proyecto = ws.getRoot().getProject("Enclavamiento");
        if (!proyecto.exists()) proyecto.create(null);
        proyecto.open(null);
        IProjectDescription pd = proyecto.getDescription();
        pd.setNatureIds(new String[] {"org.rodinp.core.rodinnature"});
        proyecto.setDescription(pd, null);
        java.nio.file.Path copia = proyecto.getLocation().toFile().toPath();
        try (var entradas = Files.list(fuente)) {
            for (java.nio.file.Path p : entradas.toList()) {
                String nombre = p.getFileName().toString();
                if ((nombre.endsWith(".buc") || nombre.endsWith(".bum") || nombre.endsWith(".bpr"))
                        && componentes.contains(nombre.substring(0, nombre.length() - 4))) {
                    Files.copy(p, copia.resolve(nombre), StandardCopyOption.REPLACE_EXISTING);
                }
            }
        }
        proyecto.refreshLocal(IResource.DEPTH_INFINITE, null);
        ws.build(IncrementalProjectBuilder.FULL_BUILD, null);
        Job.getJobManager().join(ResourcesPlugin.FAMILY_AUTO_BUILD, null);
        int errores = 0;
        for (IMarker marker : proyecto.findMarkers(IMarker.PROBLEM, true, IResource.DEPTH_INFINITE)) {
            int severidad = marker.getAttribute(IMarker.SEVERITY, 0);
            System.out.println("MARKER " + marker.getResource().getName() + " severity=" + severidad + " " + marker.getAttribute(IMarker.MESSAGE, ""));
            if (severidad == IMarker.SEVERITY_ERROR) errores++;
        }
        System.out.println("STATIC_ERRORS=" + errores);
        if (errores > 0) return 2;
        IRodinProject rp = RodinCore.valueOf(proyecto);
        int total = 0;
        int cerradas = 0;
        List<String> filas = new ArrayList<>();
        filas.add("modelo,obligacion,confianza,manual,rota");
        for (String nombre : modelos) {
            IPORoot po = (IPORoot) rp.getRodinFile(nombre + ".bpo").getRoot();
            IProofComponent componente = EventBPlugin.getProofManager().getProofComponent(po);
            componente.makeConsistent(null);
            for (IPOSequent seq : po.getSequents()) {
                String id = seq.getElementName();
                IProofAttempt intento = componente.createProofAttempt(id, "afev", null);
                IProofTree arbol = intento.getProofTree();
                if (replay) {
                    IProofSkeleton guardado = componente.getPRRoot().getProof(id).getSkeleton(arbol.getFormulaFactory(), null);
                    IProofTree nuevo = ProverFactory.makeProofTree(arbol.getSequent(), null);
                    Object resultadoReplay = org.eventb.core.seqprover.tactics.BasicTactics.replayTac(guardado).apply(nuevo.getRoot(), null);

                    System.out.println("REPLAY " + nombre + " " + id + " closed=" + nuevo.isClosed());
                    if (!nuevo.isClosed()) throw new IllegalStateException("Fallo al reproducir " + nombre + "/" + id + " resultado=" + resultadoReplay);
                    arbol = nuevo;
                }
                if (!replay && !arbol.isClosed()) {
                    String[] preparacion = {"org.eventb.core.seqprover.autoRewriteTac", "org.eventb.core.seqprover.typeRewriteTac", "org.eventb.core.seqprover.impGoalTac", "org.eventb.core.seqprover.conjGoalTac"};
                    for (int vuelta = 0; vuelta < 2; vuelta++) {
                        for (String tactica : preparacion) {
                            ITactic paso = SequentProver.getAutoTacticRegistry().getTacticDescriptor(tactica).getTacticInstance();
                            for (IProofTreeNode nodo : arbol.getRoot().getOpenDescendants()) paso.apply(nodo, null);
                        }
                        for (IProofTreeNode nodo : arbol.getRoot().getOpenDescendants()) {
                            var posiciones = org.eventb.core.seqprover.eventbExtensions.Tactics.arithGetPositions(nodo.getSequent().goal());
                            if (!posiciones.isEmpty()) org.eventb.core.seqprover.eventbExtensions.Tactics.arithRewrites(null, posiciones.get(0)).apply(nodo, null);
                        }
                    }
                    ITactic pp = SequentProver.getAutoTacticRegistry().getTacticDescriptor("org.eventb.pp.ppUnrestricted").getTacticInstance();
                    for (IProofTreeNode nodo : arbol.getRoot().getOpenDescendants()) pp.apply(nodo, null);
                    var registroTacticas = SequentProver.getAutoTacticRegistry();
                    String smtId = "org.eventb.smt.core.SMTParam";
                    if (!arbol.isClosed() && registroTacticas.isRegisteredParameterizer(smtId)) {
                        var descriptor = registroTacticas.getParameterizerDescriptor(smtId);
                        var opciones = descriptor.makeParameterSetting();
                        opciones.setString("configName", "veriT");
                        opciones.setBoolean("restricted", false);
                        opciones.setLong("timeOutDelay", 4000L);
                        ITactic smt = descriptor.instantiate(opciones, "veriT sin restricción").getTacticInstance();
                        for (IProofTreeNode nodo : arbol.getRoot().getOpenDescendants()) smt.apply(nodo, null);
                    }
                }
                System.out.println("PO " + nombre + " " + id + " confidence=" + arbol.getConfidence() + " closed=" + arbol.isClosed());
                if (arbol.isClosed()) cerradas++;
                else System.out.println("GOAL " + arbol.getRoot().getFirstOpenDescendant().getSequent());
                total++;
                if (!replay) intento.commit(false, null);
                intento.dispose();
                componente.save(null, true);
                IPSStatus status = componente.getStatus(id);
                if (replay) status.copyProofInfo(null);
                filas.add(nombre + "," + id + "," + status.getConfidence() + "," + status.getHasManualProof() + "," + status.isBroken());
            }
        }
        Files.write(evidencia.resolve("estados.csv"), filas);
        String contexto = objetivo.equals("M2") ? "C2" : "C1";
        String[] archivos = {contexto + ".bcc", contexto + ".bpr", contexto + ".bpo", contexto + ".bps", objetivo + ".bcm", objetivo + ".bpr", objetivo + ".bpo", objetivo + ".bps"};
        for (String nombre : archivos) {
            java.nio.file.Path p = copia.resolve(nombre);
            if (Files.exists(p)) Files.copy(p, evidencia.resolve(nombre), StandardCopyOption.REPLACE_EXISTING);
        }
        ws.save(true, null);
        System.out.println("TOTAL=" + total + " CLOSED=" + cerradas);
        return total == cerradas ? EXIT_OK : 3;
    }
    public void stop() {}
}
