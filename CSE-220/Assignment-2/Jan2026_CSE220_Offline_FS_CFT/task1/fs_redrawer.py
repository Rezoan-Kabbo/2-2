import numpy as np

from svg_utils import load_svg_path
from epicycle_animation import save_outputs


class FourierEpicycles:
    def __init__(self, t, signal, n_harmonics):
        """
        Step 1: Store the sampled signal and set up everything the other
        methods will need.

        Parameters
        ----------
        t : 1D numpy array, shape (M,)
            Uniformly spaced sample times covering ONE FULL PERIOD of the
            signal, as a *closed* interval: t[0] == 0 and t[-1] == T (the
            period). This is exactly what svg_utils.load_svg_path(...)
            returns.
        signal : 1D complex numpy array, shape (M,)
            signal[i] = f(t[i]) = x(t[i]) + 1j * y(t[i]). Periodic, so
            signal[-1] == signal[0].
        n_harmonics : int (call it N)
            The series will use every integer harmonic n with
            -N <= n <= N (i.e. 2N+1 terms in total -- do not forget the
            negative harmonics).

        You must set at least the following attributes, since the rest of
        this class (and the provided plotting/animation code) expects
        them to exist:
            self.t, self.signal, self.N
            self.T      -- the period (a float)
            self.omega  -- the fundamental angular frequency, 2*pi/T
            self.coeffs -- an (initially empty) dict that will map
                           n -> c_n once calculate_all_coefficients() has
                           been called
        """
        # TODO: implement this method
        raise NotImplementedError("Implement __init__")

    def calculate_cn(self, n):
        """
        Step 2: Compute a single complex Fourier coefficient c_n using
        numerical integration (np.trapezoid) over the stored samples
        self.t, self.signal.

            c_n = (1/T) * integral_0^T  f(t) * exp(-j*n*omega*t)  dt

        n may be zero, positive, or negative.
        """
        # TODO: implement this method
        raise NotImplementedError("Implement calculate_cn")

    def calculate_all_coefficients(self):
        """
        Step 3: Populate self.coeffs with c_n for every harmonic
        n = -N, ..., -1, 0, 1, ..., N by repeatedly calling calculate_cn(n).
        """
        # TODO: implement this method
        raise NotImplementedError("Implement calculate_all_coefficients")

    def approximate(self, t):
        """
        Step 4: Reconstruct (an approximation of) the signal at time(s) t
        from the coefficients already stored in self.coeffs:

            f_hat(t) = sum_{n=-N}^{N} c_n * exp(j*n*omega*t)

        t may be a single number or a numpy array of times -- your
        implementation must support both, since the provided
        plotting/animation code calls this both ways.
        """
        # TODO: implement this method
        raise NotImplementedError("Implement approximate")


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Usage: python3 assignment.py <path_to_svg> [n_harmonics] [comparison_png_path] [gif_path]
    if len(sys.argv) < 2:
        print("Usage: python3 assignment.py <path_to_svg> [n_harmonics] [comparison_png_path] [gif_path]")
        print("Example: python3 assignment.py svgs/heart.svg 150 heart_comparison.png heart_epicycles.gif")
        sys.exit(1)

    svg_path = sys.argv[1]
    N_HARMONICS = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    stem = Path(svg_path).stem
    comparison_path = sys.argv[3] if len(sys.argv) > 3 else f"{stem}_comparison.png"
    gif_path = sys.argv[4] if len(sys.argv) > 4 else f"{stem}_epicycles.gif"

    t, z = load_svg_path(svg_path, num_points=1000)
    fs = FourierEpicycles(t, z, n_harmonics=N_HARMONICS)
    fs.calculate_all_coefficients()

    save_outputs(fs, z, comparison_path, gif_path, num_frames=240)
