"""
image_utils.py  --  PROVIDED. Do not modify.

Image loading/saving, blur-kernel construction and comparison figures for
Task B. Treat it as a black box: no transform, no convolution and no padding
logic lives in here.

Interface
---------
    img    = load_image(path, as_gray=False)   -> float array in [0, 1]
    save_image(img, path)
    k      = make_kernel("bokeh", radius=9)    -> 2D float array, sums to 1
    save_comparison([a, b], ["original", "blurred"], "out/compare.png")
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402


def load_image(path, as_gray=False):
    """
    Load an image as floating point intensities in [0, 1].

    Parameters
    ----------
    path : str
    as_gray : bool
        If True, return a 2D array of shape (H, W). Otherwise return a 3D
        array of shape (H, W, 3) holding R, G, B planes -- in that case your
        convolution must be applied to each colour plane separately.

    Returns
    -------
    numpy.ndarray of float64
    """
    img = Image.open(path)
    img = img.convert("L" if as_gray else "RGB")
    return np.asarray(img, dtype=np.float64) / 255.0


def save_image(array, path):
    """
    Save a float array in [0, 1] (values outside are clipped) as an 8-bit PNG.

    Accepts shape (H, W) for grayscale or (H, W, 3) for colour.
    """
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    data = np.clip(np.asarray(array, dtype=np.float64), 0.0, 1.0)
    data = np.rint(data * 255.0).astype(np.uint8)
    mode = "L" if data.ndim == 2 else "RGB"
    Image.fromarray(data, mode=mode).save(path)
    return path


def make_kernel(name, **params):
    """
    Build a 2D blur kernel as a float array whose entries sum to 1.

    Supported kernels (the offline uses all three):

    ``make_kernel("box", size=k)``
        Uniform k x k average. Cheap, and shows the characteristic boxy
        smearing.

    ``make_kernel("gaussian", size=k, sigma=s)``
        k x k Gaussian with standard deviation ``s`` pixels. If ``sigma`` is
        omitted it defaults to ``size / 6``.

    ``make_kernel("bokeh", radius=r)``
        A filled disc of radius ``r`` pixels with anti-aliased edges, of size
        (2r+1) x (2r+1). This is the out-of-focus "bokeh" blur of a camera
        lens with a circular aperture: bright points become bright discs.

    ``make_kernel("motion", length=L, angle=deg)``
        A straight streak of length ``L`` pixels at ``angle`` degrees
        (0 = horizontal, measured counter-clockwise), as produced by camera
        movement during the exposure.

    Returns
    -------
    numpy.ndarray of float64, shape (kh, kw)
    """
    name = name.lower()

    if name == "box":
        size = int(params.get("size", 9))
        if size < 1:
            raise ValueError("box: size must be >= 1")
        kernel = np.ones((size, size), dtype=np.float64)

    elif name == "gaussian":
        size = int(params.get("size", 15))
        if size < 1:
            raise ValueError("gaussian: size must be >= 1")
        sigma = float(params.get("sigma", size / 6.0))
        half = (size - 1) / 2.0
        axis = np.arange(size, dtype=np.float64) - half
        line = np.exp(-(axis ** 2) / (2.0 * sigma ** 2))
        kernel = np.outer(line, line)

    elif name == "bokeh":
        radius = float(params.get("radius", 9))
        if radius < 1:
            raise ValueError("bokeh: radius must be >= 1")
        size = int(2 * int(round(radius)) + 1)
        half = (size - 1) / 2.0
        # 4x supersampling so the disc edge is smooth rather than jagged.
        fine = np.linspace(-half - 0.5, half + 0.5, size * 4 + 1)[:-1] + (1.0 / 8.0)
        gx, gy = np.meshgrid(fine, fine)
        mask = ((gx ** 2 + gy ** 2) <= radius ** 2).astype(np.float64)
        kernel = mask.reshape(size, 4, size, 4).mean(axis=(1, 3))

    elif name == "motion":
        length = int(params.get("length", 15))
        angle = float(params.get("angle", 0.0))
        if length < 1:
            raise ValueError("motion: length must be >= 1")
        size = length if length % 2 == 1 else length + 1
        kernel = np.zeros((size, size), dtype=np.float64)
        centre = (size - 1) / 2.0
        theta = np.deg2rad(angle)
        for step in np.linspace(-(length - 1) / 2.0, (length - 1) / 2.0, length * 8):
            r = centre - step * np.sin(theta)
            c = centre + step * np.cos(theta)
            r0, c0 = int(np.floor(r)), int(np.floor(c))
            fr, fc = r - r0, c - c0
            for dr, dc, weight in ((0, 0, (1 - fr) * (1 - fc)),
                                   (0, 1, (1 - fr) * fc),
                                   (1, 0, fr * (1 - fc)),
                                   (1, 1, fr * fc)):
                if 0 <= r0 + dr < size and 0 <= c0 + dc < size:
                    kernel[r0 + dr, c0 + dc] += weight

    else:
        raise ValueError("unknown kernel: %r" % (name,))

    total = kernel.sum()
    if total <= 0:
        raise ValueError("kernel %r summed to zero" % (name,))
    return kernel / total


def save_comparison(images, titles, out_path, suptitle=None):
    """
    Save a row of images side by side with titles, for the report.

    Parameters
    ----------
    images : list of numpy arrays
        Each (H, W) or (H, W, 3), float in [0, 1]. They may differ in size.
    titles : list of str
        One per image.
    out_path : str
    suptitle : str, optional
    """
    if len(images) != len(titles):
        raise ValueError("save_comparison: images and titles differ in length")
    parent = os.path.dirname(os.path.abspath(out_path))
    if parent:
        os.makedirs(parent, exist_ok=True)

    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.4), dpi=140)
    if n == 1:
        axes = [axes]
    for ax, img, title in zip(axes, images, titles):
        data = np.clip(np.asarray(img, dtype=np.float64), 0.0, 1.0)
        ax.imshow(data, cmap=None if data.ndim == 3 else "gray",
                  vmin=0.0, vmax=1.0, interpolation="nearest")
        ax.set_title(title, fontsize=10, color="#0b0b0b")
        ax.axis("off")
    if suptitle:
        fig.suptitle(suptitle, fontsize=12, color="#0b0b0b")
    fig.tight_layout()
    fig.savefig(out_path, facecolor="#fcfcfb")
    plt.close(fig)
    return out_path


def save_kernel_preview(kernel, out_path, title="kernel"):
    """Save a magnified view of a kernel (useful when debugging padding)."""
    parent = os.path.dirname(os.path.abspath(out_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    fig, ax = plt.subplots(figsize=(3.6, 3.6), dpi=140)
    ax.imshow(kernel, cmap="magma", interpolation="nearest")
    ax.set_title("%s  (%d x %d)" % (title, kernel.shape[0], kernel.shape[1]),
                 fontsize=10)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, facecolor="#fcfcfb")
    plt.close(fig)
    return out_path
