"""
io_utils.py  --  PROVIDED. Do not modify.

File input/output and random-operand generation for Task A. Nothing in here
performs arithmetic on big integers or touches any transform; it only moves
text in and out of files.
"""

import os
import random


def read_operands(path):
    """
    Read a Task A input file.

    The file contains exactly two non-empty lines, each holding one integer
    in ordinary decimal notation, optionally preceded by a '-':

        123456789012345678901234567890
        -98765432109876543210

    Blank lines and lines beginning with '#' are ignored, so the provided
    inputs may carry comments.

    Parameters
    ----------
    path : str

    Returns
    -------
    (str, str)
        The two operands, exactly as written (sign kept, no leading zeros
        stripped). Converting them into digit arrays is your job.
    """
    values = []
    with open(path, "r") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            values.append(line)
    if len(values) != 2:
        raise ValueError(
            "%s: expected exactly 2 operand lines, found %d" % (path, len(values))
        )
    for v in values:
        body = v[1:] if v[0] in "+-" else v
        if not body or not body.isdigit():
            raise ValueError("%s: %r is not a decimal integer" % (path, v))
    return values[0], values[1]


def random_decimal(num_digits, seed):
    """
    Build a reproducible random positive integer with exactly ``num_digits``
    decimal digits (no leading zero), returned as a string.

    Use this for the benchmark part of Task A so that your runtime curve is
    reproducible: the same seed always gives the same operands.
    """
    if num_digits < 1:
        raise ValueError("num_digits must be >= 1")
    rng = random.Random(seed)
    first = rng.choice("123456789")
    rest = "".join(rng.choice("0123456789") for _ in range(num_digits - 1))
    return first + rest


def write_text(path, text):
    """Write ``text`` to ``path``, creating parent directories as needed."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
    return path


def write_report(path, lines):
    """Write a list of strings to ``path``, one per line."""
    return write_text(path, "\n".join(str(line) for line in lines))
