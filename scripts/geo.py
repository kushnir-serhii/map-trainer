"""Small geometry helpers shared by the build scripts (no third-party packages)."""
import math


def rings_of(geom):
    """List of polygons, each a list of rings (first = outer), for Polygon / MultiPolygon."""
    if geom['type'] == 'Polygon':
        return [geom['coordinates']]
    return list(geom['coordinates'])


def area(r):
    """Signed area of a ring of (x, y) points."""
    return sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1)) / 2


def simplify(pts, tol):
    """Douglas-Peucker; keeps the first and last point."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1e-12
        best, idx = -1, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / L if (dx or dy) else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, i
        if best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def ring_path(r, nd=1):
    f = f'{{:.{nd}f}}'
    return 'M' + 'L'.join(f.format(x) + ',' + f.format(y) for x, y in r[:-1]) + 'Z'


def inside(p, ring):
    x, y = p
    c = False
    for i in range(len(ring) - 1):
        (x0, y0), (x1, y1) = ring[i], ring[i + 1]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = 0 if not (dx or dy) else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def label_point(ring, avoid=(), avoid_w=0.6, step=None):
    """A point well inside `ring` (largest distance to the border), pushed away from `avoid` points
    (city dots) so the label does not sit on them. Grid search, good enough for ~1000-unit maps."""
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    step = step or max(x1 - x0, y1 - y0) / 40
    best, bp = -1, None
    y = y0 + step / 2
    while y < y1:
        x = x0 + step / 2
        while x < x1:
            if inside((x, y), ring):
                d = min(seg_dist((x, y), ring[i], ring[i + 1]) for i in range(len(ring) - 1))
                for ax, ay in avoid:
                    d = min(d, math.hypot(x - ax, y - ay) * avoid_w)
                if d > best:
                    best, bp = d, (x, y)
            x += step
        y += step
    if bp is None:  # degenerate ring: fall back to the vertex average
        bp = (sum(xs) / len(xs), sum(ys) / len(ys))
    return bp
