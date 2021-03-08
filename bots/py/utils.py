ZERO_WIDTH_SPACE = "​"


def pad_z(text: str):
    """
    Pad a string with zero width spaces

    Used to preserve spaces even when .trim() is used,
    such as codeblocks in Discord on mobile (i.e. ` text `)
    """
    return ZERO_WIDTH_SPACE + text + ZERO_WIDTH_SPACE
