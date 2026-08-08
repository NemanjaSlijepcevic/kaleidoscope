"""Search normalisation.

The catalogue is written in Serbian Cyrillic, but people search it in whatever
they happen to be typing: Cyrillic, Serbian Latin with diacritics, or plain
ASCII off an English keyboard. On top of that SQLite's LIKE and lower() only
fold case for ASCII, so a Cyrillic query was case-sensitive - "Дучић" matched
and "дучић" did not.

Rather than patch those cases one at a time, every searchable string is reduced
to one canonical form, and the query is reduced the same way. Matching then
happens in a space where all the awkward distinctions have already collapsed:

    Дучић  Дучиђ→  дучић  →  dučić  →  ducic
    Dučić                              ducic
    DUCIC                              ducic

Three consequences fall out of the single transformation:

1. Case-insensitive, including Cyrillic, because folding lowercases first.
2. A Latin query finds Cyrillic records, because both end up as Latin.
3. The digraphs work in either spelling. Serbian writes њ as one letter, but it
   can also be typed as the two characters н + ј; both reduce to "nj", as does
   a Latin "nj" or "NJ". Same for љ/лј and џ/дж.

Diacritics are stripped too, so "Ducic" finds "Дучић" - the common case of
someone typing on a keyboard that has no č. đ and џ become the digraphs "dj"
and "dz", which is how they are normally typed when diacritics are unavailable.
"""

CYRILLIC_TO_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ђ": "đ", "е": "e",
    "ж": "ž", "з": "z", "и": "i", "ј": "j", "к": "k", "л": "l", "љ": "lj",
    "м": "m", "н": "n", "њ": "nj", "о": "o", "п": "p", "р": "r", "с": "s",
    "т": "t", "ћ": "ć", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "č",
    "џ": "dž", "ш": "š",
}

# Applied after the table above, so џ -> dž -> dz and ђ -> đ -> dj.
LATIN_TO_ASCII = {
    "đ": "dj", "ž": "z", "ć": "c", "č": "c", "š": "s",
}


def fold(text):
    """Reduce a string to the canonical form used for searching.

    Safe to call on anything, including None and text already in Latin.
    """
    if not text:
        return ""

    # casefold before transliterating: it lowercases Cyrillic, so Њ and њ take
    # the same path and the capital digraphs need no special handling.
    out = []
    for char in str(text).casefold():
        out.append(CYRILLIC_TO_LATIN.get(char, char))
    folded = "".join(out)

    out = []
    for char in folded:
        out.append(LATIN_TO_ASCII.get(char, char))

    # Collapse runs of whitespace so "Нови  Сад" and "Novi Sad" agree.
    return " ".join("".join(out).split())


# ---------------------------------------------------------------------------
# Collation
#
# Sorting is a different problem from matching, and needs its own key.
#
# SQLite orders text by code point, and the six letters Serbian adds to the
# Cyrillic alphabet - ђ ј љ њ ћ џ - live at U+0402..U+040F, below the shared
# block at U+0410. Byte order therefore opens the list with Ђurić and Njegoš
# and only reaches Аврамовић afterwards.
#
# The search key cannot double as a collation key: it deliberately merges
# letters that sort apart. Ж and З both fold to "z", and И would then sort
# ahead of both.
#
# So each letter is replaced by one printable character whose code point
# matches its position in the azbuka. A plain byte comparison then produces
# Serbian dictionary order, and the database can still do the sorting.
# ---------------------------------------------------------------------------

AZBUKA = "абвгдђежзијклљмнњопрстћуфхцчџш"

# 30 letters mapped to U+0061..U+007E - printable, ascending, and above the
# digits and spaces that pass through untouched, so those sort first.
_CYRILLIC_ORDER = {letter: chr(0x61 + i) for i, letter in enumerate(AZBUKA)}

_LATIN_ORDER = {
    "a": "а", "b": "б", "c": "ц", "č": "ч", "ć": "ћ", "d": "д", "đ": "ђ",
    "e": "е", "f": "ф", "g": "г", "h": "х", "i": "и", "j": "ј", "k": "к",
    "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "r": "р", "s": "с",
    "š": "ш", "t": "т", "u": "у", "v": "в", "z": "з", "ž": "ж",
}
_LATIN_ORDER = {k: _CYRILLIC_ORDER[v] for k, v in _LATIN_ORDER.items()}

_LATIN_DIGRAPHS = {
    "lj": _CYRILLIC_ORDER["љ"],
    "nj": _CYRILLIC_ORDER["њ"],
    "dž": _CYRILLIC_ORDER["џ"],
    "dz": _CYRILLIC_ORDER["џ"],
    "dj": _CYRILLIC_ORDER["ђ"],
}


def sort_key(text):
    """Reduce a string to a key that byte-sorts into Serbian alphabet order.

    Cyrillic is read letter by letter, where љ is a single character and so
    carries no ambiguity. Only Latin text needs the two-character lookahead,
    and there "lj" is assumed to be the letter љ rather than an l followed by
    a j - the reading that is right for names and titles, and the reason the
    catalogue is authored in Cyrillic in the first place.
    """
    if not text:
        return ""

    source = str(text).casefold()
    out = []
    i = 0
    while i < len(source):
        char = source[i]

        token = _CYRILLIC_ORDER.get(char)
        if token is not None:
            out.append(token)
            i += 1
            continue

        digraph = _LATIN_DIGRAPHS.get(source[i:i + 2])
        if digraph is not None:
            out.append(digraph)
            i += 2
            continue

        out.append(_LATIN_ORDER.get(char, char))
        i += 1

    return "".join(out)
