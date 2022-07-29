import utime as time
from utils import clamp


class PID:
    def __init__(self, k_p, k_i, k_d, reference=0, output_min=None, output_max=None):
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d

        self.reference = reference

        self.output_min = output_min
        self.output_max = output_max

        self.reset()

    def output(self, input, reference=None): 
        if reference is not None:
            self.reference = reference

        error = self.reference - input
        delta_error = error - self.last_error if self.last_error is not None else error

        curr_time = time.ticks_ms()       
        delta_time = time.ticks_diff(curr_time, self.last_time)

        self.proportional = self.k_p * error
        self.integral += self.k_i * error * delta_time
        self.derivative = self.k_d * delta_error / delta_time

        self.integral = clamp(self.integral, self.output_min, self.output_max)

        output = self.proportional + self.derivative + self.integral
        output = clamp(output, self.output_min, self.output_max)

        self.last_time = curr_time
        self.last_input = input
        self.last_output = output
        self.last_error = error

        return output

    def reset(self):
        self.proportional = 0
        self.integral = 0
        self.derivative = 0

        self.integral = clamp(self.integral, self.output_min, self.output_max)

        self.last_time = time.ticks_ms()
        self.last_input = None
        self.last_output = None
        self.last_error = None