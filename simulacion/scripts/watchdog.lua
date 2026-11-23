-- Estado y reloj del latido de comunicación, mantenidos en la escena.
local function crearWatchdog(plazo)
    local wd = {sesion = 0, secuencia = 0, ultimo = 0, enclavado = false}
    function wd:nuevaSesion(sesion, t)
        if sesion <= self.sesion then return false end
        if self.sesion ~= 0 then
            self.enclavado = true
            self.fallo_s = t
            self.ultimo = nil
        else
            self.ultimo = t
        end
        self.sesion, self.secuencia = sesion, 0
        return true
    end
    function wd:latido(sesion, secuencia, t)
        if sesion ~= self.sesion or secuencia <= self.secuencia then return false end
        self.secuencia, self.ultimo = secuencia, t
        return true
    end
    function wd:vigente(t)
        return self.ultimo ~= nil and t - self.ultimo < plazo - 1e-9
    end
    function wd:avanzar(t)
        if not self:vigente(t) and not self.enclavado then
            self.enclavado, self.fallo_s = true, t
        end
    end
    function wd:reconocer(t)
        if self:vigente(t) then self.enclavado = false end
    end
    return wd
end
