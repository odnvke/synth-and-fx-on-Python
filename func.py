def znak(v):
    """return a sign of value"""
    if v > 0: return 1
    if v < 0: return -1
    return 0

def limit(t):
    return max(min(t, 1), -1)

def conv(v):
    """0-1  to  -1 - 1"""
    return abs(v)*2-1

def conv2(v):
    """-1 - 1  to  0-1"""
    return v/2+0.5

def maxAbs(v, v2):
    if abs(v) > abs(v2): return v
    return v2

def _max(v, v2):
    if v > v2: return v
    return -v2

def minAbs2(v, v2):
    return (1-min(abs(v), abs(v2)))*znak(min(v, v2))

def maxMid(v, v2):
    if abs(abs(v) - 0.5) < abs(abs(v2) - 0.5): return v
    return v2

def minMid(v, v2):
    if abs(abs(v) - 0.5) > abs(abs(v2) - 0.5): return v
    return v2

def minAbs(v, v2):
    if abs(v) < abs(v2): return v
    return v2

