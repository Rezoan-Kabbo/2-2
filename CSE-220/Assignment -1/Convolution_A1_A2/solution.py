# =====================================================================
# Assignment Tasks
# =====================================================================

import numpy as np
import matplotlib.pyplot as plt

from signal_lti import DiscreteSignal, LTISystem, readable_time_ticks

def make_signal(start_time, end_time, values):
    """Helper: build a DiscreteSignal from a list of values."""
    signal = DiscreteSignal(start_time, end_time)
    for offset, value in enumerate(values):
        signal.set_value_at_time(start_time + offset, value)
    return signal


def max_absolute_difference(first_signal, second_signal):
    """Helper: largest |difference| between two signals over their combined range."""
    min_t = min(first_signal.start_time, second_signal.start_time)
    max_t = max(first_signal.end_time, second_signal.end_time)
    
    max_diff = 0.0
    for t in range(min_t, max_t + 1):
        diff = abs(first_signal.get_value_at_time(t) - second_signal.get_value_at_time(t))
        if diff > max_diff:
            max_diff = diff
            
    return max_diff


def test_linearity(apply_system, x1, x2, a, b):
    # T{a*x1 + b*x2}
    scaled_x1 = x1.multiply(a)
    scaled_x2 = x2.multiply(b)
    combined_input = scaled_x1.add(scaled_x2)
    output_combined_input = apply_system(combined_input) # nickname or alias of system_b or LTIsystem ouput function
    
    # a*T{x1} + b*T{x2}
    out1 = apply_system(x1) 
    out2 = apply_system(x2)
    scaled_out1 = out1.multiply(a)
    scaled_out2 = out2.multiply(b)
    combined_outputs = scaled_out1.add(scaled_out2)
    
    # Return max| apply_system(a*x1 + b*x2)  -  (a*apply_system(x1) + b*apply_system(x2)) |
    return max_absolute_difference(output_combined_input, combined_outputs)


def test_time_invariance(apply_system, x, k):
    # T{x(n - k)}
    shifted_input = x.shift(k)
    output_of_shifted_input = apply_system(shifted_input)
    
    # y(n - k) where y(n) = T{x(n)}
    standard_output = apply_system(x)
    shifted_output = standard_output.shift(k)
    
    # Return max| apply_system(x shifted by k)  -  (apply_system(x) shifted by k) |
    return max_absolute_difference(output_of_shifted_input, shifted_output)


def system_b(input_signal):
    # yB(n) = n * x(n)
    result = DiscreteSignal(input_signal.start_time, input_signal.end_time)
    for n in input_signal.times():
        result.set_value_at_time(n, n * input_signal.get_value_at_time(n))
    return result


def main():
    tolerance = 1e-9

    # ---- Given signals and scalars (do not change) ----
    x1 = make_signal(-2, 2, [1, 0, 2, -1, 3])
    x2 = make_signal(-1, 3, [2, -3, 0, 1, 1])
    a, b = 2.0, -3.0
    k = 3

    h = make_signal(0, 2, [1.0, 0.5, 0.25])
    
    # Instantiate System A using your LTISystem class
    system_a = LTISystem(h)

    # Test both properties for system A
    print("=== System A: genuine LTI system (LTISystem.output) ===")
    diff_linear_a = test_linearity(system_a.output, x1, x2, a, b)
    diff_ti_a = test_time_invariance(system_a.output, x1, k)
    
    print(f"Linearity max diff:        {diff_linear_a}")
    print(f"Time-invariance max diff:  {diff_ti_a}")

    print()

    # Test both properties for system B
    print("=== System B: y[n] = n * x[n] ===")
    diff_linear_b = test_linearity(system_b, x1, x2, a, b)
    diff_ti_b = test_time_invariance(system_b, x1, k)
    
    print(f"Linearity max diff:        {diff_linear_b}")
    print(f"Time-invariance max diff:  {diff_ti_b}")

    print()
    
    # Conclusion
    if diff_linear_b <= tolerance and diff_ti_b > tolerance:
        print("Conclusion: System B fails time-invariance, but it is linear.")
    elif diff_linear_b > tolerance and diff_ti_b <= tolerance:
        print("Conclusion: System B fails linearity, but it is time-invariant.")
    else:
        print("Conclusion: System B fails both linearity and time-invariance.")


if __name__ == "__main__":
    main()