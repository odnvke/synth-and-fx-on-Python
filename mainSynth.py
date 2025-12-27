import math
from bezier import cubic_bezier, quadratic_bezier
from func import *
from waveshape import *
from bitCrasher import BitCrusher

bitL = BitCrusher(rate=(1/44100)*6.5, mode=1, randomness=100)
bitR = BitCrusher(rate=(1/44100)*6.5, mode=1)

def fx(r, l="none"):
    r = bitR.tick(tanh(r*2))
    l = bitL.tick(tanh(l*2))
    return (limit(r), limit(l))