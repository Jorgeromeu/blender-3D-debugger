# 3D-debugger
A simple, extensible blender script for debugging 3D related code such as ray tracers, specifically designed for working with the [`pbrt`](https://pbr-book.org/) renderer but can theoretically be used with any renderer.

# Examples

Visualizing directions of camera rays in an example scene:

![window](https://user-images.githubusercontent.com/40536127/169659841-7c5cc815-8d9b-41e0-8ca3-6e872be2fc45.png)

# Usage

To use the script, you first need to produce a traces file containing all of the shapes you want to visualize. The simplest way to do this is to write this data to the log file of your renderer. For example, with the `pbrt` renderer, you can just do:

## Visualizing points

```cpp
// p is a Point3f or Vector3f
LOG(INFO) << "DBG POINT:" << p;

// optionally pass a name
LOG(INFO) << "DBG POINT:" << p << ";" << "pointName";
```
## Visualizing lines

```cpp
// a is the start point, b is the end point
LOG(INFO) << "DBG LINE:" << a << ";" << b;

// optionally pass a name
LOG(INFO) << "DBG LINE:" << a << ";" << b << ";" << "lineName";
```

## Visualizing directions

```cpp
// p is the start point, d is a (normalized) direction
LOG(INFO) << "DBG DIR:" << p << ";" << d;

// optionally pass a name
LOG(INFO) << "DBG DIR:" << p << ";" << d << ";" <<"directionName;
```

# Loading the traces file into blender

In blender, switch to the scripting tab, or open a text editor area and open [`blendebug.py`](https://github.com/Jorgeromeu/3D-debugger/blob/master/blendebug.py). Then set `LOGFILE` to be the absolute path to your traces file.

Now simply run the script and the debug traces will be created and placed in the `DEBUG` collection so you can conveniently hide or select all of the debug traces.

![image](https://user-images.githubusercontent.com/40536127/169660396-4953a428-c411-4e7d-99df-0e9e3f368e4e.png)

## Things to watch out for:

> If you re-run the renderer, and re-run the script in blender, the existing traces will be deleted first, so there is no need to do this manually.

> Often times traces you are debugging dont all need to be placed (for instance if you are visualizing sampled points on a light source). In such cases, you can set the `MAX_OBJS` field in `SETTINGS` and then set `LIMIT_POINTS` so that the amount of points is bounded. Then it will only place a random subset of the points you provided. This way you dont need to change resolution or spp settings and can instead work with the entire dataset.

# TODO:
- Support colors
- UI within blender

