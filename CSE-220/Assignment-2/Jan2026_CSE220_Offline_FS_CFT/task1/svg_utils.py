"""
svg_utils.py  -- PROVIDED CODE. You do not need to read or modify this file.

Turns a simple single-path SVG drawing into a discrete, uniformly-sampled,
complex-valued periodic "signal"

    z(t) = x(t) + 1j * y(t),   t in [0, 2*pi)

that you can feed straight into your FourierEpicycles class. Only the SVG
path commands M (moveto), L (lineto), C (cubic Bezier) and Z (closepath),
with absolute coordinates, are supported -- this covers every drawing that
ships with this assignment.
"""
import re
import numpy as np

_PATH_RE = re.compile(r'<path[^>]*\sd="([^"]+)"')
_TOKEN_RE = re.compile(r'[MLCZ]|-?\d+(?:\.\d+)?(?:e-?\d+)?')
_NUMS_NEEDED = {'M': 2, 'L': 2, 'C': 6, 'Z': 0}


def _read_path_d(filename):
    with open(filename, 'r') as f:
        content = f.read()
    match = _PATH_RE.search(content)
    if not match:
        raise ValueError(f"No <path d=\"...\"> element found in {filename}")
    return match.group(1)


def _parse_commands(d):
    tokens = _TOKEN_RE.findall(d)
    commands = []
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd not in _NUMS_NEEDED:
            raise ValueError(f"Unsupported/unexpected token '{cmd}' in path data")
        i += 1
        n = _NUMS_NEEDED[cmd]
        nums = [float(x) for x in tokens[i:i + n]]
        i += n
        commands.append((cmd, nums))
    return commands


def _cubic_bezier(p0, p1, p2, p3, num):
    t = np.linspace(0.0, 1.0, num, endpoint=False).reshape(-1, 1)
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 \
        + 3 * (1 - t) * (t ** 2) * p2 + (t ** 3) * p3


def _path_to_polyline(d, line_samples=20, curve_samples=400):
    # Curves need many more samples than straight lines: a coarsely
    # faceted polyline approximation of a smooth Bezier arc behaves like a
    # sequence of tiny sharp corners, which shows up as spurious
    # high-frequency ringing once enough harmonics are used to "see" them.
    commands = _parse_commands(d)
    pts = []
    current = start = None
    for cmd, nums in commands:
        if cmd == 'M':
            current = start = np.array(nums, dtype=float)
            pts.append(current)
        elif cmd == 'L':
            end = np.array(nums, dtype=float)
            seg = np.linspace(current, end, line_samples, endpoint=False)
            pts.extend(seg)
            current = end
        elif cmd == 'C':
            p1 = np.array(nums[0:2]); p2 = np.array(nums[2:4]); p3 = np.array(nums[4:6])
            seg = _cubic_bezier(current, p1, p2, p3, curve_samples)
            pts.extend(seg)
            current = p3
        elif cmd == 'Z':
            seg = np.linspace(current, start, line_samples, endpoint=False)
            pts.extend(seg)
            current = start
    return np.array(pts)


def load_svg_path(filename, num_points=1000):
    """
    Load an SVG file and return (t, z):
      t : shape (num_points,) float array, uniformly spaced samples over the
          *closed* interval [0, 2*pi] (t[0] == 0, t[-1] == 2*pi)
      z : shape (num_points,) complex array, z[i] = x(t[i]) + 1j*y(t[i]),
          with z[-1] == z[0] since the drawing is periodic.

    Using a closed interval (both endpoints included, with the signal
    wrapping exactly) means a plain call to np.trapezoid(signal * kernel, t)
    integrates correctly over one full period -- exactly like integrating
    over the closed interval [-L, L] last year. There is no need to worry
    about "wraparound" corrections.

    The drawing is centered at the origin, scaled to roughly fit in
    [-1, 1] x [-1, 1], and re-parametrized to *equal arc length* so that it
    is traced out at constant speed (important for a clean epicycle
    animation). The SVG y-axis (which points downward) is flipped so the
    shape looks right-side-up in a normal matplotlib plot.
    """
    d = _read_path_d(filename)
    poly = _path_to_polyline(d)
    poly = poly - poly.mean(axis=0)
    scale = np.max(np.abs(poly))
    poly = poly / scale
    x, y = poly[:, 0], -poly[:, 1]

    seg_len = np.hypot(np.diff(x, append=x[0]), np.diff(y, append=y[0]))
    arc = np.concatenate(([0.0], np.cumsum(seg_len)))
    total_len = arc[-1]

    t = np.linspace(0, 2 * np.pi, num_points, endpoint=True)
    target_arc = t / (2 * np.pi) * total_len

    x_closed = np.append(x, x[0])
    y_closed = np.append(y, y[0])
    x_r = np.interp(target_arc, arc, x_closed)
    y_r = np.interp(target_arc, arc, y_closed)

    z = x_r + 1j * y_r
    z[-1] = z[0]
    return t, z
