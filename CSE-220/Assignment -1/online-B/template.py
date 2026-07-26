"""
Instructions:
- Reuse the same DiscreteSignal and LTISystem classes from the offline.
- x, h1, the stored window of h2, and the observation range are given below.
- Complete the TODOs.
- Do NOT use numpy.convolve / scipy.signal / any built-in convolution.

Finite-window note:
Mathematically, h2[n] = u[n] continues forever. The code stores enough samples
of h2 for every input sample to affect the complete graded observation window.
Compare results only on OBSERVATION_START...OBSERVATION_END.
"""

import numpy as np
import matplotlib.pyplot as plt


def make_signal(start_time, end_time, values):
    """Helper: build a DiscreteSignal from a list of values."""
    signal = DiscreteSignal(start_time, end_time)
    for offset, value in enumerate(values):
        signal.set_value_at_time(start_time + offset, value)
    return signal


def max_absolute_difference_in_range(first_signal, second_signal, start_time, end_time):
    """Largest |first[n] - second[n]| for start_time <= n <= end_time."""
    # TODO: compute and return the maximum absolute difference on this range.
    raise NotImplementedError


def samples_in_range(signal, start_time, end_time):
    """Return [(n, signal[n]), ...] over an inclusive time range."""
    return [
        (n, signal.get_value_at_time(n))
        for n in range(start_time, end_time + 1)
    ]


def cascade(first_system, second_system, input_signal):
    """Apply first_system, then second_system, and return both outputs."""
    # TODO:
    # intermediate_output = first_system.output(...)
    # final_output = second_system.output(...)
    # return intermediate_output, final_output
    raise NotImplementedError


def plot_cascade_responses(
    input_signal,
    accumulator_output,
    difference_output,
    start_time,
    end_time,
):
    """Plot the input, accumulator response, and first-difference response."""
    times = np.arange(start_time, end_time + 1)

    input_values = [
        input_signal.get_value_at_time(n)
        for n in times
    ]
    accumulator_values = [
        accumulator_output.get_value_at_time(n)
        for n in times
    ]
    difference_values = [
        difference_output.get_value_at_time(n)
        for n in times
    ]

    fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)

    axes[0].stem(times, input_values)
    axes[0].set_title("Input signal $x[n]$")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True)

    axes[1].stem(times, accumulator_values)
    axes[1].set_title("Accumulator response $v[n]$")
    axes[1].set_ylabel("Amplitude")
    axes[1].grid(True)

    axes[2].stem(times, difference_values)
    axes[2].set_title("First-difference response $y[n]$")
    axes[2].set_xlabel("n")
    axes[2].set_ylabel("Amplitude")
    axes[2].grid(True)

    fig.suptitle("Accumulator and First-Difference Cascade")
    plt.tight_layout()
    plt.show()


def main():
    tolerance = 1e-9

    # ---- Given observation window (do not change) ----
    OBSERVATION_START = -2
    OBSERVATION_END = 8

    # ---- Given input signal (do not change) ----
    # x[n] is a non-impulse input with values [2, -1, 3, 1, -2] on n = -2...2 and is zero afterward.
    x = make_signal(
        OBSERVATION_START,
        OBSERVATION_END,
        [2.0, -1.0, 3.0, 1.0, -2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    )

    # TODO: Define impulse responses
    # h1[n] = delta[n] - delta[n-1] = [1, -1]
    # h2[n] = u[n]. Store enough samples for the graded observation window.

    # TODO: create the two LTISystem objects.
    differentiator = None
    accumulator = None

    # TODO: apply x[n] through Accumulator -> First difference.
    accumulator_output = None
    difference_output = None

    # TODO: compare the first-difference response with x[n] on the observation window.
    max_difference = None

    print("=== Input x[n] -> Accumulator -> First difference ===")
    print("Input samples:")
    print(samples_in_range(x, OBSERVATION_START, OBSERVATION_END))
    print("Accumulator response samples:")
    print(samples_in_range(accumulator_output, OBSERVATION_START, OBSERVATION_END))
    print("First-difference response samples:")
    print(samples_in_range(difference_output, OBSERVATION_START, OBSERVATION_END))
    print(f"Maximum absolute difference from x[n]: {max_difference}")

    # TODO: call the provided plotting helper:
    # plot_cascade_responses(
    #     x,
    #     accumulator_output,
    #     difference_output,
    #     OBSERVATION_START,
    #     OBSERVATION_END,
    # )

    print()
    conclusion = None
    print(conclusion)

    if max_difference is not None:
        print("Identity test passed:", max_difference < tolerance)


if __name__ == "__main__":
    main()
