"""
image_conv.py  --  TASK B: blurring an image through the frequency domain.

YOUR CODE GOES HERE. image_utils.py (loading, saving, kernels, comparison
figures) and bench_utils.py (timing, runtime plots) are provided; the
transform, the padding logic and the convolution are yours.

Usage (the command line is already wired up for you):

    python3 image_conv.py images/skyline512.png --kernel bokeh --param 9 \
        --engine fft --out-dir outputs/skyline_bokeh
    python3 image_conv.py images/sunset512.png --gray --kernel motion \
        --param 41 --engine fft --out-dir outputs/sunset_motion
    python3 image_conv.py images/skyline512.png --benchmark \
        --out-dir outputs/benchmark

Restrictions: no numpy.fft / scipy.fft / scipy.ndimage / cv2 / PIL filters,
no numpy.convolve, no scipy.signal. Every transform goes through your own
transforms.py.
"""

import argparse
import os

import numpy as np

from bench_utils import plot_runtime_curve, time_best, timing_table_lines
from image_utils import (load_image, make_kernel, save_comparison, save_image,
                         save_kernel_preview)
from io_utils import write_report
from transforms import DFTAnalyzer, FFTTransformer, next_power_of_two


def transform_2d(plane, engine):
    """
    2D forward transform of a single 2D array, by separability.

    The 2D DFT factorises into 1D transforms: transform every ROW, then
    transform every COLUMN of the result (the order does not matter). This is
    the only reason a 2D transform is affordable -- doing it directly from the
    2D definition would be O(N^4).

    Parameters
    ----------
    plane : 2D array_like, shape (P, Q)
    engine : DFTAnalyzer or FFTTransformer

    Returns
    -------
    numpy.ndarray of complex128, shape (P, Q)
    """
    plane = np.asarray(plane, dtype=complex)
    P, Q = plane.shape

    # Transform every row.
    row_transformed = np.empty((P, Q), dtype=complex)
    for r in range(P):
        row_transformed[r, :] = engine.transform(plane[r, :])

    # Then transform every column of that result.
    result = np.empty((P, Q), dtype=complex)
    for c in range(Q):
        result[:, c] = engine.transform(row_transformed[:, c])

    return result


def inverse_2d(spectrum, engine):
    """
    2D inverse transform, the same way round. Shape is preserved.
    """
    spectrum = np.asarray(spectrum, dtype=complex)
    P, Q = spectrum.shape

    col_transformed = np.empty((P, Q), dtype=complex)
    for c in range(Q):
        col_transformed[:, c] = engine.inverse(spectrum[:, c])

    result = np.empty((P, Q), dtype=complex)
    for r in range(P):
        result[r, :] = engine.inverse(col_transformed[r, :])

    return result


def _pad_to(array, shape):
    """Zero-pad a 2D array up to ``shape`` (>= the array's own shape)."""
    out = np.zeros(shape, dtype=np.float64)
    h, w = array.shape
    out[:h, :w] = array
    return out


def convolve_plane(plane, kernel, engine, circular=False):
    """
    Convolve one 2D plane with ``kernel`` through the frequency domain.

    Returns an array the SAME size as the input plane.

    circular=False (the normal case -- linear convolution):
        The full convolution of an (H, W) image with a (kh, kw) kernel is
        (H+kh-1, W+kw-1). Zero-pad both arrays to at least that size before
        transforming -- with FFTTransformer, pad further, up to a power of two
        in each dimension (every engine exposes a ``name`` attribute, so
        ``engine.name == "fft"`` tells you which rule applies). Multiply the
        two spectra, inverse-transform, take the real part, then crop the
        (H, W) window that corresponds to the original pixels: rows
        kh//2 .. kh//2+H-1 and columns kw//2 .. kw//2+W-1
        (the kernel sits at the origin of the padded array, so the result is
        offset by half the kernel -- forget this and your image comes out
        shifted diagonally).

    circular=True (the deliberate mistake -- see the specification):
        Transform at exactly (H, W) with no padding at all, with the kernel
        wrapped around the origin (np.roll is allowed -- it is not a
        transform). The output is the CIRCULAR convolution: content that
        should have fallen off one edge reappears on the opposite edge. The
        provided images are 256x256 and 512x512, so this path works with the
        radix-2 FFT directly.

    Parameters
    ----------
    plane : 2D numpy array of float, values in [0, 1]
    kernel : 2D numpy array of float, sums to 1
    engine : DFTAnalyzer or FFTTransformer
    circular : bool

    Returns
    -------
    numpy.ndarray of float64, same shape as ``plane``
    """
    plane = np.asarray(plane, dtype=np.float64)
    kernel = np.asarray(kernel, dtype=np.float64)
    H, W = plane.shape
    kh, kw = kernel.shape

    if circular:
        # No padding at all: transform at exactly (H, W). The kernel is
        # placed with its own origin at (0, 0) of an (H, W) canvas and then
        # rolled so its centre sits at the origin -- wrapping around the
        # edges, which is exactly what makes this circular.
        kernel_full = _pad_to(kernel, (H, W))
        kernel_full = np.roll(kernel_full, -(kh // 2), axis=0)
        kernel_full = np.roll(kernel_full, -(kw // 2), axis=1)

        A = transform_2d(plane, engine)
        B = transform_2d(kernel_full, engine)
        C = A * B
        full = inverse_2d(C, engine).real
        return full

    # Linear convolution: pad to at least (H+kh-1, W+kw-1).
    needed_h = H + kh - 1
    needed_w = W + kw - 1
    if getattr(engine, "name", None) == "fft":
        N_h = next_power_of_two(needed_h)
        N_w = next_power_of_two(needed_w)
    else:
        N_h, N_w = needed_h, needed_w

    plane_padded = _pad_to(plane, (N_h, N_w))
    kernel_padded = _pad_to(kernel, (N_h, N_w))

    A = transform_2d(plane_padded, engine)
    B = transform_2d(kernel_padded, engine)
    C = A * B
    full = inverse_2d(C, engine).real

    # The kernel sits at the origin of the padded array, so the true result
    # is offset by half the kernel: crop the (H, W) window starting there.
    r0, c0 = kh // 2, kw // 2
    return full[r0:r0 + H, c0:c0 + W]


def convolve_image(image, kernel, engine, circular=False):
    """
    Apply convolve_plane to a whole image.

    A grayscale image is (H, W); a colour image is (H, W, 3) and each colour
    plane is convolved independently, then stacked back together.
    """
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return convolve_plane(image, kernel, engine, circular=circular)

    planes = [
        convolve_plane(image[:, :, ch], kernel, engine, circular=circular)
        for ch in range(image.shape[2])
    ]
    return np.stack(planes, axis=-1)


def convolve_plane_direct(plane, kernel):
    """
    Spatial convolution, written out literally, as the correctness oracle and
    the third benchmark curve.

        out[r, c] = sum_i sum_j  plane[r + kh//2 - i, c + kw//2 - j] * kernel[i, j]

    with out-of-range pixels treated as zero. Four nested loops, O(N^2 K^2),
    no NumPy vectorisation -- this one is meant to be slow and obviously
    correct. It is never applied to a full 512x512 image (see run_single).
    """
    plane = np.asarray(plane, dtype=np.float64)
    kernel = np.asarray(kernel, dtype=np.float64)
    H, W = plane.shape
    kh, kw = kernel.shape
    half_h, half_w = kh // 2, kw // 2

    out = np.zeros((H, W), dtype=np.float64)
    for r in range(H):
        for c in range(W):
            total = 0.0
            for i in range(kh):
                rr = r + half_h - i
                if rr < 0 or rr >= H:
                    continue
                for j in range(kw):
                    cc = c + half_w - j
                    if cc < 0 or cc >= W:
                        continue
                    total += plane[rr, cc] * kernel[i, j]
            out[r, c] = total
    return out


_KERNEL_BUILDERS = {
    "bokeh": lambda param: make_kernel("bokeh", radius=param),
    "gaussian": lambda param: make_kernel("gaussian", size=int(round(param))),
    "box": lambda param: make_kernel("box", size=int(round(param))),
    "motion": lambda param: make_kernel("motion", length=int(round(param)), angle=30.0),
}


def _make_engine(engine_name):
    if engine_name == "dft":
        return DFTAnalyzer()
    if engine_name == "fft":
        return FFTTransformer()
    if engine_name == "arbitrary":
        raise NotImplementedError("Bonus: --engine arbitrary not implemented")
    raise ValueError("unknown engine: %r" % engine_name)


def run_single(path, kernel_name, param, engine_name, out_dir, gray=False):
    """
    Blur one image and write the required outputs.

    Build the kernel with image_utils.make_kernel:
        bokeh    -> make_kernel("bokeh", radius=param)
        gaussian -> make_kernel("gaussian", size=param)
        box      -> make_kernel("box", size=param)
        motion   -> make_kernel("motion", length=param, angle=30.0)

    Must produce, inside ``out_dir``:
      blurred.png     -- the linear (zero-padded) convolution
      wraparound.png  -- the same blur computed circularly, with no padding
      kernel.png      -- image_utils.save_kernel_preview of the kernel
      comparison.png  -- image_utils.save_comparison of original / blurred /
                         wraparound, side by side
      report.txt      -- image path and size, kernel name and size, engine,
                         the linear-convolution size, the transform size you
                         actually used, and the verification result. It is
                         written by your code; there is no separate write-up
                         to hand in.

    Verification: convolve the top-left 64x64 corner of the image (first colour
    plane, if colour) both ways -- convolve_plane and convolve_plane_direct --
    and report max |spectral - direct|. It should be ~1e-15, and anything above
    1e-9 is a bug, not rounding.
    """
    if kernel_name not in _KERNEL_BUILDERS:
        raise ValueError("unknown kernel: %r" % kernel_name)
    kernel = _KERNEL_BUILDERS[kernel_name](param)
    kh, kw = kernel.shape

    engine = _make_engine(engine_name)

    image = load_image(path, as_gray=gray)
    plane_for_report = image if image.ndim == 2 else image[:, :, 0]
    H, W = plane_for_report.shape

    linear = convolve_image(image, kernel, engine, circular=False)
    wraparound = convolve_image(image, kernel, engine, circular=True)

    os.makedirs(out_dir, exist_ok=True)
    blurred_path = os.path.join(out_dir, "blurred.png")
    wraparound_path = os.path.join(out_dir, "wraparound.png")
    kernel_path = os.path.join(out_dir, "kernel.png")
    comparison_path = os.path.join(out_dir, "comparison.png")

    save_image(linear, blurred_path)
    save_image(wraparound, wraparound_path)
    save_kernel_preview(kernel, kernel_path, title="%s kernel" % kernel_name)
    save_comparison(
        [image, linear, wraparound],
        ["original", "linear convolution (zero-padded)", "circular convolution (no padding)"],
        comparison_path,
        suptitle="%s, %s kernel %dx%d, engine=%s" % (
            os.path.basename(path), kernel_name, kh, kw, engine_name),
    )

    # Transform sizes actually used (mirrors the logic inside convolve_plane).
    needed_h, needed_w = H + kh - 1, W + kw - 1
    if getattr(engine, "name", None) == "fft":
        N_h, N_w = next_power_of_two(needed_h), next_power_of_two(needed_w)
    else:
        N_h, N_w = needed_h, needed_w

    # Verification: top-left 64x64 corner (or the whole plane if smaller),
    # spectral method vs the literal spatial oracle.
    crop_h, crop_w = min(64, H), min(64, W)
    crop = plane_for_report[:crop_h, :crop_w]
    spectral_crop = convolve_plane(crop, kernel, engine, circular=False)
    direct_crop = convolve_plane_direct(crop, kernel)
    max_diff = float(np.max(np.abs(spectral_crop - direct_crop)))
    verdict = "MATCH" if max_diff < 1e-9 else "MISMATCH"

    write_report(
        os.path.join(out_dir, "report.txt"),
        [
            "Task B -- single blur",
            "",
            "input file:            %s" % path,
            "image size:            %d x %d%s" % (
                image.shape[0], image.shape[1],
                "" if image.ndim == 2 else (" x %d" % image.shape[2])),
            "kernel:                %s (param=%s), size %d x %d" % (
                kernel_name, param, kh, kw),
            "engine:                %s" % engine_name,
            "linear-convolution size: %d x %d" % (needed_h, needed_w),
            "transform size used N:  %d x %d" % (N_h, N_w),
            "verification (64x64 corner): max|spectral - direct| = %.3e -> %s" % (
                max_diff, verdict),
        ],
    )

    print("%s [%s, %s]: verification %s (max diff %.3e)" % (
        path, kernel_name, engine_name, verdict, max_diff))
    if verdict == "MISMATCH":
        import sys
        print("  WARNING: spectral and direct convolution disagree!", file=sys.stderr)

    return verdict


# ---------------------------------------------------------------------------
# PROVIDED -- run_benchmark is already written. It calls your convolve_plane
# and convolve_plane_direct, so it starts working as soon as those are
# correct. You do not need to modify anything below (though you may extend
# it).
# ---------------------------------------------------------------------------
IMAGE_SIZES = [16, 32, 64, 128, 256, 512]
KERNEL_RADII = [1, 3, 7, 15, 31]
BENCH_RADIUS = 7            # kernel used for the growing-image study
BENCH_SIZE = 256            # image crop used for the growing-kernel study
TIME_BUDGET = 8.0           # stop a sweep once one measurement exceeds this


def run_benchmark(path, out_dir):
    """
    Two timing studies, two plots, both on one grayscale plane:

      1. growing image, fixed kernel   -> runtime_vs_image_size.png
      2. growing kernel, fixed image   -> runtime_vs_kernel_size.png

    plus both timing tables in report.txt. Each sweep stops early once a
    single measurement exceeds TIME_BUDGET seconds, so a slow machine simply
    produces a shorter curve rather than hanging.
    """
    full = load_image(path, as_gray=True)

    def sweep(label, make_call, points):
        """points: list of (x_value, zero-argument-callable-factory input)."""
        xs, ys = [], []
        print("%s:" % label)
        for x, arg in points:
            seconds = time_best(make_call(arg), repeats=1)
            xs.append(x)
            ys.append(seconds)
            print("  %8s   %9.4f s" % (x, seconds))
            if seconds > TIME_BUDGET:
                print("  (stopping this curve -- over the time budget)")
                break
        return xs, ys

    # ---- study 1: fixed kernel, growing image
    kernel = make_kernel("bokeh", radius=BENCH_RADIUS)
    crops = [(n, full[:n, :n].copy()) for n in IMAGE_SIZES]

    size_series = {}
    size_series["Naive DFT (row-column)"] = sweep(
        "naive DFT", lambda img: (lambda: convolve_plane(img, kernel, DFTAnalyzer())), crops)
    size_series["Radix-2 FFT (row-column)"] = sweep(
        "radix-2 FFT", lambda img: (lambda: convolve_plane(img, kernel, FFTTransformer())), crops)
    size_series["Direct spatial convolution"] = sweep(
        "direct spatial", lambda img: (lambda: convolve_plane_direct(img, kernel)), crops)

    size_plot = os.path.join(out_dir, "runtime_vs_image_size.png")
    plot_runtime_curve(size_series, size_plot,
                       title="Task B: %d x %d blur of an N x N image" % kernel.shape,
                       xlabel="image side length N (pixels)",
                       references=("n3", "n2"))

    # ---- study 2: fixed image, growing kernel
    image = full[:BENCH_SIZE, :BENCH_SIZE].copy()
    kernels = [(make_kernel("bokeh", radius=r).shape[0], make_kernel("bokeh", radius=r))
               for r in KERNEL_RADII]

    kernel_series = {}
    kernel_series["Direct spatial convolution"] = sweep(
        "direct spatial", lambda k: (lambda: convolve_plane_direct(image, k)), kernels)
    kernel_series["Radix-2 FFT (row-column)"] = sweep(
        "radix-2 FFT", lambda k: (lambda: convolve_plane(image, k, FFTTransformer())), kernels)

    kernel_plot = os.path.join(out_dir, "runtime_vs_kernel_size.png")
    plot_runtime_curve(kernel_series, kernel_plot,
                       title="Task B: %d x %d image, growing kernel" % image.shape,
                       xlabel="kernel side length K (pixels)",
                       references=("n2",))

    write_report(os.path.join(out_dir, "report.txt"),
                 ["Task B -- runtime benchmark", "",
                  "Study 1: fixed %d x %d kernel, growing image" % kernel.shape, ""]
                 + timing_table_lines(size_series, size_label="N")
                 + ["", "plot: %s" % os.path.basename(size_plot), "",
                    "Study 2: fixed %d x %d image, growing kernel" % image.shape, ""]
                 + timing_table_lines(kernel_series, size_label="K")
                 + ["", "plot: %s" % os.path.basename(kernel_plot)])
    print("wrote", size_plot, "and", kernel_plot)


def main():
    ap = argparse.ArgumentParser(description="2D convolution by DFT/FFT")
    ap.add_argument("image", help="path to the input image")
    ap.add_argument("--kernel", default="bokeh",
                    choices=["bokeh", "gaussian", "box", "motion"])
    ap.add_argument("--param", type=float, default=9,
                    help="bokeh radius / gaussian size / box size / motion length")
    ap.add_argument("--engine", default="fft", choices=["dft", "fft", "arbitrary"])
    ap.add_argument("--gray", action="store_true", help="process as grayscale")
    ap.add_argument("--out-dir", default="outputs")
    ap.add_argument("--benchmark", action="store_true",
                    help="run the timing study instead of a single blur")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    if args.benchmark:
        run_benchmark(args.image, args.out_dir)
    else:
        run_single(args.image, args.kernel, args.param, args.engine,
                   args.out_dir, gray=args.gray)


if __name__ == "__main__":
    main()