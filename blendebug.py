import bpy
import random

# CHANGE THINGS HERE
LOGFILE = '/tmp/pbrt.INFO'
SETTINGS = {
    'MAX_OBJS': 100,
    'LIMIT_POINTS': True,
    'LIMIT_LINES': True,
    'LIMIT_DIRECTIONS': True,
    'DIRECTION_LENGTH': 0.5
}

STATE = {'N_OBJS': 0}

def pointHandler(params):
    global STATE
    global SETTINGS

    if SETTINGS['LIMIT_POINTS'] and STATE['N_OBJS'] <= SETTINGS['MAX_OBJS']:
        return

    try:
        nums = params[0][1:-2]
        x, y, z = nums.split(',')
        x = float(x)
        y = float(y)
        z = float(z)

        # if there is a second arg, use as name
        try:
            name = str(params[2])
        except IndexError:
            name = 'l'

        verts = [(x, y, z)]
        edges = []
        faces = []

        # create mesh
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, edges, faces)
        mesh.validate()
        mesh.update()

        # create obj
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)

        STATE['N_OBJS'] += 1

    except:
        print(f'failed to plot point: {params}')

def lineHandler(params):
    global STATE
    global SETTINGS

    if SETTINGS['LIMIT_LINES'] and STATE['N_OBJS'] <= SETTINGS['MAX_OBJS']:
        return

    try:
        # parse first point
        p0 = params[0][1:-2]
        x0, y0, z0 = p0.split(',')
        x0 = float(x0)
        y0 = float(y0)
        z0 = float(z0)

        # parse second point
        p1 = params[1][1:-2]
        x1, y1, z1 = p1.split(',')
        x1 = float(x1)
        y1 = float(y1)
        z1 = float(z1)

        # if there is a second arg, use as name
        try:
            name = str(params[2])
        except IndexError:
            name = 'l'

        verts = [(x0, y0, z0), (x1, y1, z1)]
        edges = [(0, 1)]
        faces = []

        # create mesh
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, edges, faces)
        mesh.validate()
        mesh.update()

        # create object
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)

        STATE['N_OBJS'] += 1

    except:
        print(f'failed to plot line: {params}')

def directionHandler(params):
    global STATE
    global SETTINGS

    if SETTINGS['LIMIT_DIRECTIONS'] and STATE['N_OBJS'] >= SETTINGS['MAX_OBJS']:
        return

    try:
        # parse origin
        origin = params[0][1:-2]
        og_x, og_y, og_z = origin.split(',')
        og_x = float(og_x)
        og_y = float(og_y)
        og_z = float(og_z)

        # parse direction
        direction = params[1][1:-2]
        d_x, d_y, d_z = direction.split(',')
        d_x = float(d_x)
        d_y = float(d_y)
        d_z = float(d_z)

        # if third arg, name
        try:
            name = str(params[2])
        except IndexError:
            name = 'dir'

        length = SETTINGS['DIRECTION_LENGTH']
        arrowLen = length / 10

        direction_orth = (-d_y * arrowLen, -d_x * arrowLen, 0)

        origin = (og_x, og_y, og_z)
        endpoint = (og_x + length * d_x, og_y + length * d_y, og_z + length * d_z)
        arrow_l = (endpoint[0] - arrowLen * d_x + direction_orth[0], endpoint[1] - arrowLen * d_y + direction_orth[1],
                   endpoint[2] - arrowLen * d_z + direction_orth[2])
        arrow_r = (endpoint[0] - arrowLen * d_x - direction_orth[0], endpoint[1] - arrowLen * d_y - direction_orth[1],
                   endpoint[2] - arrowLen * d_z - direction_orth[2])

        verts = [origin, endpoint, arrow_l, arrow_r]
        edges = [(0, 1), (1, 2), (1, 3)]
        faces = []

        # create mesh
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, edges, faces)
        mesh.validate()
        mesh.update()

        # create object
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)

        STATE['N_OBJS'] += 1

    except:
        print(f'failed to plot line: {params}')

HANDLERS = {'POINT': pointHandler,
            'LINE': lineHandler,
            'DIR': directionHandler}

if __name__ == '__main__':

    # place all objects in the DEBBUG collection
    collection = bpy.data.collections.get('DEBUG')

    # if DEBUG collection doesnt exist, make one
    if not collection:
        collection = bpy.data.collections.new('DEBUG')
        bpy.context.scene.collection.children.link(collection)

    # clear the collection
    bpy.ops.object.select_all(action='DESELECT')
    for object in collection.objects[:]:
        object.select_set(True)
    bpy.ops.object.delete()

    # place all objects in debug file
    lines = open(LOGFILE).readlines()

    # get the debug-lines    
    debuglines = []
    for line in lines:
        if 'DBG' in line:
            _, data = line.split('DBG ')
            debuglines.append(data)

    random.shuffle(debuglines)

    # plot each structure
    for line in debuglines:
        ty, params = line.split(':')
        params = params.split(';')

        HANDLERS[ty](params)
