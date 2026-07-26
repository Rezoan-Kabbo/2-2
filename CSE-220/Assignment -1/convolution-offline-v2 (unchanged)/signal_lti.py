import numpy as np


def readable_time_ticks(time_values, max_labels=18):
    if len(time_values) <= max_labels:
        return time_values

    step = int(np.ceil(len(time_values) / max_labels))
    ticks = time_values[::step]

    if ticks[-1] != time_values[-1]:
        ticks.append(time_values[-1])

    return ticks


class DiscreteSignal:
    """Finite discrete-time signal with integer indices."""

    # Arguments: start_time and end_time are integers with start_time <= end_time.
    # Output: None; initialize start_time, end_time, and zero-valued stored samples.
    # Example: DiscreteSignal(-2, 3) represents samples for n = -2, -1, ..., 3.
    def __init__(self, start_time, end_time):
        raise NotImplementedError("Complete the DiscreteSignal constructor")

    # Arguments: none.
    # Returns: int, the number of stored samples in this finite signal.
    # Example: len(DiscreteSignal(-2, 3)) should be 6.
    def __len__(self):
        raise NotImplementedError("Complete __len__")

    # Arguments: none.
    # Returns: range of integer time indices covered by the signal.
    # Example: DiscreteSignal(-1, 2).times() should cover -1, 0, 1, 2.
    def times(self):
        raise NotImplementedError("Complete times")

    # Arguments: t is an integer time index.
    # Returns: float, the signal value at t; return 0.0 if t is outside the range.
    # Example: if x[2] = 5, then x.get_value_at_time(2) should return 5.0.
    def get_value_at_time(self, t):
        raise NotImplementedError("Complete get_value_at_time")

    # Arguments: t is an integer time index, value is the sample value to store.
    # Output: None; update the stored sample at t, or raise an error if t is outside.
    # Example: x.set_value_at_time(2, 5) makes x[2] equal to 5.
    def set_value_at_time(self, t, value):
        raise NotImplementedError("Complete set_value_at_time")

    # Arguments: k is an integer shift amount.
    # Returns: DiscreteSignal, a copy with indices shifted so y[n] = x[n - k].
    # Example: shifting a signal over 0..2 by 3 returns a signal over 3..5.
    def shift(self, k):
        raise NotImplementedError("Complete shift")

    # Arguments: other is another DiscreteSignal.
    # Returns: DiscreteSignal over the combined range with sample-wise sums.
    # Example: if x[0] = 2 and z[0] = 3, then x.add(z)[0] should be 5.
    def add(self, other):
        raise NotImplementedError("Complete add")

    # Arguments: scalar is a number used to multiply every stored sample.
    # Returns: DiscreteSignal with the same time range and scaled sample values.
    # Example: if x[1] = 4, then x.multiply(0.5)[1] should be 2.
    def multiply(self, scalar):
        raise NotImplementedError("Complete multiply")

    # Arguments: tolerance is the threshold below which values are treated as zero.
    # Returns: list of (time_index, value) tuples for samples with abs(value) > tolerance.
    # Example: values [1, 0, 3] starting at n = 0 should return [(0, 1), (2, 3)].
    def nonzero_samples(self, tolerance=1e-12):
        raise NotImplementedError("Complete nonzero_samples")

    def plot(self, title, save_path=None, ax=None):
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots()

        time_values = list(self.times())
        markerline, stemlines, baseline = ax.stem(time_values, self.values)
        markerline.set_markersize(6)
        baseline.set_color("black")
        baseline.set_linewidth(1)

        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel("n")
        ax.set_ylabel("value")
        ax.grid(True, alpha=0.35)
        ax.set_xticks(readable_time_ticks(time_values))
        ax.tick_params(axis="x", labelsize=9)

        if save_path is not None:
            plt.savefig(save_path, bbox_inches="tight", dpi=150)

        return ax


class LTISystem:
    """Discrete-time LTI system described by a finite impulse response."""

    # Arguments: impulse_response is a DiscreteSignal representing h[n].
    # Output: None; store the impulse response that defines this LTI system.
    # Example: LTISystem(impulse_identity()) creates the identity system.
    def __init__(self, impulse_response):
        raise NotImplementedError("Complete the LTISystem constructor")

    # Arguments: input_signal is a DiscreteSignal representing x[n].
    # Returns: (start, end) tuple for the convolution output y[n].
    # Example: x over 0..4 and h over 0..2 produce output range (0, 6).
    def output_range(self, input_signal):
        raise NotImplementedError("Complete output_range")

    # Arguments: input_signal is a DiscreteSignal representing x[n].
    # Returns: list of (k, component_signal) for each nonzero input sample x[k].
    # Example: x[2] = 3 contributes the component 3*h[n - 2].
    def get_response_components(self, input_signal):
        raise NotImplementedError("Complete get_response_components")

    # Arguments: input_signal is a DiscreteSignal representing x[n].
    # Returns: DiscreteSignal y[n], computed by adding all response components.
    # Example: for the identity impulse, the output should match the input signal.
    def output_by_superposition(self, input_signal):
        raise NotImplementedError("Complete output_by_superposition")

    # Arguments: input_signal is a DiscreteSignal and n is one output time index.
    # Returns: list of (k, x_k, h_n_minus_k, product) nonzero contribution tuples.
    # Example: a term may look like (2, 3.0, 0.5, 1.5) for x[2]h[n - 2].
    def get_contributions_at_time(self, input_signal, n):
        raise NotImplementedError("Complete get_contributions_at_time")

    # Arguments: input_signal is a DiscreteSignal and n is one output time index.
    # Returns: float, the convolution-sum value y[n].
    # Example: output_at_time(x, 4) returns the scalar sample y[4].
    def output_at_time(self, input_signal, n):
        raise NotImplementedError("Complete output_at_time")

    # Arguments: input_signal is a DiscreteSignal representing x[n].
    # Returns: DiscreteSignal containing every output sample y[n].
    # Example: system.output(x) returns the full convolution result x[n] * h[n].
    def output(self, input_signal):
        raise NotImplementedError("Complete output")
