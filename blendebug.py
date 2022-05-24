import bpy
import random
import numpy as np

# CHANGE THINGS HERE
LOGFILE = '/tmp/pbrt.INFO'

SETTINGS = {
    'MAX_OBJS': 100,
    'DIRECTION_LENGTH': 0.5,
    'COLLECTION': 'DEBUG',
}

COLORS = {
    'BLACK': (0, 0, 0, 0),
    'WHITE': (1, 1, 1, 1),
    'RED': (1, 0, 0, 1),
    'GREEN': (0, 1, 0, 1),
    'BLUE': (0, 0, 1, 1),
}

# utilities
def parse_point(point_str: str) -> np.ndarray:
    """
    Parse a 3D point in the format "[x, y, z]" to a numpy vector
    :param point_str: point in string format
    :return:
    """
    x, y, z = point_str[1:-2].split(',')
    x = float(x)
    y = float(y)
    z = float(z)
    return np.array([x, y, z])

def to_vertex(arr: np.ndarray):
    """
    Convert a numpy array to blender vertex data
    :param arr: numpy array representing 3d point
    :return: same point as a blender vertex
    """
    x, y, z = arr
    return x, y, z

def create_object(verts, edges, faces, name, color):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.validate()
    mesh.update()

    # create obj
    obj = bpy.data.objects.new(name, mesh)
    obj.color = COLORS[color]
    bpy.data.collections[SETTINGS['COLLECTION']].objects.link(obj)

# handlers
def point_handler(params, color):
    p = parse_point(params[0])

    # if there is a second arg, use as name
    try:
        name = str(params[2])
    except IndexError:
        name = 'l'

    verts = [p]
    edges = []
    faces = []

    create_object(verts, edges, faces, name, color)

def line_handler(params, color):
    # parse first point
    p0 = parse_point(params[0])
    p1 = parse_point(params[1])

    # if there is a second arg, use as name
    try:
        name = str(params[2])
    except IndexError:
        name = 'l'

    verts = [to_vertex(p0), to_vertex(p1)]
    edges = [(0, 1)]
    faces = []

    create_object(verts, edges, faces, name, color)

def tri_handler(params, color):
    # parse first point
    p0 = parse_point(params[0])
    p1 = parse_point(params[1])
    p2 = parse_point(params[2])

    # if there is an additional arg, use as name
    try:
        name = str(params[3])
    except IndexError:
        name = 'l'

    verts = [to_vertex(p0), to_vertex(p1), to_vertex(p2)]
    edges = [(0, 1), (0, 2), (1, 2)]
    faces = []

    create_object(verts, edges, faces, name, color)

def tetra_handler(params, color):
    # parse first point
    p0 = parse_point(params[0])
    p1 = parse_point(params[1])
    p2 = parse_point(params[2])
    p3 = parse_point(params[3])

    # if there is an additional arg, use as name
    try:
        name = str(params[4])
    except IndexError:
        name = 'l'

    verts = [to_vertex(p0), to_vertex(p1), to_vertex(p2), to_vertex(p3)]
    edges = [(0, 1), (0, 2), (1, 2), (3, 0), (3, 1), (3, 2)]
    faces = []

    create_object(verts, edges, faces, name, color)

def direction_handler(params, color):
    origin = parse_point(params[0])
    direction = parse_point(params[1])

    # if third arg, name
    try:
        name = str(params[2])
    except IndexError:
        name = 'dir'

    length = SETTINGS['DIRECTION_LENGTH']
    arrowLen = length / 10

    endpoint = origin + length * direction

    # vector orthogonal to direction (for arrow heads)
    direction_orth = np.array([-direction[1] * arrowLen, -direction[0] * arrowLen, 0])
    arrow_l = endpoint - arrowLen * direction + direction_orth
    arrow_r = endpoint - arrowLen * direction - direction_orth

    verts = [to_vertex(origin), to_vertex(endpoint), to_vertex(arrow_l), to_vertex(arrow_r)]
    edges = [(0, 1), (1, 2), (1, 3)]
    faces = []

    create_object(verts, edges, faces, name, color)

def poly_handler(params, color):

    # get the first n vertices that are a point
    i = 0
    verts = []
    for i, param in enumerate(params):
        try:
            verts.append(to_vertex(parse_point(param)))
        except ValueError:
            break

    # if next arg, name
    try:
        name = str(params[i])
    except IndexError:
        name = 'dir'

    # connect vertices
    edges = []
    for i, _ in enumerate(verts[:-1]):
        edges.append((i, i+1))
    edges.append((0, len(verts) - 1))

    faces = []

    create_object(verts, edges, faces, name, color)

HANDLERS = {'POINT': point_handler,
            'LINE': line_handler,
            'DIR': direction_handler,
            'TRI': tri_handler,
            'POLY': poly_handler,
            'TETRA': tetra_handler}

def parse_trace(trace: str):
    pre, params = trace.split(':')

    try:
        ty, color = pre.split('-')
    except ValueError:
        ty = pre
        color = 'BLACK'

    params = params.split(';')
    return ty, color, params

def place_traces(collection_name: str):
    # if DEBUG collection doesnt exist, make one
    if not bpy.data.collections.get(collection_name):
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    # clear objects in DEBUG collection
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.collections[collection_name].objects[:]:
        obj.select_set(True)
    bpy.ops.object.delete()

    # filter log file for traces only
    traces = []
    for line in open(LOGFILE):
        if 'DBG' in line:
            _, data = line.split('DBG ')
            traces.append(data)

    # shuffle and truncate traces (to only display a subset)
    random.shuffle(traces)
    traces = traces[0:SETTINGS['MAX_OBJS']]

    # plot the traces
    for trace in traces:

        ty, color, params = parse_trace(trace)

        # plot the trace
        HANDLERS[ty](params, color)

if __name__ == '__main__':
    place_traces(SETTINGS['COLLECTION'])
