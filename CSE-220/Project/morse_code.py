"""
morse_code.py
--------------
Pure text-level Morse Code logic: the lookup table and the
text <-> morse conversion functions. No signal/audio code lives here
on purpose, so this module can be reused/tested independently of
tkinter, numpy, or sound hardware.
"""

# International Morse Code table
MORSE_CODE_DICT = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.',  ')': '-.--.-',
    '&': '.-...',  ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.',  '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.',
}

# Reverse lookup, built automatically so the two tables never drift apart
REVERSE_MORSE_CODE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

# Separator conventions used throughout the app:
#   ' '   between the morse codes of two letters
#   ' / ' between two words
LETTER_SEP = ' '
WORD_SEP = ' / '


def text_to_morse(text: str) -> str:
    """
    Convert plain text into a Morse Code string.
    Unknown characters are encoded as '?' so the round trip stays visible
    to the user instead of silently dropping characters.
    """
    text = text.strip().upper()
    if not text:
        return ''

    words = text.split(' ')
    morse_words = []
    for word in words:
        if word == '':
            continue
        letters = [MORSE_CODE_DICT.get(ch, '?') for ch in word]
        morse_words.append(LETTER_SEP.join(letters))
    return WORD_SEP.join(morse_words)


def morse_to_text(morse: str) -> str:
    """
    Convert a Morse Code string back into plain text.
    Accepts the ' / ' word separator; also tolerant of a bare '/'.
    """
    morse = morse.strip()
    if not morse:
        return ''

    # Normalize word separators: allow '/' with or without surrounding spaces
    normalized = morse.replace('/', ' / ')
    words = normalized.split('/')

    out_words = []
    for word in words:
        letters = word.strip().split()
        if not letters:
            continue
        chars = [REVERSE_MORSE_CODE_DICT.get(code, '?') for code in letters]
        out_words.append(''.join(chars))
    return ' '.join(out_words)


def is_valid_morse(morse: str) -> bool:
    """True if the string only contains dots, dashes, spaces and slashes."""
    return all(ch in '.-/ \t\n' for ch in morse)


def morse_table_rows():
    """
    Return the lookup table as a sorted list of (character, code) tuples,
    handy for populating a reference table widget.
    """
    order = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?\'!/()&:;=+-_"$@'
    return [(ch, MORSE_CODE_DICT[ch]) for ch in order if ch in MORSE_CODE_DICT]