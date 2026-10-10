"""Derived 20 mm curb component; CPU geometry only, no simulator imports."""
import numpy as np

HEIGHT_M = .020
STRIP_WIDTH_M = .150
TILE_SIZE_M = 9.
EDGE_X_M = -STRIP_WIDTH_M / 2


def mesh():
    # The strip joins an upper platform at the same height. This is one curb,
    # not a narrow raised box with a second descending edge or a stair flight.
    x0, x1 = -TILE_SIZE_M / 2, TILE_SIZE_M / 2
    y0, y1 = x0, x1
    v = np.array([
        [x0, y0, 0], [EDGE_X_M, y0, 0],
        [EDGE_X_M, y1, 0], [x0, y1, 0],
        [EDGE_X_M, y0, HEIGHT_M], [EDGE_X_M, y1, HEIGHT_M],
        [STRIP_WIDTH_M / 2, y0, HEIGHT_M],
        [STRIP_WIDTH_M / 2, y1, HEIGHT_M],
        [x1, y0, HEIGHT_M], [x1, y1, HEIGHT_M],
    ], dtype=np.float64)
    f = np.array([
        [0, 1, 2], [0, 2, 3],       # lower support
        [4, 6, 7], [4, 7, 5],       # 150 mm upper strip
        [6, 8, 9], [6, 9, 7],       # continuous upper platform
        [1, 4, 5], [1, 5, 2],       # unsmoothed vertical riser
    ], dtype=np.int64)
    return v, f


def height(x, y):
    x, y = np.broadcast_arrays(np.asarray(x), np.asarray(y))
    inside = (np.abs(x) <= TILE_SIZE_M / 2) & (np.abs(y) <= TILE_SIZE_M / 2)
    return np.where(inside, np.where(x < EDGE_X_M, 0., HEIGHT_M), np.nan)


def mirrored_mesh():
    v, f = mesh()
    v[:, 0] *= -1
    return v, f[:, ::-1]
