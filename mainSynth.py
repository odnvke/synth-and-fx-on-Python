import math
from bezier import cubic_bezier, quadratic_bezier

def fx(r, l="none"):
    _, r = cubic_bezier(r/2+0.5, c1x=-1, c1y=6, c2x=1, c2y=-6)
    _, l = cubic_bezier(l/2+0.5, c1x=-1, c1y=6, c2x=1, c2y=-6)

    return (r, l)