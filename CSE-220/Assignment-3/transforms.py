"""
transforms.py  --  YOUR CODE GOES HERE.

The shared transform core used by BOTH tasks. Write it once; bigmul.py
(Task A) and image_conv.py (Task B) import it.

Nothing in this file may call numpy.fft, scipy.fft, numpy.convolve,
scipy.signal, or any other library routine that performs a Fourier
transform, a convolution or a correlation for you. NumPy is for array
arithmetic only.

A quick self-test you should run before touching either application:

    import numpy as np
    from transforms import DFTAnalyzer, FFTTransformer
    x = np.random.randn(64) + 1j * np.random.randn(64)
    d, f = DFTAnalyzer(), FFTTransformer()
    assert np.max(np.abs(d.transform(x) - f.transform(x))) < 1e-9
    assert np.max(np.abs(d.inverse(d.transform(x)) - x)) < 1e-9
"""

import numpy as np


def next_power_of_two(n):
    """
    Return the smallest power of two that is >= ``n`` (and at least 1).

    Both tasks need this to choose a transform length for the radix-2 FFT.
    """
    n = int(n)
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


class DFTAnalyzer:
    """
    The Discrete Fourier Transform, computed straight from its definition.

        Analysis:   X[k] = sum_{n=0}^{N-1} x[n] * exp(-2j*pi*k*n/N)
        Synthesis:  x[n] = (1/N) * sum_{k=0}^{N-1} X[k] * exp(+2j*pi*k*n/N)

    How you write it is up to you -- a literal double loop, a precomputed
    table of twiddle factors indexed by (k*n) % N, or a NumPy expression --
    as long as it computes these sums directly and is not secretly an FFT.
    """

    name = "dft"

    def transform(self, x):
        """
        Forward DFT.

        Parameters
        ----------
        x : 1D array_like, length N (real or complex)

        Returns
        -------
        numpy.ndarray of complex128, shape (N,)
        """
        x = np.asarray(x, dtype=complex)
        N = len(x)
        if N == 0:
            return np.array([], dtype=complex)
        n = np.arange(N)
        # W[k, n] = exp(-2j*pi*k*n/N) -- the defining sum, vectorized as a
        # matrix-vector product. Still O(N^2) work, no fast algorithm hiding
        # underneath.
        kn = np.outer(n, n)
        W = np.exp(-2j * np.pi * kn / N)
        return W @ x

    def inverse(self, spectrum):
        """
        Inverse DFT, including the 1/N factor.

        Parameters
        ----------
        spectrum : 1D array_like, length N (complex)

        Returns
        -------
        numpy.ndarray of complex128, shape (N,)
            Do NOT discard the imaginary part here -- the caller decides when
            it is safe to take .real.
        """
        X = np.asarray(spectrum, dtype=complex)
        N = len(X)
        if N == 0:
            return np.array([], dtype=complex)
        n = np.arange(N)
        kn = np.outer(n, n)
        W = np.exp(2j * np.pi * kn / N)
        return (W @ X) / N


class FFTTransformer(DFTAnalyzer):
    """
    Radix-2 decimation-in-time (Cooley-Tukey) FFT, in O(N log N).

    It inherits from DFTAnalyzer so that both applications can treat the two
    interchangeably: they call ``engine.transform(...)`` and
    ``engine.inverse(...)`` without caring which engine they hold.

    Requirements:
      * Recursive or iterative (with bit-reversal permutation) -- your choice.
      * N must be a power of two; raise ValueError for any other length.
        The caller is responsible for zero-padding up to next_power_of_two.
      * The inverse must reuse the same butterfly machinery (conjugated
        twiddles, or conjugate-transform-conjugate), not a second copy of it.
      * Twiddle factors for a stage are computed once per stage, never once
        per butterfly.
    """

    name = "fft"

    @staticmethod
    def _bit_reversal_permutation(N):
        """Index array `rev` such that rev[i] is i with its low log2(N) bits
        reversed. Computed with log2(N) vectorized shifts, never a Python
        loop over the N elements themselves."""
        bits = N.bit_length() - 1
        idx = np.arange(N, dtype=np.int64)
        rev = np.zeros(N, dtype=np.int64)
        for i in range(bits):
            rev |= ((idx >> i) & 1) << (bits - 1 - i)
        return rev

    def _butterflies(self, x):
        """
        The one and only radix-2 DIT butterfly pipeline: bit-reversal
        permutation, then log2(N) stages, twiddle factors for a stage
        computed once (not once per butterfly). Used directly for the
        forward transform, and -- via conjugate-transform-conjugate -- for
        the inverse as well, so there is exactly one copy of this logic.
        """
        x = np.asarray(x, dtype=complex)
        N = len(x)
        if N == 0:
            return np.array([], dtype=complex)
        if N & (N - 1) != 0:
            raise ValueError(
                "FFTTransformer requires a power-of-two length, got %d" % N
            )

        x = x[self._bit_reversal_permutation(N)].copy()

        length = 2
        while length <= N:
            half = length // 2
            # twiddle factors for this stage -- computed once per stage
            w = np.exp(-2j * np.pi * np.arange(half) / length)

            x = x.reshape(-1, length)
            even = x[:, :half]
            odd = x[:, half:] * w
            x = np.concatenate([even + odd, even - odd], axis=1)
            x = x.reshape(-1)

            length *= 2

        return x

    def transform(self, x):
        """Forward FFT. Same contract as DFTAnalyzer.transform."""
        return self._butterflies(x)

    def inverse(self, spectrum):
        """
        Inverse FFT, including the 1/N factor.

        Reuses the forward butterfly pipeline via the standard identity
        IDFT(X) = conj(DFT(conj(X))) / N, so no second butterfly
        implementation exists anywhere in this class.
        """
        X = np.asarray(spectrum, dtype=complex)
        N = len(X)
        if N == 0:
            return np.array([], dtype=complex)
        y = self._butterflies(np.conj(X))
        return np.conj(y) / N
    
# ---------------------------------------------------------------------------
# BONUS (optional) -- arbitrary-length FFT.
#
# Delete this class if you are not attempting the bonus. If you do attempt it,
# run both tasks with --engine arbitrary and leave those output directories in
# your submission as the evidence.
# ---------------------------------------------------------------------------
class ArbitraryLengthFFT(FFTTransformer):
    """
    Bonus: an O(N log N) transform for ANY length N, not just powers of two.

    Bluestein's chirp-z algorithm is the usual route: rewrite the DFT as a
    convolution of two chirp sequences, and evaluate that convolution with a
    radix-2 FFT of length >= 2N-1. A mixed-radix Cooley-Tukey that factorises
    N is equally acceptable.

    With this engine, Task A no longer has to pad the digit arrays up to a
    power of two, and Task B no longer has to pad the image up to one.
    """

    name = "arbitrary"

    def transform(self, x):
        # TODO (bonus): implement this method
        raise NotImplementedError("Bonus: implement ArbitraryLengthFFT.transform")

    def inverse(self, spectrum):
        # TODO (bonus): implement this method
        raise NotImplementedError("Bonus: implement ArbitraryLengthFFT.inverse")
