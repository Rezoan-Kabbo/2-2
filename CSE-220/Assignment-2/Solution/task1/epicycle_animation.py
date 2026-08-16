"""
epicycle_animation.py -- PROVIDED CODE. You do not need to read or modify this file.

Turns a *completed* FourierEpicycles object (i.e. one whose
calculate_all_coefficients() has already been called) into the classic
"epicycle" animation: a chain of rotating circles whose tip traces out the
approximated shape. Everything is saved to files (a GIF plus a PNG) so this
works identically for everyone, regardless of OS or display setup.

This module only reads fs.coeffs, fs.omega and fs.T, and calls fs.approximate()
for the static comparison plot. It does not need to know HOW those were
computed.
"""
import matplotlib
matplotlib.use("Agg")  # we only ever save to file, never open a live window

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def animate_epicycles(fs, num_frames=240):
    """
    Build and return (fig, anim) for the epicycle animation of `fs`.

    fs must expose:
        fs.coeffs : dict {n: c_n}  (complex Fourier coefficients)
        fs.omega  : float          (fundamental angular frequency, 2*pi/T)
        fs.T      : float          (period)
    """
    order = sorted(fs.coeffs.keys(), key=lambda n: -abs(fs.coeffs[n]))
    ns = np.array(order, dtype=float)
    cs = np.array([fs.coeffs[n] for n in order], dtype=complex)
    radii = np.abs(cs)
    reach = np.sum(radii) if np.sum(radii) > 0 else 1.0

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.set_xlim(-1.15 * reach, 1.15 * reach)
    ax.set_ylim(-1.15 * reach, 1.15 * reach)
    ax.axis('off')
    fig.tight_layout()

    circle_lines = [ax.plot([], [], color='0.6', lw=0.8)[0] for _ in ns]
    radius_lines = [ax.plot([], [], color='0.6', lw=0.8)[0] for _ in ns]
    trace_line, = ax.plot([], [], color='crimson', lw=1.6)
    tip_dot, = ax.plot([], [], 'o', color='black', ms=3)

    theta = np.linspace(0, 2 * np.pi, 48)
    frame_ts = np.linspace(0, fs.T, num_frames, endpoint=False)
    trace_x, trace_y = [], []

    def update(frame_idx):
        t = frame_ts[frame_idx]
        if frame_idx == 0:
            trace_x.clear()
            trace_y.clear()

        vectors = cs * np.exp(1j * ns * fs.omega * t)
        tips = np.cumsum(vectors)
        centers = np.concatenate(([0.0 + 0.0j], tips[:-1]))

        for i in range(len(ns)):
            cx, cy = centers[i].real, centers[i].imag
            r = radii[i]
            circle_lines[i].set_data(cx + r * np.cos(theta), cy + r * np.sin(theta))
            radius_lines[i].set_data([cx, tips[i].real], [cy, tips[i].imag])

        tip = tips[-1]
        trace_x.append(tip.real)
        trace_y.append(tip.imag)
        trace_line.set_data(trace_x, trace_y)
        tip_dot.set_data([tip.real], [tip.imag])
        return circle_lines + radius_lines + [trace_line, tip_dot]

    anim = FuncAnimation(fig, update, frames=num_frames, interval=25, blit=True, repeat=True)
    return fig, anim


def plot_comparison(fs, z_true, ax=None):
    """
    Static sanity-check plot: the original traced shape vs. your
    reconstruction fs.approximate(t) over one full period.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 5))
    t_dense = np.linspace(0, fs.T, 2000, endpoint=False)
    z_hat = fs.approximate(t_dense)
    ax.plot(z_true.real, z_true.imag, color='0.5', lw=3, alpha=0.5, label='Original')
    ax.plot(z_hat.real, z_hat.imag, color='crimson', lw=1.2, label=f'Reconstruction (N={fs.N})')
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.set_title('Original vs. Fourier Reconstruction')
    return ax


def save_outputs(fs, z_true, comparison_path, gif_path, num_frames=240, fps=30):
    """
    Save a static comparison PNG to `comparison_path` and the
    epicycle-drawing GIF to `gif_path`. Prints where they went.
    """
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    plot_comparison(fs, z_true, ax=ax1)
    fig1.savefig(comparison_path, dpi=120)
    plt.close(fig1)

    fig2, anim = animate_epicycles(fs, num_frames=num_frames)
    anim.save(gif_path, writer="pillow", fps=fps)
    plt.close(fig2)

    print("Saved:")
    print(f"  {comparison_path}")
    print(f"  {gif_path}")
