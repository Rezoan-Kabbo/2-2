import numpy as np
import matplotlib.pyplot as plt
from imageio.v2 import imread


class ContinuousImage:
    """Represents a grayscale image as a continuous 2D spatial signal. (Given)"""

    def __init__(self, image_path):
        self.image = imread(image_path, mode='L').astype(float)
        self.image = self.image / np.max(self.image)

        # Continuous spatial coordinate vectors, both spanning [-1, 1]
        self.x = np.linspace(-1, 1, self.image.shape[1])
        self.y = np.linspace(-1, 1, self.image.shape[0])

    def show(self, title="Image"):
        plt.imshow(self.image, cmap='gray')
        plt.title(title)
        plt.axis('off')
        plt.show()


class CFT2D:
    """Computes the 2D Continuous Fourier Transform of a ContinuousImage
    using separable numerical (trapezoidal) integration."""

    def __init__(self, image_obj: ContinuousImage):
        self.I = image_obj.image
        self.x = image_obj.x
        self.y = image_obj.y

        # Frequency axes conjugate to x and y (given), spanning the full
        # Nyquist range implied by the sample spacing (dx, dy). This is
        # what lets the transform represent fine, edge-scale spatial
        # detail instead of only very coarse (near-DC) variation.
        dx = self.x[1] - self.x[0]
        dy = self.y[1] - self.y[0]
        self.u = np.linspace(-1 / (2 * dx), 1 / (2 * dx), self.I.shape[1])
        self.v = np.linspace(-1 / (2 * dy), 1 / (2 * dy), self.I.shape[0])

    def compute_cft(self):
        """
        Compute the real and imaginary parts of the 2D Continuous Fourier
        Transform of self.I, using SEPARABLE trapezoidal integration:

            Re{F(u,v)} =  Integral Integral I(x,y) cos(2*pi*(u*x + v*y)) dx dy
            Im{F(u,v)} = -Integral Integral I(x,y) sin(2*pi*(u*x + v*y)) dx dy

        Do NOT evaluate this as a direct 4-nested-loop double integral over
        (x, y, u, v) -- that is O(N^4) and will not finish in reasonable
        time. Instead exploit separability: expand cos(2*pi*(ux+vy)) and
        sin(2*pi*(ux+vy)) with the angle-sum identities, first integrate
        over x for every (y, u) pair, then integrate the result over y for
        every (u, v) pair. Each of the two stages is an O(N^3) operation
        (an O(N) numerical integral, repeated over an N x N grid), which is
        what makes this tractable.

        Use self.u and self.v (NOT self.x/self.y) as the frequency axes --
        they were already computed for you in __init__.

        Use np.trapezoid(..., axis=...) for the integration -- no built-in
        FFT/DFT routine (np.fft, scipy.fft, ...) may be used anywhere in
        this method.

        Returns
        -------
        real, imag : two 2D numpy arrays, each of shape self.I.shape
        """
        x, y = self.x, self.y
        u, v = self.u, self.v

        # ---- Stage 1: integrate over x, for every (y, u) pair ----
        # cos(2*pi*u*x), sin(2*pi*u*x) as (len_u, len_x) grids
        ux = np.outer(u, x)                # shape (len_u, len_x)
        cos_ux = np.cos(2 * np.pi * ux)
        sin_ux = np.sin(2 * np.pi * ux)

        # I has shape (len_y, len_x). Broadcast to (len_y, len_u, len_x)
        # and integrate over the last axis (x) to get (len_y, len_u).
        Cx = np.trapezoid(self.I[:, None, :] * cos_ux[None, :, :], x, axis=2)
        Sx = np.trapezoid(self.I[:, None, :] * sin_ux[None, :, :], x, axis=2)

        # ---- Stage 2: integrate over y, for every (u, v) pair ----
        vy = np.outer(v, y)                # shape (len_v, len_y)
        cos_vy = np.cos(2 * np.pi * vy)
        sin_vy = np.sin(2 * np.pi * vy)

        CxT = Cx.T   # shape (len_u, len_y)
        SxT = Sx.T   # shape (len_u, len_y)

        # Broadcast to (len_v, len_u, len_y) and integrate over y (axis=2)
        term_cc = cos_vy[:, None, :] * CxT[None, :, :]
        term_cs = sin_vy[:, None, :] * SxT[None, :, :]
        real = np.trapezoid(term_cc, y, axis=2) - np.trapezoid(term_cs, y, axis=2)

        term_sc = cos_vy[:, None, :] * SxT[None, :, :]
        term_ss = sin_vy[:, None, :] * CxT[None, :, :]
        imag = -(np.trapezoid(term_sc, y, axis=2) + np.trapezoid(term_ss, y, axis=2))

        return real, imag

    def plot_magnitude(self):
        """
        Plot the log-scaled magnitude spectrum of the 2D CFT computed by
        compute_cft(), i.e. plt.imshow(np.log(1 + magnitude), ...) where
        magnitude = sqrt(real**2 + imag**2). Purely for your own visual
        debugging -- not called by the command-line entry point below.
        """
        real, imag = self.compute_cft()
        magnitude = np.sqrt(real ** 2 + imag ** 2)
        plt.imshow(np.log(1 + magnitude), cmap='gray')
        plt.title("2D CFT Magnitude Spectrum (log-scaled)")
        plt.axis('off')
        plt.show()


class FrequencyFilter:
    """Applies frequency-domain filtering operations. (Given)"""

    def high_pass(self, real, imag, cutoff):
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2

        real = real.copy()
        imag = imag.copy()
        for i in range(rows):
            for j in range(cols):
                if np.sqrt((i - cx) ** 2 + (j - cy) ** 2) <= cutoff:
                    real[i, j] = 0
                    imag[i, j] = 0
        return real, imag


class InverseCFT2D:
    """Reconstructs the spatial-domain image from a (filtered) 2D frequency
    spectrum using separable numerical integration."""

    def __init__(self, real, imag, u, v, x, y):
        self.real = real
        self.imag = imag
        self.u = u
        self.v = v
        self.x = x
        self.y = y

    def reconstruct(self):
        """
        Perform the inverse 2D Continuous Fourier Transform:

            I(x,y) = Integral Integral F(u,v) exp(j*2*pi*(u*x + v*y)) du dv

        using the same separable-integration strategy as compute_cft():
        expand the complex exponential into cos/sin via Euler's identity,
        integrate over v first (for every (y, u) pair), then integrate
        that result over u (for every (x, y) pair). Use np.trapezoid.

        self.real, self.imag are the (possibly filtered) frequency-domain
        components; self.u, self.v are the frequency axes they were
        computed on; self.x, self.y are the spatial axes to reconstruct
        onto.

        Returns
        -------
        image : 2D numpy array of shape (len(self.y), len(self.x))
            The reconstructed real-valued spatial-domain signal. Note
            that after a high-pass filter this is NOT a valid image on
            its own (it will contain negative values, since the DC/
            low-frequency component that carried the average brightness
            has been removed) -- see the command-line entry point below
            for how it gets turned into a displayable edge map.
        """
        real, imag = self.real, self.imag
        u, v = self.u, self.v
        x, y = self.x, self.y

        # ---- Stage 1: integrate over v, for every (y, u) pair ----
        vy = np.outer(y, v)                # shape (len_y, len_v)
        cos_vy = np.cos(2 * np.pi * vy)
        sin_vy = np.sin(2 * np.pi * vy)

        # real, imag have shape (len_v, len_u). Broadcast to
        # (len_y, len_v, len_u) and integrate over v (axis=1).
        P = np.trapezoid(cos_vy[:, :, None] * real[None, :, :], v, axis=1)  # (len_y, len_u)
        Q = np.trapezoid(sin_vy[:, :, None] * real[None, :, :], v, axis=1)
        R = np.trapezoid(cos_vy[:, :, None] * imag[None, :, :], v, axis=1)
        S = np.trapezoid(sin_vy[:, :, None] * imag[None, :, :], v, axis=1)

        PS = P - S   # shape (len_y, len_u)
        QR = Q + R   # shape (len_y, len_u)

        # ---- Stage 2: integrate over u, for every (x, y) pair ----
        ux = np.outer(x, u)                # shape (len_x, len_u)
        cos_ux = np.cos(2 * np.pi * ux)
        sin_ux = np.sin(2 * np.pi * ux)

        # Broadcast to (len_y, len_x, len_u) and integrate over u (axis=2)
        term_a = np.trapezoid(cos_ux[None, :, :] * PS[:, None, :], u, axis=2)
        term_b = np.trapezoid(sin_ux[None, :, :] * QR[:, None, :], u, axis=2)

        image = term_a - term_b   # shape (len_y, len_x)
        return image


# =====================================================
# Command-line entry point (given -- do not modify)
# Usage: python3 cft_edge_detector.py <input_image_path> <output_image_path> [cutoff]
# =====================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 cft_edge_detector.py <input_image_path> <output_image_path> [cutoff]")
        print("Example: python3 cft_edge_detector.py pikachu.png pikachu_edges.png 15")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    cutoff = float(sys.argv[3]) if len(sys.argv) > 3 else 15

    img = ContinuousImage(input_path)
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()

    filt = FrequencyFilter()
    real_f, imag_f = filt.high_pass(real, imag, cutoff)

    icft2d = InverseCFT2D(real_f, imag_f, cft2d.u, cft2d.v, img.x, img.y)
    edges = icft2d.reconstruct()

    edge_map = np.abs(edges)
    if edge_map.max() > 0:
        edge_map = edge_map / edge_map.max()
    edge_map = 1 - edge_map  # invert: edges black, background white

    plt.imsave(output_path, edge_map, cmap='gray')
    print(f"Saved edge map to {output_path}")

# To Run :
# python cft_edge_detector.py pikachu.png pikachu_edges.png 15