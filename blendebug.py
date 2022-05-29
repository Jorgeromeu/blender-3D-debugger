import bpy
import random
import numpy as np

# CHANGE THINGS HERE
LOGFILE = '/tmp/pbrt.INFO'

SETTINGS = {
    'MAX_OBJS': 10,
    'DIRECTION_LENGTH': 0.5,
    'COLLECTION': 'DEBUG',
}

COLORS = {
    'BLACK': (0, 0, 0, 0),
    'WHITE': (1, 1, 1, 1),
    'RED': (1, 0, 0, 1),
    'GREEN': (0, 1, 0, 1),
    'BLUE': (0, 0, 1, 1),
    'CYAN': (0.1, 1, 1, 1)
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

def create_object(verts, edges, faces, name, color, collection):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.validate()
    mesh.update()

    # create obj
    obj = bpy.data.objects.new(name, mesh)
    obj.color = COLORS[color]
    collection.objects.link(obj)

# handlers
def point_handler(params, color, collection):
    p = parse_point(params[0])

    # if there is a second arg, use as name
    try:
        name = str(params[2])
    except IndexError:
        name = 'l'

    verts = [p]
    edges = []
    faces = []

    create_object(verts, edges, faces, name, color, collection)

def line_handler(params, color, collection):
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

    create_object(verts, edges, faces, name, color, collection)

def tri_handler(params, color, collection):
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

    create_object(verts, edges, faces, name, color, collection)

def tetra_handler(params, color, collection):
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

    create_object(verts, edges, faces, name, color, collection)

def direction_handler(params, color, collection):
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

    create_object(verts, edges, faces, name, color, collection)

def aabb_handler(params, color, collection):
    lo = parse_point(params[0])
    hi = parse_point(params[1])

    # if third arg, name
    try:
        name = str(params[2])
    except IndexError:
        name = 'aabb'

    hip = hi + np.array([0, 0, 0.1])
    lop = lo - np.array([0, 0, 0.1])

    verts = [to_vertex(lo), (lo[0], lo[1], hi[2]), (lo[0], hi[1], lo[2]), (hi[0], lo[1], lo[2]),
             to_vertex(hi), (hi[0], hi[1], lo[2]), (hi[0], lo[1], hi[2]), (lo[0], hi[1], hi[2]),
             to_vertex(lop), to_vertex(hip)]
    edges = [(0, 1), (0, 2), (0, 3),
             (4, 5), (4, 6), (4, 7),
             (1, 7), (1, 6), (5, 3), (5, 2),
             (6, 3), (7, 2),
             # hilo-markers
             (0, 8), (4, 9)]
    faces = [

    ]

    create_object(verts, edges, faces, name, color, collection)

HANDLERS = {'POINT': point_handler,
            'LINE': line_handler,
            'DIR': direction_handler,
            'TRI': tri_handler,
            'TETRA': tetra_handler,
            'AABB': aabb_handler}

def parse_trace(trace: str):
    pre, params = trace.split(':')

    try:
        ty, color = pre.split('-')
    except ValueError:
        ty = pre
        color = 'WHITE'

    params = params.split(';')
    return ty, color, params

def setup_collection(collection_name: str):
    """
    If a collection already exists clear it, else create it

    :param collection_name: name of collection
    :return: reference to collection
    """

    # if collection doesnt exist, make one
    if not bpy.data.collections.get(collection_name):
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    # clear objects in collection
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.collections[collection_name].objects[:]:
        obj.select_set(True)
    bpy.ops.object.delete()

    return bpy.data.collections[collection_name]

def place_traces(traces, collection):
    # plot the traces
    for trace in traces:
        ty, color, params = parse_trace(trace)

        # plot the trace
        HANDLERS[ty](params, color)

def read_logfile(path):
    # filter log file for traces only
    traces = []
    for line in open(path):
        if 'DBG' in line:
            _, data = line.split('DBG ')
            traces.append(data)

    # shuffle and truncate traces (to only display a subset)
    random.shuffle(traces)
    traces = traces[0:SETTINGS['MAX_OBJS']]
    return traces

if __name__ == '__main__':

    # change to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # create collection
    collection = setup_collection(SETTINGS['COLLECTION'])

    # foo(collection)

    traces = read_logfile(LOGFILE)

    # plot the traces
    for trace in traces:
        ty, color, params = parse_trace(trace)

        # plot the trace
        HANDLERS[ty](params, color, collection)
