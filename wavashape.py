import math
from func import *

half_pi = math.pi/2

def isc_t2(v, t):
    if abs(v) < t: return v
    znk = znak(v)
    v = max(abs(v) - t, 0)
    return v * znk / (1 - t)

def isc_c(v, t):
    return max(abs(v), t)*znak(v)

def isc2_c(v, t):
    if abs(v) < t: return -t*znak(v)
    return v

def isc_b(v, t):
    if abs(v) < t:
        return (t-abs(v))*znak(v)
    return v

def isc2_b(v, t):
    if abs(v) < t:
        return (t+abs(v))*-znak(v)
    return v

def isc(v, t):
    znk = znak(v)
    v = max(abs(v)-t, 0)
    return v*znk/(1-t)

def isc2(v, t):
    znk = znak(v)
    v = abs(v)-t
    return v*znk

def crash(v, t):
    if abs(v) < t/5:
        return 0
    return max(abs(v), t) * znak(v)

def comp(v, t, r):
    znk = znak(v)

    v = abs(v)

    v_base = min(v, t)
    v_over = max(v - v_base, 0.0) / r

    return (min(v_base, v) + v_over) * znk

def znak(v):
    if v > 0: return 1
    if v < 0: return -1
    return 0

def overDrave(v, b, r=2):
    znk = znak(v)

    v = abs(v)
    if v == 0 or b == 0:
        return 0
    return math.pow(v*r, 1/b)/math.pow(r, 1/b)*znk

def tanh(v):
    return math.tanh(v)


def verticBitCrsh(v, n):
    return round(v*n)/n

def verticBitCrsh2(v, n):
    return int(v*n)/n

def verticBitCrsh3(v, n):
    return (int(((v/2+0.5) * ((n+1)/n)) * n) / n) * 2 -1

def waveshaper1_sin(v, n):
    return math.sin(v * n * half_pi)

def waveshaper1b_sin(v, n):
    return math.sin(v * n * half_pi)/2 + v/2

def waveshaper2_tan(v, n):
    return math.tan(1.45*n*v)/8.5*n

def waveshaper3_abs(v, n):
    return abs(abs(n*v*2)-2)-1

def waveshaper3b_abs_pow(v, n, power:int=3):
    znk = znak(v)
    return math.pow(abs((abs(abs(2*v*n)-2))-1), power) * znk

def waveshaper4_cos_in_sin(v, n, nmod=2):
    return math.sin(n*math.cos(nmod*n*v))

def waveshaper5_sin_plus_sin(v, n, nmod):
    return (math.sin(v*n)+math.sin(v*n*nmod))/2

def waveshaper6_sin_func_sin(v, n, nmod):
    return maxAbs(math.sin(v*n*half_pi), math.sin(v*n*nmod*half_pi))

def waveshaper6b(v, n, nmod):
    return _max(math.sin(v*n*half_pi), math.sin(v*n*nmod*half_pi))

def waveshaper6c(v, n, nmod):
    return minAbs(math.sin(v*n*half_pi), math.sin(v*n*nmod*half_pi))

def waveshaper6d(v, n, nmod):
    return minMid(math.sin(v*n*half_pi), math.sin(v*n*nmod*half_pi))

def waveshaper7_log(v, n=2, base=2):
    znk = znak(v)
    return math.log(abs(v*n)+1, base)/math.log(n+1, base) * znk

def waveshaper7b_gamma(v, n=1):
    return math.gamma(v)

def waveshaper8_softsign(v, n):
    return (v*n / (1+abs(v*n))) / (n / (1+abs(n)))

def waveshaper9_clone_wave(v, n=2):
    return ((v*n/2)%1)*2-1

def waveshaper9__to_wave_fx(v_fx, v_org):
    return v_fx * 0.5 + znak(v_org)*0.5

def waveshaper9_to_wave_fx(v_fx, v_org, n=2):
    return (int((v_org/2+0.5) * n) / n * 2-1) + (1/n) + (v_fx / n)



def waveshaper8b_arctg(v, n):
    return math.asin(v*n/math.sqrt(1+pow(v*n,2))) / math.asin(n/math.sqrt(1+pow(n,2)))


def frac(v, n):
    znk = znak(v)

    return ((n*abs(v))%1) * znk

def frac2(v, n=1):
    v *= n

    if v > 1:
        if (v-1)%4 > 2:
            #return 1
            return ((v+1)%2)-1
            #print("1a", v, v-(int(v+1/2)))
        else:
            #return 1
            return 1-((v-1)%2)
            #print("1b", v, 1-(v-1)%2)
    if v < -1:
        if (v+1)%4 < 2:
            #return -1
            return ((v+1)%2)-1
            #print("2a", v, int(v+1/2)*2-1 + v)
        else:
            #return -1
            return 1-((v-1)%2)
            #print("2b", v, ((v-1)%2)+1)
    return v