import os
import argparse

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from signal_lti import DiscreteSignal, LTISystem, readable_time_ticks


# Arguments: start_time and end_time are integers; values is a list of samples.
# Returns: DiscreteSignal with values placed from start_time through end_time.
# Example: make_signal(2, 4, [7, 8, 9]) creates x[2] = 7, x[3] = 8, x[4] = 9.
def make_signal(start_time, end_time, values):
    raise NotImplementedError("Complete make_signal")


# Arguments: start_time/end_time are integers; samples maps time indices to values.
# Returns: DiscreteSignal over the full range, with unspecified samples left as 0.
# Example: signal_from_samples(0, 3, {0: 1, 2: 5}) creates values [1, 0, 5, 0].
def signal_from_samples(start_time, end_time, samples):
    raise NotImplementedError("Complete signal_from_samples")


# Arguments: none.
# Returns: DiscreteSignal for the identity impulse response h[0] = 1.
# Example: impulse_identity() creates a signal over 0..0 with value 1.
def impulse_identity():
    raise NotImplementedError("Complete impulse_identity")


# Arguments: length is a positive integer number of averaging samples.
# Returns: DiscreteSignal h[n] = 1/length for n = 0, ..., length - 1.
# Example: impulse_moving_average(3) returns h[0] = h[1] = h[2] = 1/3.
def impulse_moving_average(length):
    raise NotImplementedError("Complete impulse_moving_average")


# Return the 3-point moving average: h[0] = h[1] = h[2] = 1/3.
def impulse_moving_average_3():
    return impulse_moving_average(3)


# Return the 5-point moving average: h[0] through h[4] are all 1/5.
def impulse_moving_average_5():
    return impulse_moving_average(5)


# Return the 7-point moving average: h[0] through h[6] are all 1/7.
def impulse_moving_average_7():
    return impulse_moving_average(7)


# Arguments: none.
# Returns: DiscreteSignal for weighted smoothing: h[0] = 0.5, h[1] = 0.3, h[2] = 0.2.
# Example: this system computes 0.5x[n] + 0.3x[n - 1] + 0.2x[n - 2].
def impulse_weighted_smoothing():
    raise NotImplementedError("Complete impulse_weighted_smoothing")


# Arguments: none.
# Returns: DiscreteSignal for the first-difference impulse h[0] = 1, h[1] = -1.
# Example: this system computes y[n] = x[n] - x[n - 1].
def impulse_first_difference():
    raise NotImplementedError("Complete impulse_first_difference")


BUILT_IN_IMPULSES = [
    ("identity", "identity: h[0] = 1", impulse_identity),
    ("moving_average_3", "3-point moving average", impulse_moving_average_3),
    ("moving_average_5", "5-point moving average", impulse_moving_average_5),
    ("moving_average_7", "7-point moving average", impulse_moving_average_7),
    (
        "weighted_smoothing",
        "weighted smoothing: 0.5x[n] + 0.3x[n-1] + 0.2x[n-2]",
        impulse_weighted_smoothing,
    ),
    ("first_difference", "first difference: x[n] - x[n-1]", impulse_first_difference),
]


def read_nonempty_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = []
        for line in file:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                lines.append(stripped)
    return lines


def parse_signal(lines, index):
    start_time, end_time = map(int, lines[index].split())
    values = list(map(float, lines[index + 1].split()))
    return make_signal(start_time, end_time, values), index + 2


def parse_impulse_response(lines, index):
    mode = lines[index].strip().lower()
    index += 1

    if mode == "custom":
        impulse_response, index = parse_signal(lines, index)
        return [("convolution", "custom impulse response", impulse_response)], index

    if mode in {"built-in", "builtin"}:
        impulse_cases = []
        for number, (slug, description, factory) in enumerate(BUILT_IN_IMPULSES, start=1):
            prefix = f"builtin_{number}_{slug}"
            impulse_cases.append((prefix, description, factory()))
        return impulse_cases, index

    raise ValueError("Impulse response mode must be custom or built-in")


def read_problem_from_file(file_path):
    lines = read_nonempty_lines(file_path)

    input_signal, index = parse_signal(lines, 0)
    impulse_cases, index = parse_impulse_response(lines, index)

    if index != len(lines):
        raise ValueError("Input file has extra lines after the impulse response section")

    return input_signal, impulse_cases


def print_signal(signal, name):
    lines = [f"{name}:"]
    for n in signal.times():
        lines.append(f"  n = {n:4d}, value = {signal.get_value_at_time(n):10.4f}")
    lines.append("")
    return "\n".join(lines)


# Arguments: first_signal and second_signal are DiscreteSignal objects.
# Returns: float, the largest absolute difference over their combined time range.
# Example: if the only mismatch is 0.25 at n = 2, return 0.25.
def max_absolute_difference(first_signal, second_signal):
    raise NotImplementedError("Complete max_absolute_difference")


def normalized_grayscale_rgb(signal):
    values = np.array(signal.values, dtype=float)
    minimum = float(np.min(values))
    maximum = float(np.max(values))

    if np.isclose(minimum, maximum):
        gray_values = np.full(values.shape, 128, dtype=np.uint8)
    else:
        gray_values = np.round(255 * (values - minimum) / (maximum - minimum))
        gray_values = gray_values.astype(np.uint8)

    return np.stack([gray_values, gray_values, gray_values], axis=-1)


def plot_signals_as_stems(input_signal, impulse_response, output_signal, save_path):
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), constrained_layout=True)

    input_signal.plot("Input signal x[n]", ax=axes[0])
    impulse_response.plot("Impulse response h[n]", ax=axes[1])
    output_signal.plot("Output signal y[n]", ax=axes[2])

    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_color_blocks(signal, title, ax):
    rgb_values = normalized_grayscale_rgb(signal)
    image = rgb_values.reshape(1, len(rgb_values), 3)
    time_values = list(signal.times())
    tick_labels = readable_time_ticks(time_values)
    tick_positions = [time_values.index(label) for label in tick_labels]

    ax.imshow(image, aspect="auto", interpolation="nearest")
    ax.set_title(title)
    ax.set_yticks([])
    ax.set_xlabel("n")
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)
    ax.tick_params(axis="x", labelsize=9)

    for boundary in range(len(signal.values) + 1):
        ax.axvline(boundary - 0.5, color="white", linewidth=0.8)


def plot_signals_as_color_blocks(input_signal, output_signal, save_path):
    fig, axes = plt.subplots(2, 1, figsize=(10, 3.6), constrained_layout=True)

    plot_color_blocks(input_signal, "Input signal x[n]", axes[0])
    plot_color_blocks(output_signal, "Output signal y[n]", axes[1])

    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def save_visualizations(input_signal, impulse_response, output_signal, out_dir, file_prefix):
    plot_dir = os.path.join(out_dir, "plot")
    color_dir = os.path.join(out_dir, "color")
    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(color_dir, exist_ok=True)

    plot_path = os.path.join(plot_dir, f"{file_prefix}.png")
    color_path = os.path.join(color_dir, f"{file_prefix}.png")

    plot_signals_as_stems(input_signal, impulse_response, output_signal, plot_path)
    plot_signals_as_color_blocks(
        input_signal,
        output_signal,
        color_path,
    )

    return plot_path, color_path


def clear_old_figures(out_dir):
    for file_name in os.listdir(out_dir):
        file_path = os.path.join(out_dir, file_name)
        if os.path.isfile(file_path) and (
            file_name.endswith(".png") or file_name in {"results.txt", "report.txt"}
        ):
            os.remove(file_path)

    for folder_name in ("plot", "color"):
        folder_path = os.path.join(out_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".png"):
                os.remove(os.path.join(folder_path, file_name))


def build_report_section(
    title,
    input_signal,
    impulse_response,
    output_signal,
    maximum_difference,
    plot_path,
    color_path,
):
    lines = [
        title,
        "=" * len(title),
        print_signal(input_signal, "Input signal x[n]"),
        print_signal(impulse_response, "Impulse response h[n]"),
        print_signal(output_signal, "Output signal y[n]"),
        "Verification",
        f"Output range: [{output_signal.start_time}, {output_signal.end_time}]",
        f"Maximum absolute difference between two methods: {maximum_difference:.12g}",
        "",
        f"Stem plot: {plot_path}",
        f"Color plot: {color_path}",
        "",
    ]
    return "\n".join(lines)


def build_report(input_file, sections):
    lines = [f"Input file: {input_file}", ""]
    lines.extend(sections)
    return "\n".join(lines)


def write_report(report, out_dir):
    report_path = os.path.join(out_dir, "report.txt")
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)
    return report_path


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run finite discrete-time convolution from an input file."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input file, for example inputs/1.txt",
    )
    parser.add_argument(
        "--out-dir",
        default="outputs",
        help="Directory where the report and figures will be written.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    os.makedirs(args.out_dir, exist_ok=True)
    clear_old_figures(args.out_dir)

    input_signal, impulse_cases = read_problem_from_file(args.input_file)

    report_sections = []

    for file_prefix, description, impulse_response in impulse_cases:
        system = LTISystem(impulse_response)
        y_superposition = system.output_by_superposition(input_signal)
        y_convolution = system.output(input_signal)
        maximum_difference = max_absolute_difference(y_superposition, y_convolution)

        plot_path, color_path = save_visualizations(
            input_signal,
            impulse_response,
            y_convolution,
            args.out_dir,
            file_prefix,
        )
        title = f"Impulse response: {description}"
        report_sections.append(
            build_report_section(
                title,
                input_signal,
                impulse_response,
                y_convolution,
                maximum_difference,
                plot_path,
                color_path,
            )
        )

    report = build_report(args.input_file, report_sections)
    report_path = write_report(report, args.out_dir)

    print(report)
    print(f"Saved report: {report_path}")
    print(f"Generated {len(impulse_cases)} impulse response output set(s).")


if __name__ == "__main__":
    main()
