import math
import random
import numpy as np
from note import *
import numpy.random
from numpy.random import sample

sample_rate = 44100
delta = 1/sample_rate
half_pi = math.pi/2


class osc:
    wave_form = np.array((0, 0, 0, 0, 0))
    wave_phase = np.array((0, 0, 0, 0))
    sq_pwm = 0.5
    vel = 1.0
    time = 0
    _t = 0

    rel_matrix = np.full(2, True)
    rel_loop = False
    relis = True
    relis_f = 0

    fine_tune = 0
    modul = 3

    mode = False

    def __init__(self, mode:bool=False):
        self._t = 0
        self.wave_form = np.array((0, 0, 0, 0, 0), dtype="float")
        self.wave_phase = np.array((0, 0, 0, 0), dtype="float")
        self.fine_tune = 0
        self.modul = 0.1
        self.sq_pwm = 0.5
        self.vel = 1.0
        self.mode = mode
        self.time = 0
        self.relis = True
        self.relis_f = 0
        self.rel_matrix = np.full(2, False)
        self.rel_loop = False

    def set_wave_form_sine(self, num:float=-100):
        if num == -100:
            self.wave_form = np.zeros_like(self.wave_form)
            self.wave_form[0] = 1.0
        else:
            self.wave_form[0] = num

    def set_sine_phase(self, phase:float):
        self.wave_phase[0] = phase

    def set_wave_form_triangle(self, num:float=-100):
        if num == -100:
            self.wave_form = np.zeros_like(self.wave_form)
            self.wave_form[1] = 1.0
        else:
            self.wave_form[1] = num

    def set_triangle_phase(self, phase:float):
        self.wave_phase[1] = phase

    def set_wave_form_saw(self, num:float=-100):
        if num == -100:
            self.wave_form = np.zeros_like(self.wave_form)
            self.wave_form[2] = 1.0
        else:
            self.wave_form[2] = num

    def swt_saw_phase(self, phase:float):
        self.wave_phase[3] = phase

    def set_wave_form_square(self, num:float=-100, pwm:float=0.5):
        if num == -100:
            self.wave_form = np.zeros_like(self.wave_form)
            self.wave_form[3] = 1.0
        else:
            self.wave_form[3] = num
        self.sq_pwm = pwm

    def set_square_phase(self, phase:float):
        self.wave_phase[3] = phase

    def set_wave_form_noise(self, num:float=-100):
        if num == -100:
            self.wave_form = np.zeros_like(self.wave_form)
            self.wave_form[4] = 1.0
        else:
            self.wave_form[4] = num

    def set_velosity(self, num:float=-100):
        self.vel = num

    def set_mode(self, mode:bool):
        self.mode = mode

    def set_fine_tune(self, tune:float=0):
        self.fine_tune = tune

    def set_modulation(self, mod):
        self.modul = mod

    def tick(self, note):
        global delta, half_pi



        if self.mode:
            self._t += math.tau * delta * note * (((self.fine_tune) * (self.modul)) + 1)

            if self.relis and note == 0:
                self.rel_loop = True
                self.time += math.tau * delta * self.relis_f * (((self.fine_tune) * (self.modul))+1)
            else:
                self.relis_f = note
                self.rel_loop = False
                self.time += math.tau * delta * note * (((self.fine_tune) * (self.modul))+1)
        else:
            self._t += math.tau * delta * get_note(note) * (((self.fine_tune) * (self.modul)) + 1)

            if self.relis and note == -1:
                self.rel_loop = True
                self.time += math.tau * delta * self.relis_f * (((self.fine_tune) * (self.modul)) + 1)
            else:
                self.relis_f = get_note(note)
                self.rel_loop = False
                self.time += math.tau * delta * get_note(note) * (((self.fine_tune) * (self.modul))+1)

        max_v = 0.0
        value = 0.0

        if self.wave_form[0] > 0:
            pre_value = math.sin(self.time+self.wave_phase[0]*math.tau)
            if self.rel_loop and self.rel_matrix[0]:
                pass
            elif self.rel_loop and round(pre_value, 1) == 0.0:
                self.rel_matrix[0] = True

            elif not self.rel_loop and self.rel_matrix[0]:
                self.time = 0
                self.rel_matrix[0] = False

            else:
                value += pre_value*self.wave_form[0]
                max_v += self.wave_form[0]
                self.rel_matrix[0] = False

        if self.wave_form[1] > 0:
            pre_value = (abs((self.time+(0.25+self.wave_phase[1])*math.tau) % math.tau - math.pi)/ math.pi)*-2+1
            if self.rel_loop and self.rel_matrix[1]:
                pass
            elif self.rel_loop and round(pre_value, 1) == 0.0:
                self.rel_matrix[1] = True

            elif not self.rel_loop and self.rel_matrix[1]:
                self.time = 0
                self.rel_matrix[1] = False

            else:
                value += pre_value*self.wave_form[1]
                max_v += self.wave_form[1]
                self.rel_matrix[1] = False

        if self.wave_form[2] > 0:
            value += ((((self._t+math.pi+self.wave_phase[2]*math.tau) % math.tau) - math.pi) / math.pi) * self.wave_form[2]
            max_v += self.wave_form[2]

        if self.wave_form[3] > 0:
            if ((self._t+self.wave_phase[3]*math.tau) % math.tau - math.pi) / math.pi < (self.sq_pwm)*2-1:
                value += self.wave_form[3]
            else:
                value -= self.wave_form[3]
            max_v += self.wave_form[3]

        if self.wave_form[4] > 0:
            value += ((random.random()*2)-1) * self.wave_form[4]
            max_v += self.wave_form[4]

        if max_v == 0 or value == 0:
            return 0
        return value / max_v * self.vel




class filter:
    num = 0
    mod = 0

    def __init__(self, mod=0.7):
        self.mod = mod

    def set_mod(self, mod:float):
        self.mod = mod

    def tick(self, value:float):
        v = self.num*self.mod + (value * (1-self.mod))
        self.num = v
        #print(self.num)
        return v

    def tick2(self, value):
        d = value - self.num
        if abs(d) > self.mod:
            if d > 0:
                v = self.num+self.mod
                self.num = v
                return v
            else:
                v = self.num-self.mod
                self.num = v
                return v
        else:
            self.num = value
            return value

    def tick3(self, value):
        d = value - self.num

        v = self.num+self.mod*d
        self.num = v
        return v


class bitCrusher:
    rate = 0
    v = 0
    t = 0
    rand = 0

    def __init__(self, rate:float=(1/44100)*3):
        self.rate = rate
        self.v = 0
        self.t = 0
        self.rand = 0

    def set_rate(self, rate:float=(1/44100)*3):
        self.rate = rate

    def tick(self, value:float):
        self.t += delta

        if self.t >= self.rate:
            self.t -= self.rate + random.random()*0.001*self.rand
            self.v = value

        return self.v

class bitCrusher_smooth:
    rate = 0
    p1 = 1
    p2 = 1
    t = 0
    rand = 0

    def __init__(self, rate:float=(1/44100)*3):
        self.rate = rate
        self.v = 0
        self.t = 0
        self.rand = 0
        self.p1, self.p2 = 1, 1

    def set_rate(self, rate:float=(1/44100)*3):
        self.rate = rate

    def tick2(self, value:float):
        self.t += delta

        if self.t >= self.rate:
            self.t -= self.rate + random.random()*0.001*self.rand
            self.p1 = self.p2
            self.p2 = value

        return (((self.p2-self.p1)*self.t)/self.rate - self.p1) / 1.2

    def tick(self, value:float):
        self.t += delta

        if self.t >= self.rate:
            self.t -= self.rate + random.random()*0.001*self.rand
            self.p1 = self.p2
            self.p2 = value

        return ((self.p2-self.p1)*self.t)/self.rate + self.p1

class bitCrusher2:
    data = np.array(())
    rate = 0
    v = 0
    t = 0
    rand = 0

    def __init__(self, rate:float=(1/44100)*3):
        self.rate = rate
        self.v = 0
        self.t = 0
        self.rand = 0

    def set_rate(self, rate:float=(1/44100)*3):
        self.rate = rate

    def tick(self, value:float):
        self.t += delta
        self.data = np.hstack((self.data, value))

        if self.t >= self.rate:
            self.t -= self.rate + random.random()*0.001*self.rand
            self.v = self.data.mean()
            self.data = np.array(())

        return self.v

class delay():
    buffer = np.zeros((0))
    buffer_size = 100
    t = 0
    feedback = 0.0
    feedback_value = 0.0
    dry = 0
    inp_idx = 0
    out_idx = 0

    def __init__(self, buffer_size:int=100):
        self.buffer = np.zeros((buffer_size))
        self.buffer_size = buffer_size
        self.t = 0
        self.feedback_value = 0.0
        self.feedback = 0.0
        self.dry = 0
        self.inp_idx = 0
        self.out_idx = 0

    def ones(self):
        self.buffer = np.zeros_like(self.buffer)

    def zeros(self):
        self.buffer = np.ones_like(self.buffer)

    def random(self):
        self.buffer = np.random.random(self.buffer_size)*2.0-1

    def tick(self, value:float):
        while  self.buffer_size > self.buffer.size:
            self.buffer = np.hstack((self.buffer, np.zeros(2)))

        self.inp_idx += 1
        self.inp_idx %= self.buffer_size
        self.out_idx = (self.inp_idx+1) % self.buffer_size

        output_value = self.buffer[self.out_idx]

        if self.t <= self.buffer_size:
            self.buffer[self.inp_idx] = value
        else:
            self.buffer[self.inp_idx] = value*(1-self.feedback) + self.feedback_value*self.feedback

        if self.t < 10000000000:
            self.t += 1

        self.feedback_value = output_value
        return (1-self.dry)*output_value + value*self.dry

class reverb:
    a_r_e = 1
    num_of_channel = 0
    d_channel = 0.002
    start_d = 0
    dry = 0
    feedback = 0
    delays = []

    def update(self):
        self.delays = []
        self.d = int(self.d_channel * sample_rate)

        d_matrix = np.arange(0, self.num_of_channel) * self.d\
                   + self.start_d + np.random.randint(-self.a_r_e, self.a_r_e, self.num_of_channel)

        print(d_matrix)
        for i in range(self.num_of_channel):

            n_delay = delay(d_matrix[i])
            n_delay.feedback = self.feedback
            n_delay.dry = 0

            self.delays.append(n_delay)

    def __init__(self, start_d=0.02, dry=0.5, feedback=0.9, num_of_channel=4):
        self.a_r_e = 1
        self.d_channel = 0.002
        self.num_of_channel = num_of_channel
        self.d = int(self.d_channel*sample_rate)
        self.start_d = int(start_d*sample_rate)
        self.dry = dry
        self.feedback = feedback

        d_matrix = np.arange(0, self.num_of_channel) * self.d\
                   + self.start_d + np.random.randint(-self.a_r_e, self.a_r_e, self.num_of_channel)

        print(d_matrix)
        for i in range(self.num_of_channel):
            n_delay = delay(d_matrix[i])
            n_delay.feedback = self.feedback
            n_delay.dry = 0

            self.delays.append(n_delay)

    def tick(self, value):
        d_value = np.zeros(self.num_of_channel)
        for i in range(self.num_of_channel):
            d_value[i] = self.delays[i].tick(value)

        v = d_value.mean()

        return v*(1-self.dry) + value*self.dry


class flanger:
    size = 15/44100
    p_idx = 0
    rate = 1
    amp = 0.002
    buffer = np.zeros(int(size)+100)
    o = osc(True)
    t = 0
    dry = 0.5
    feadback = 0
    fdb = 0

    def __init__(self):
        self.size = 0.005 * 44100
        self.buffer = np.zeros(int(self.size*2) + 200)
        self.o = osc(True)
        self.o.set_wave_form_sine()
        self.t = 0
        self.amp = 0.002
        self.rate = 1
        self.dry = 0.5
        self.feadback = 0
        self.fdb = 0

    def set_dry_wet(self, dry:float=0.5):
        self.dry = dry

    def set_base_frequency(self, mill:float=7):
        self.size = mill * 44.1

    def set_amp_mod(self, mill:float=5):
        self.amp = mill/2000

    def set_rate(self, rate:float=1):
        self.rate = rate

    def get_osc(self):
        return self.o

    def set_feadback(self, num:float=0.3):
        self.feadback = num

    def tick(self, value):
        sizeV = self.o.tick(self.rate) * self.amp * 44100

        idx = int(sizeV)+int(self.size)


        while  self.buffer.size < idx+2:
            self.buffer = np.hstack((self.buffer, np.zeros(2)))

        self.buffer[0: idx] = self.buffer[1: idx+1]

        self.buffer[min(self.p_idx, idx): max(self.p_idx, idx)+1] = value*(1-self.feadback) + self.fdb*self.feadback

        self.p_idx = int(sizeV)+int(self.size)

        self.fdb = self.buffer[0]

        return (self.buffer[0]*self.dry + value*(1-self.dry))


class perlin_noise():
    d = 0
    n = numpy.zeros(d)
    t = 0
    num = 2

    def __init__(self):
        self.d = 4
        self.n = numpy.zeros(self.d)
        self.t = 0
        self.num = 2

    def tick(self):
        if self.d != self.n.size:
            self.n = numpy.zeros(self.d)

        for i in range(self.d):
            if self.t % (math.pow(self.num, i)) == 0:
                #print(i)
                self.n[i] = random.random()*2-1

        self.t += 1

        n = np.zeros(0)
        for i in range(self.d):
            n = np.hstack((n, np.full(int(math.pow(i, 2)), self.n[i])))
        return np.mean(n)

class sample_and_hold():
    _osc = osc()
    _osc2 = osc()
    g = False
    r = 0
    v = 0
    p_ov = 0

    def __init__(self,rate=2000, pwm=0.5):
        self._osc = osc(True)
        self._osc.set_wave_form_square(1, pwm)
        self.v = 0
        self.r = rate
        self.p_ov = 0

    def tick(self, value):
        if self._osc.tick(self.r) == 1.0:
            if self.p_ov == 0:
                self.v = value

            self.p_ov = 1
            return self.v

        else:
            self.p_ov = 0
            return value
