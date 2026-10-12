local sim = require('sim')
local textUtils = require('textUtils')

if sim.getSimulationState() ~= sim.simulation_stopped then
    error('Deten la simulacion antes de crear la escena.')
end
if sim.getObject('/mina', {noError = true}) ~= -1 then
    error('Ya existe /mina. Abre inicial.ttt para generar una escena nueva.')
end

local root
local created = {}
local colors = {
    steel = {0.22, 0.29, 0.34},
    silver = {0.62, 0.68, 0.70},
    mesh = {0.34, 0.40, 0.42},
    belt = {0.075, 0.09, 0.10},
    tread = {0.15, 0.17, 0.18},
    yellow = {1.00, 0.70, 0.035},
    blue = {0.08, 0.30, 0.68},
    orange = {0.96, 0.32, 0.045},
    red = {0.80, 0.045, 0.035},
    green = {0.10, 0.44, 0.23},
    white = {0.90, 0.94, 0.93},
    concrete = {0.48, 0.52, 0.53},
    skin = {0.70, 0.48, 0.32},
}

local function place(handle, name, position, parent)
    created[#created + 1] = handle
    sim.setObjectAlias(handle, name)
    sim.setObjectParent(handle, parent or root, true)
    sim.setObjectPosition(handle, position)
    return handle
end

local function group(name, position, parent)
    local handle = place(sim.createDummy(0.005), name, position, parent)
    sim.setObjectProperty(handle, sim.objectproperty_selectable | sim.objectproperty_collapsed)
    return handle
end

local function shape(name, kind, size, position, color, parent)
    local handle = place(sim.createPrimitiveShape(kind, size, 0), name, position, parent)
    sim.setBoolProperty(handle, 'dynamic', false)
    sim.setBoolProperty(handle, 'respondable', false)
    sim.setShapeColor(handle, nil, sim.colorcomponent_ambient_diffuse, color)
    sim.setShapeColor(handle, nil, sim.colorcomponent_specular, {0.15, 0.15, 0.15})
    return handle
end

local function box(name, size, position, color, parent)
    return shape(name, sim.primitiveshape_cuboid, size, position, color, parent)
end

local function cylinder(name, size, position, color, parent)
    return shape(name, sim.primitiveshape_cylinder, size, position, color, parent)
end

local function ball(name, size, position, color, parent)
    return shape(name, sim.primitiveshape_spheroid, size, position, color, parent)
end

local function rod(name, start, finish, diameter, color, parent)
    local dx, dy, dz = finish[1] - start[1], finish[2] - start[2], finish[3] - start[3]
    local length = math.sqrt(dx * dx + dy * dy + dz * dz)
    local center = {(start[1] + finish[1]) / 2, (start[2] + finish[2]) / 2, (start[3] + finish[3]) / 2}
    local handle = cylinder(name, {diameter, diameter, length}, center, color, parent)
    -- Rotate the cylinder's local Z axis onto the segment direction.
    if dz / length < -0.999999 then
        sim.setObjectQuaternion(handle, {1, 0, 0, 0})
    else
        local denominator = math.sqrt(2 * (1 + dz / length))
        sim.setObjectQuaternion(handle, {-dy / length / denominator, dx / length / denominator, 0, denominator / 2})
    end
    return handle
end

local function label(name, value, height, position, parent, onFloor, color)
    local handle = group(name, {0, 0, 0}, parent)
    textUtils.generateTextShape(value, color or colors.white, height, true, nil, handle)
    sim.setObjectAlias(handle, name)
    sim.setObjectPosition(handle, position)
    if not onFloor then
        sim.setObjectOrientation(handle, {math.pi / 2, 0, 0})
    end
    return handle
end

local function revolute(name, position, parent, cyclic, range)
    local joint = sim.createJoint(sim.joint_revolute, sim.jointmode_kinematic, 0, {0.06, 0.025})
    local handle = place(joint, name, position, parent)
    sim.setJointInterval(handle, cyclic, {0, range})
    sim.setJointPosition(handle, 0)
    return handle
end

local function floor()
    local base = box('plataforma', {6.6, 5.6, 0.10}, {0.25, -0.35, 0.015}, colors.concrete)
    local zone = box('zona_peligro', {4.40, 3.00, 0.008}, {0, 0, 0.07}, {0.39, 0.43, 0.44})
    for _, y in ipairs({-1.45, 1.45}) do
        box('limite', {4.40, 0.10, 0.008}, {0, y, 0.079}, colors.yellow, zone)
        for i = 0, 21 do
            box('marca', {0.10, 0.102, 0.009}, {-2.10 + i * 0.20, y, 0.080}, colors.belt, zone)
        end
    end
    for _, x in ipairs({-2.15, 2.15}) do
        box('limite', {0.10, 2.80, 0.008}, {x, 0, 0.079}, colors.yellow, zone)
    end
    box('paso_acceso', {1.00, 1.05, 0.008}, {0, -2.03, 0.07}, {0.28, 0.36, 0.38}, base)
    label('rotulo_acceso', 'ACCESO', 0.13, {0, -2.45, 0.08}, base, true)
    return base
end

local function conveyor()
    local frame = box('faja', {3.10, 0.88, 0.14}, {0, 0.15, 0.82}, colors.steel)
    box('superficie_faja', {2.92, 0.73, 0.04}, {0, 0.15, 0.92}, colors.belt, frame)
    box('retorno', {2.92, 0.73, 0.025}, {0, 0.15, 0.68}, colors.belt, frame)
    for i = 0, 17 do
        box('union_banda_' .. i, {0.012, 0.72, 0.006}, {-1.40 + i * 0.165, 0.15, 0.943}, colors.tread, frame)
    end
    for i, x in ipairs({-1.10, 0, 1.10}) do
        for side, y in ipairs({-0.18, 0.48}) do
            box('pata_' .. i .. '_' .. side, {0.08, 0.08, 0.64}, {x, y, 0.42}, colors.steel, frame)
            box('placa_anclaje', {0.20, 0.18, 0.035}, {x, y, 0.09}, colors.silver, frame)
        end
        rod('travesano', {x, -0.20, 0.30}, {x, 0.50, 0.30}, 0.05, colors.silver, frame)
    end
    for i, x in ipairs({-1.43, 1.43}) do
        local axis = revolute('eje_rodillo_' .. i, {x, 0.15, 0.80}, frame, true, 2 * math.pi)
        sim.setObjectOrientation(axis, {math.pi / 2, 0, 0})
        local roller = cylinder('rodillo_' .. i, {0.26, 0.26, 0.78}, {x, 0.15, 0.80}, colors.silver, axis)
        sim.setObjectOrientation(roller, {math.pi / 2, 0, 0})
        box('marca_giro', {0.10, 0.006, 0.018}, {x, -0.245, 0.80}, colors.yellow, roller)
    end
    for _, y in ipairs({-0.30, 0.60}) do
        box('guarda_lateral', {2.70, 0.055, 0.10}, {0, y, 0.89}, colors.yellow, frame)
    end
    local motor = cylinder('motor', {0.25, 0.25, 0.40}, {1.08, 0.86, 0.77}, colors.blue, frame)
    sim.setObjectOrientation(motor, {math.pi / 2, 0, 0})
    box('reductor', {0.28, 0.22, 0.27}, {1.40, 0.75, 0.77}, colors.steel, frame)
    for i = 0, 5 do
        local fin = cylinder('aleta_motor', {0.27, 0.27, 0.015}, {1.08, 0.70 + i * 0.055, 0.77}, colors.steel, motor)
        sim.setObjectOrientation(fin, {math.pi / 2, 0, 0})
    end
    box('placa_faja', {1.05, 0.015, 0.16}, {0, -0.30, 0.79}, colors.steel, frame)
    label('rotulo_faja', 'FAJA 01', 0.105, {0, -0.312, 0.745}, frame)
end

local function fence(name, a, b, parent, color)
    local panel = group(name, {0, 0, 0}, parent)
    local dx, dy = b[1] - a[1], b[2] - a[2]
    local length = math.sqrt(dx * dx + dy * dy)
    for _, z in ipairs({0.18, 1.48}) do
        rod('marco', {a[1], a[2], z}, {b[1], b[2], z}, 0.035, color, panel)
    end
    for _, point in ipairs({a, b}) do
        rod('marco', {point[1], point[2], 0.18}, {point[1], point[2], 1.48}, 0.035, color, panel)
    end
    local steps = math.ceil(length / 0.16)
    for i = 1, steps - 1 do
        local x, y = a[1] + dx * i / steps, a[2] + dy * i / steps
        rod('malla_vertical', {x, y, 0.20}, {x, y, 1.46}, 0.009, colors.mesh, panel)
    end
    for i = 1, 7 do
        local z = 0.18 + i * 0.1625
        rod('malla_horizontal', {a[1], a[2], z}, {b[1], b[2], z}, 0.009, colors.mesh, panel)
    end
    return panel
end

local function perimeter()
    local rail = group('perimetro', {0, 0, 0})
    local posts = {
        {-2.20, -1.50}, {2.20, -1.50}, {-2.20, 1.50},
        {2.20, 1.50}, {-0.55, -1.50}, {0.55, -1.50},
    }
    for _, point in ipairs(posts) do
        box('poste', {0.07, 0.07, 1.48}, {point[1], point[2], 0.82}, colors.yellow, rail)
        box('base_poste', {0.17, 0.17, 0.04}, {point[1], point[2], 0.09}, colors.steel, rail)
    end
    fence('cerco_izquierdo', {-2.20, -1.50}, {-2.20, 1.50}, rail, colors.steel)
    fence('cerco_derecho', {2.20, -1.50}, {2.20, 1.50}, rail, colors.steel)
    fence('cerco_fondo', {-2.20, 1.50}, {2.20, 1.50}, rail, colors.steel)
    fence('cerco_frente_izquierdo', {-2.20, -1.50}, {-0.55, -1.50}, rail, colors.steel)
    fence('cerco_frente_derecho', {0.55, -1.50}, {2.20, -1.50}, rail, colors.steel)
    local gate = revolute('puerta', {-0.55, -1.50, 0.82}, nil, false, math.pi / 2)
    fence('hoja', {-0.52, -1.50}, {0.52, -1.50}, gate, colors.yellow)
    rod('tirador', {0.40, -1.56, 0.77}, {0.40, -1.56, 1.00}, 0.025, colors.silver, gate)
    box('placa_acceso', {0.70, 0.025, 0.22}, {0, -1.53, 1.27}, colors.steel, gate)
    label('rotulo_puerta', 'ACCESO', 0.085, {0, -1.55, 1.23}, gate)
    box('enclavamiento', {0.10, 0.09, 0.20}, {0.58, -1.50, 1.03}, colors.red, rail)
    box('senal_peligro', {1.18, 0.025, 0.29}, {-1.40, -1.52, 1.29}, colors.yellow, rail)
    label('rotulo_peligro', 'ZONA DE RIESGO', 0.085, {-1.40, -1.545, 1.25}, rail, false, colors.belt)
end

local function worker(id, x, y, color)
    local body = box('operario_' .. id, {0.36, 0.23, 0.45}, {x, y, 1.13}, color)
    box('cinturon', {0.37, 0.24, 0.045}, {x, y, 0.925}, colors.belt, body)
    for _, dx in ipairs({-0.095, 0.095}) do
        rod('pierna', {x + dx, y, 0.22}, {x + dx, y, 0.92}, 0.125, colors.blue, body)
        box('bota', {0.15, 0.28, 0.12}, {x + dx, y - 0.04, 0.13}, colors.belt, body)
        box('reflectante', {0.05, 0.012, 0.37}, {x + dx, y - 0.122, 1.14}, colors.white, body)
    end
    box('reflectante_cintura', {0.36, 0.012, 0.045}, {x, y - 0.122, 1.01}, colors.white, body)
    for _, side in ipairs({-1, 1}) do
        ball('hombro', {0.16, 0.18, 0.18}, {x + side * 0.23, y, 1.27}, colors.blue, body)
        rod('brazo', {x + side * 0.23, y, 1.25}, {x + side * 0.29, y - 0.03, 0.96}, 0.12, colors.blue, body)
        ball('guante', {0.12, 0.13, 0.16}, {x + side * 0.29, y - 0.03, 0.88}, colors.belt, body)
    end
    cylinder('cuello', {0.10, 0.10, 0.10}, {x, y, 1.39}, colors.skin, body)
    ball('cabeza', {0.23, 0.22, 0.27}, {x, y, 1.52}, colors.skin, body)
    box('gafas', {0.20, 0.035, 0.055}, {x, y - 0.105, 1.55}, colors.belt, body)
    local helmet = ball('casco_' .. id, {0.29, 0.28, 0.18}, {x, y, 1.665}, colors.yellow, body)
    cylinder('ala_casco', {0.33, 0.33, 0.025}, {x, y, 1.60}, colors.yellow, helmet)
    label('identificador', 'OP ' .. id, 0.065, {x, y - 0.13, 1.18}, body)
    sim.setObjectProperty(body, sim.objectproperty_selectable | sim.objectproperty_collapsed)
    return body
end

local function padlock(name, x, color, parent)
    local lock = box(name, {0.075, 0.045, 0.10}, {x, -1.67, 0.93}, color, parent)
    rod('arco_izquierdo', {x - 0.026, -1.67, 0.97}, {x - 0.026, -1.67, 1.04}, 0.012, colors.silver, lock)
    rod('arco_derecho', {x + 0.026, -1.67, 0.97}, {x + 0.026, -1.67, 1.04}, 0.012, colors.silver, lock)
    rod('arco_superior', {x - 0.026, -1.67, 1.04}, {x + 0.026, -1.67, 1.04}, 0.012, colors.silver, lock)
end

local function panel()
    local cabinet = box('panel', {0.62, 0.26, 0.90}, {2.78, -1.45, 1.15}, colors.steel)
    box('pedestal', {0.12, 0.12, 0.62}, {2.78, -1.45, 0.40}, colors.silver, cabinet)
    box('pie', {0.48, 0.40, 0.06}, {2.78, -1.45, 0.095}, colors.steel, cabinet)
    box('frente', {0.56, 0.015, 0.83}, {2.78, -1.59, 1.15}, {0.68, 0.73, 0.74}, cabinet)
    box('cabecera', {0.54, 0.01, 0.13}, {2.78, -1.604, 1.49}, colors.steel, cabinet)
    label('rotulo_panel', 'CONTROL 01', 0.055, {2.78, -1.615, 1.47}, cabinet)
    local switch = revolute('seccionador', {2.65, -1.63, 1.28}, cabinet, false, math.pi / 2)
    sim.setObjectOrientation(switch, {math.pi / 2, 0, 0})
    box('base_seccionador', {0.15, 0.018, 0.16}, {2.65, -1.61, 1.28}, colors.yellow, cabinet)
    box('maneta', {0.035, 0.065, 0.14}, {2.65, -1.65, 1.28}, colors.red, switch)
    local emergency = cylinder('parada_emergencia', {0.12, 0.12, 0.06}, {2.94, -1.65, 1.29}, colors.red, cabinet)
    sim.setObjectOrientation(emergency, {math.pi / 2, 0, 0})
    for i, item in ipairs({{'start', colors.green}, {'reset', colors.blue}, {'stop', colors.red}}) do
        local x = 2.60 + (i - 1) * 0.18
        local button = cylinder(item[1], {0.06, 0.06, 0.035}, {x, -1.63, 1.12}, item[2], cabinet)
        sim.setObjectOrientation(button, {math.pi / 2, 0, 0})
        label('rotulo_' .. item[1], string.upper(item[1]), 0.025, {x, -1.62, 1.055}, cabinet)
    end
    padlock('bloqueo_1', 2.64, colors.blue, cabinet)
    padlock('bloqueo_2', 2.90, colors.orange, cabinet)
    label('rotulo_loto', 'LOTO', 0.05, {2.78, -1.62, 0.81}, cabinet)
    local light = group('baliza', {2.78, -1.45, 1.65}, cabinet)
    for i, color in ipairs({colors.green, colors.yellow, colors.red}) do
        cylinder('lente_' .. i, {0.09, 0.09, 0.07}, {2.78, -1.45, 1.65 + i * 0.075}, color, light)
    end
    box('contacto_potencia', {0.11, 0.07, 0.14}, {3.12, -1.45, 1.18}, colors.silver, cabinet)
    local reader = box('lector_rfid', {0.16, 0.12, 0.22}, {0.70, -1.60, 1.10}, colors.blue)
    box('pantalla', {0.12, 0.015, 0.10}, {0.70, -1.67, 1.13}, colors.belt, reader)
    label('rotulo_rfid', 'RFID', 0.03, {0.70, -1.68, 1.045}, reader)
end

local function proximity(name, kind, floats, position, orientation)
    -- Sensors are evaluated explicitly against workers by future scene logic.
    local sensor = sim.createProximitySensor(kind, 16, 5, {16, 16, 1, 1, 0, 0, 0, 0}, floats)
    place(sensor, name, position)
    sim.setObjectOrientation(sensor, orientation)
    return sensor
end

local function sensors()
    proximity('sensor_presencia', sim.proximitysensor_pyramid,
        {0, 2.40, 4.40, 3.00, 4.40, 3.00, 0, 0, 0, 0, 0, 0, 0.02, 0, 0},
        {0, 0, 2.46}, {math.pi, 0, 0})
    proximity('sensor_barrera', sim.proximitysensor_ray,
        {0, 1.10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.02, 0, 0},
        {-0.55, -1.65, 1.10}, {0, math.pi / 2, 0})
    for i, x in ipairs({-0.55, 0.55}) do
        local name = i == 1 and 'emisor_barrera' or 'receptor_barrera'
        local housing = box(name, {0.075, 0.10, 0.24}, {x, -1.65, 1.10}, colors.steel)
        ball('lente', {0.025, 0.045, 0.045}, {x + (i == 1 and 0.045 or -0.045), -1.65, 1.10}, colors.red, housing)
    end
    local mast = group('soporte_sensor', {0, 0, 0})
    rod('mastil', {0, 1.50, 0.10}, {0, 1.50, 2.46}, 0.045, colors.steel, mast)
    rod('brazo', {0, 1.50, 2.46}, {0, 0, 2.46}, 0.035, colors.steel, mast)
    box('carcasa_sensor', {0.18, 0.14, 0.06}, {0, 0, 2.49}, colors.blue, mast)
end

local function frameCamera()
    local camera = sim.getObject('/DefaultCamera', {noError = true})
    if camera == -1 then
        return
    end
    local eye = {6.3, -9.0, 6.6}
    local target = {0.30, -0.30, 0.90}
    local forward = {target[1] - eye[1], target[2] - eye[2], target[3] - eye[3]}
    local length = math.sqrt(forward[1]^2 + forward[2]^2 + forward[3]^2)
    for i = 1, 3 do
        forward[i] = forward[i] / length
    end
    local horizontal = math.sqrt(forward[1]^2 + forward[2]^2)
    local x = {-forward[2] / horizontal, forward[1] / horizontal, 0}
    local y = {
        -forward[3] * x[2],
        forward[3] * x[1],
        forward[1] * x[2] - forward[2] * x[1],
    }
    sim.setObjectMatrix(camera, {
        x[1], y[1], forward[1], eye[1],
        x[2], y[2], forward[2], eye[2],
        x[3], y[3], forward[3], eye[3],
    })
    sim.setObjectFloatParam(camera, sim.camerafloatparam_perspective_angle, math.rad(44))
end

local function build()
    root = sim.createDummy(0.005)
    created[#created + 1] = root
    sim.setObjectAlias(root, 'mina')
    sim.setModelProperty(root, 0)
    floor()
    conveyor()
    perimeter()
    worker(1, -1.05, -2.12, colors.orange)
    worker(2, 1.20, -2.12, colors.yellow)
    panel()
    sensors()
    frameCamera()
    sim.writeCustomTableData(root, 'configuracion', {
        version = 2,
        estado = 'modelo_geometrico',
        zona = {xmin = -2.20, xmax = 2.20, ymin = -1.50, ymax = 1.50},
        operarios = {1, 2},
        unidades = 'm',
    })
    sim.setObjectSel({})
    sim.addLog(sim.verbosity_scriptinfos, 'Modelo creado. Guarda como simulacion/mina_modelada.ttt.')
    return root
end

local ok, result = xpcall(build, debug.traceback)
if not ok then
    for i = #created, 1, -1 do
        pcall(sim.removeObjects, {created[i]})
    end
    error(result)
end
return result
