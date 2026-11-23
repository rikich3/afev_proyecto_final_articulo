-- Planta discreta simulada dentro de CoppeliaSim. El cliente envía órdenes,
-- mientras que este script conserva estados, actualiza actuadores y mide la escena.
local sim = require('sim')
local p, cfg, wd, h, inicio, historial, rfid
local EPS = 1e-9
local function reloj() return sim.getSimulationTime() end

local function dentro(id)
    local x = sim.getObjectPosition(h.operarios[id], sim.handle_world)
    -- Envolvente horizontal del avatar, independiente del detector de proximidad.
    return math.abs(x[1]) <= 2.20 + 0.38 and math.abs(x[2]) <= 1.50 + 0.18
end

local function ocupantes()
    local lista = {}
    for id = 1, 2 do if dentro(id) then lista[#lista + 1] = id end end
    return lista
end

local function bloqueos()
    local lista = {}
    for id = 1, 2 do if p.bloqueos[id] then lista[#lista + 1] = id end end
    return lista
end

local function parada()
    return math.abs(p.velocidad) <= cfg.epsilon_parada_m_s
end

local function aislado()
    return sim.getJointPosition(h.seccionador) > 1
end

local function puertaCerrada()
    return math.abs(sim.getJointPosition(h.puerta)) < 0.01
end

local function permisoFisico()
    return p.orden.permiso_acceso == true and not wd.enclavado and wd:vigente(reloj())
        and not p.emergencia and not p.contacto and aislado() and parada()
        and p.bloqueos[1] and p.bloqueos[2]
end

function verdad()
    local xy = {}
    for id = 1, 2 do xy[id] = sim.getObjectPosition(h.operarios[id], sim.handle_world) end
    return {
        tick = p.tick, t_sim_s = reloj(), ocupantes_reales = ocupantes(),
        posiciones_m = xy, potencia_real = p.contacto and not aislado(),
        contacto_real_cerrado = p.contacto, velocidad_real_m_s = p.velocidad,
        puerta_real_cerrada = puertaCerrada(), seccionador_real_abierto = aislado(),
        bloqueos_reales = bloqueos(), permiso_efectivo = permisoFisico(),
        fallo_watchdog = wd.enclavado, ultimo_heartbeat_s = wd.ultimo,
        fallo_watchdog_s = wd.fallo_s, apertura_s = p.apertura_s,
        parada_s = p.parada_s,
    }
end

function sysCall_init()
    h = {operarios = {}, ejes = {}, candados = {}, luces = {}}
    local mina = sim.getObject('/mina')
    cfg = sim.readCustomTableData(mina, 'parametros_banco')
    if not cfg or not cfg.heartbeat_timeout_s then
        cfg = {heartbeat_timeout_s = 0.1, contact_open_delay_s = 0.02,
            epsilon_parada_m_s = 0.001, velocidad_nominal_m_s = 0.5}
    end
    h.puerta = sim.getObject('/mina/puerta')
    h.seccionador = sim.getObject('/mina/panel/seccionador')
    h.sensor = sim.getObject('/mina/sensor_presencia')
    h.barrera = sim.getObject('/mina/sensor_barrera')
    h.contacto = sim.getObject('/mina/panel/contacto_potencia')
    inicio = {}
    for id = 1, 2 do
        h.operarios[id] = sim.getObject('/mina/operario_' .. id)
        h.ejes[id] = sim.getObject('/mina/faja/eje_rodillo_' .. id)
        h.candados[id] = sim.getObject('/mina/panel/bloqueo_' .. id)
        inicio[id] = sim.getObjectPosition(h.operarios[id], sim.handle_world)
    end
    for i = 1, 3 do h.luces[i] = sim.getObject('/mina/panel/baliza/lente_' .. i) end
    wd = crearWatchdog(cfg.heartbeat_timeout_s)
    wd.ultimo = reloj()
    p = {tick = 0, contacto = false, pegado = false, velocidad = 0,
        emergencia = false, bloqueos = {}, orden = {}, serie_rfid = 0}
    historial, rfid = {}, {}
end

function nuevaSesion(sesion)
    if not wd:nuevaSesion(sesion, reloj()) then return false end
    p.orden = {}
    return true
end

function latido(sesion, secuencia)
    return wd:latido(sesion, secuencia, reloj())
end

function ordenar(sesion, orden)
    if sesion ~= wd.sesion or not wd:vigente(reloj()) then return false end
    p.orden = orden
    return true
end

function tomarMuestra()
    local detectado, libre = false, true
    for id = 1, 2 do
        if sim.checkProximitySensor(h.sensor, h.operarios[id]) > 0 then detectado = true end
        if sim.checkProximitySensor(h.barrera, h.operarios[id]) > 0 then libre = false end
    end
    local muestra = {
        tick = p.tick, t_sim_s = reloj(), laser_ocupado = detectado,
        barrera_libre = libre, puerta_cerrada = puertaCerrada(),
        contacto_cerrado = p.contacto, seccionador_abierto = aislado(),
        bloqueos_confirmados = bloqueos(), velocidad_m_s = p.velocidad,
        emergencia = p.emergencia, fallo_watchdog = wd.enclavado,
        heartbeat_vigente = wd:vigente(reloj()), sensor_valid = true,
        sensor_age_s = 0, rfid_eventos = rfid,
    }
    rfid = {}
    return muestra
end

function moverOperario(id, entrada, forzar)
    if entrada and not forzar and (not permisoFisico() or puertaCerrada()) then return false end
    local destino = entrada and {(id == 1 and -1.18 or 1.15), -1.03, inicio[id][3]} or inicio[id]
    sim.setObjectPosition(h.operarios[id], destino, sim.handle_world)
    p.serie_rfid = p.serie_rfid + 1
    local evento = {event_id = 'rfid-' .. p.serie_rfid, operario_id = id,
        accion = entrada and 'ingreso' or 'salida'}
    rfid[#rfid + 1] = evento
    return true
end

function aproximar(id)
    sim.setObjectPosition(h.operarios[id], {id == 1 and -0.30 or 0.30, -1.85, inicio[id][3]}, sim.handle_world)
    return moverOperario(id, true, false)
end

function forzarCondicion(tipo, valor)
    if tipo == 'contacto_pegado' then p.pegado = valor
    elseif tipo == 'emergencia' then p.emergencia = valor
    elseif tipo == 'movimiento_residual' then p.residual_forzado = valor
    else error('Condición no reconocida: ' .. tipo) end
end

function sysCall_actuation()
    local t, dt = reloj(), sim.getSimulationTimeStep()
    wd:avanzar(t)
    local orden = p.orden
    local sinOcupantes = #ocupantes() == 0
    local sinBloqueos = #bloqueos() == 0
    if orden.reset_watchdog and sinOcupantes and sinBloqueos and not p.contacto
            and parada() and puertaCerrada() and not aislado() and not p.emergencia then
        wd:reconocer(t)
    end
    local activo = wd:vigente(t) and not wd.enclavado and not p.emergencia
    local demanda = activo and orden.orden_contactor and puertaCerrada()
        and not aislado() and sinBloqueos
    if demanda then
        p.corte_desde = nil
        if not p.contacto and sinOcupantes then
            p.contacto = true
            p.apertura_s, p.parada_s = nil, nil
        end
    elseif p.contacto then
        p.corte_desde = p.corte_desde or t
        if not p.pegado and t - p.corte_desde + EPS >= cfg.contact_open_delay_s then
            p.contacto, p.apertura_s = false, t
        end
    end
    if p.contacto and not aislado() then
        p.velocidad = cfg.velocidad_nominal_m_s
    elseif p.residual_forzado then
        p.velocidad = p.residual_forzado
    else
        p.velocidad = math.max(0, p.velocidad - 1.5 * dt)
    end
    if not p.contacto and p.apertura_s and parada() and not p.parada_s then p.parada_s = t end

    if activo then
        if orden.orden_seccionador == 'ABRIR' and not p.contacto then
            sim.setJointPosition(h.seccionador, math.pi / 2)
        elseif orden.orden_seccionador == 'CERRAR' and puertaCerrada() and sinOcupantes and sinBloqueos then
            sim.setJointPosition(h.seccionador, 0)
        end
        for _, par in ipairs(orden.acciones_bloqueo or {}) do
            local id, accion = par[1], par[2]
            if accion == 'APLICAR' and aislado() and not p.contacto then p.bloqueos[id] = true end
            if accion == 'RETIRAR' and sinOcupantes and aislado() then p.bloqueos[id] = false end
        end
        if orden.orden_puerta == 'ABRIR' and permisoFisico() then
            sim.setJointPosition(h.puerta, math.pi / 2)
        elseif orden.orden_puerta == 'CERRAR' and sinOcupantes then
            sim.setJointPosition(h.puerta, 0)
        end
    end
    for id = 1, 2 do
        sim.setJointPosition(h.ejes[id], sim.getJointPosition(h.ejes[id]) + p.velocidad * dt / 0.08)
        sim.setShapeColor(h.candados[id], nil, sim.colorcomponent_ambient_diffuse,
            p.bloqueos[id] and {0.12, 0.47, 0.90} or {0.28, 0.31, 0.35})
    end
    sim.setShapeColor(h.contacto, nil, sim.colorcomponent_ambient_diffuse,
        p.contacto and {0.92, 0.20, 0.12} or {0.14, 0.66, 0.34})
    local luces = {p.contacto, permisoFisico(), wd.enclavado or p.emergencia or orden.alarma == true}
    for id, luz in ipairs(h.luces) do
        local nivel = luces[id] and 0.7 or 0
        sim.setShapeColor(luz, nil, sim.colorcomponent_emission, {nivel, nivel, nivel})
    end
    p.tick = p.tick + 1
end

function sysCall_sensing()
    if #historial < 3000 then historial[#historial + 1] = verdad() end
end

function leerHistorial(desde)
    local muestra = {}
    for _, fila in ipairs(historial) do
        if fila.tick > desde then muestra[#muestra + 1] = fila end
    end
    return muestra
end
