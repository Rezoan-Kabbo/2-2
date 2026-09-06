"""
bench_utils.py  --  PROVIDED. Do not modify.

Timing helper and runtime-curve plotting for the benchmark parts of both
tasks. You call these; you do not need to read or understand the internals.

Typical use
-----------
    from bench_utils import time_best, plot_runtime_curve

    dft_times, fft_times, sizes = [], [], []
    for n in [64, 128, 256, 512]:
        sizes.append(n)
        dft_times.append(time_best(lambda: multiply_with("dft", a, b)))
        fft_times.append(time_best(lambda: multiply_with("fft", a, b)))

    plot_runtime_curve(
        {"Naive DFT": (sizes, dft_times), "Radix-2 FFT": (sizes, fft_times)},
        "plots/runtime_bigmul.png",
        title="Big-integer multiplication: naive DFT vs radix-2 FFT",
        xlabel="number of decimal digits per operand",
        references=("n2", "nlogn"),
    )
"""

import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# Categorical palette (colour-blind safe, fixed order -- never cycle it).
_SERIES_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#eda100"]
_INK = "#0b0b0b"
_MUTED = "#52514e"
_GRID = "#dcdcd8"


def time_best(fn, repeats=3):
    """
    Run ``fn`` ``repeats`` times and return the SMALLEST wall-clock time in
    seconds.

    The minimum (not the mean) is the standard choice for micro-benchmarks:
    anything slower than the fastest run was slowed down by something that
    is not your algorithm (OS scheduling, garbage collection, cache misses
    caused by other processes).

    Parameters
    ----------
    fn : zero-argument callable
        The thing being timed. Wrap arguments with a lambda.
    repeats : int
        How many times to run it. Keep this small for slow measurements.

    Returns
    -------
    float
        Best observed running time, in seconds.
    """
    best = float("inf")
    for _ in range(max(1, int(repeats))):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def _reference_curve(kind, xs):
    x = np.asarray(xs, dtype=float)
    if kind == "n":
        return x, "O(n)"
    if kind == "nlogn":
        return x * np.log2(np.maximum(x, 2.0)), "O(n log n)"
    if kind == "n2":
        return x ** 2, "O(n^2)"
    if kind == "n3":
        return x ** 3, "O(n^3)"
    if kind == "n4":
        return x ** 4, "O(n^4)"
    raise ValueError("unknown reference curve: %r" % (kind,))


def plot_runtime_curve(series, out_path, title, xlabel,
                       ylabel="best running time (seconds)", references=()):
    """
    Draw measured running times on log-log axes and save the figure.

    Parameters
    ----------
    series : dict
        Maps a label (string, shown in the legend) to a pair ``(xs, ys)`` of
        equal-length sequences: problem sizes and measured seconds. Insertion
        order fixes the colours, so keep the order stable across runs.
    out_path : str
        Where to save the PNG. Parent directories are created if needed.
    title, xlabel, ylabel : str
        Figure title and axis labels.
    references : iterable of str
        Optional dashed guide lines, drawn behind the data and scaled to pass
        through the last point of the FIRST series. Any of:
        ``"n"``, ``"nlogn"``, ``"n2"``, ``"n3"``, ``"n4"``.
        On log-log axes a measured curve that is parallel to a guide line has
        that complexity -- this is how you SHOW your FFT is O(n log n) rather
        than merely claiming it.
    """
    if not series:
        raise ValueError("plot_runtime_curve: nothing to plot")

    parent = os.path.dirname(os.path.abspath(out_path))
    if parent:
        os.makedirs(parent, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)

    # Guide lines are anchored to the last point of the first series, and the
    # y-axis is clamped to the measured data afterwards so a steep guide cannot
    # squash the curves that matter.
    anchor_x, anchor_y = None, None
    for (xs, ys) in series.values():
        if len(xs):
            anchor_x, anchor_y = float(xs[-1]), float(ys[-1])
            break

    for kind in references:
        gx, glabel = _reference_curve(kind, [anchor_x])
        scale = anchor_y / float(gx[0])
        span = np.geomspace(
            min(min(v[0]) for v in series.values() if len(v[0])),
            max(max(v[0]) for v in series.values() if len(v[0])),
            64,
        )
        gy, _ = _reference_curve(kind, span)
        ax.plot(span, np.asarray(gy) * scale, linestyle=(0, (4, 3)),
                linewidth=1.0, color=_GRID, zorder=1)
        ax.annotate(glabel, xy=(span[0], gy[0] * scale), xytext=(-4, 0),
                    textcoords="offset points", fontsize=8, color=_MUTED,
                    va="center", ha="right", zorder=1)

    placed = []
    for i, (label, (xs, ys)) in enumerate(series.items()):
        color = _SERIES_COLORS[i % len(_SERIES_COLORS)]
        ax.plot(xs, ys, marker="o", markersize=5, linewidth=2.0,
                color=color, label=label, zorder=3,
                markeredgecolor="#ffffff", markeredgewidth=0.8)
        if len(xs):
            # Direct-label the end of the curve, but only where it will not
            # collide with a label already placed (the legend still names it).
            ex, ey = float(xs[-1]), float(ys[-1])
            crowded = any(
                abs(np.log10(max(ex, 1e-12)) - np.log10(max(px, 1e-12))) < 0.12
                and abs(np.log10(max(ey, 1e-12)) - np.log10(max(py, 1e-12))) < 0.20
                for (px, py) in placed
            )
            if not crowded:
                ax.annotate(label, xy=(ex, ey), xytext=(6, 6),
                            textcoords="offset points", fontsize=9,
                            color=_INK, fontweight="bold", zorder=4)
                placed.append((ex, ey))

    ax.set_xscale("log")
    ax.set_yscale("log")
    all_x = [x for (xs, _) in series.values() for x in xs]
    if all_x:
        lo, hi = float(min(all_x)), float(max(all_x))
        ax.set_xlim(lo / 1.7, hi * 1.7)
    all_y = [y for (_, ys) in series.values() for y in ys if y > 0]
    if all_y:
        ax.set_ylim(min(all_y) / 3.0, max(all_y) * 4.0)
    ax.set_title(title, fontsize=11, color=_INK, pad=10)
    ax.set_xlabel(xlabel, fontsize=9.5, color=_MUTED)
    ax.set_ylabel(ylabel, fontsize=9.5, color=_MUTED)
    ax.tick_params(colors=_MUTED, labelsize=8.5)
    ax.grid(True, which="both", color=_GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_GRID)
    if len(series) >= 2:
        ax.legend(frameon=False, fontsize=9, labelcolor=_INK, loc="upper left")

    fig.tight_layout()
    fig.savefig(out_path, facecolor="#fcfcfb")
    plt.close(fig)
    return out_path


def timing_table_lines(series, size_label="size"):
    """
    Format measured timings as aligned text lines for report.txt.

    Parameters
    ----------
    series : dict
        Same structure as ``plot_runtime_curve``.
    size_label : str
        Header for the first column.

    Returns
    -------
    list of str
    """
    labels = list(series.keys())
    sizes = sorted({int(x) for (xs, _) in series.values() for x in xs})
    width = max(12, max(len(s) for s in labels) + 2)
    head = f"{size_label:>12}" + "".join(f"{s:>{width}}" for s in labels)
    lines = [head, "-" * len(head)]
    for n in sizes:
        row = f"{n:>12}"
        for label in labels:
            xs, ys = series[label]
            found = [y for (x, y) in zip(xs, ys) if int(x) == n]
            row += f"{found[0]:>{width}.6f}" if found else f"{'--':>{width}}"
        lines.append(row)
    return lines
