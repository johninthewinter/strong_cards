class GlobSyntaxError(ValueError):
    pass


def glob_match(pattern: str, text: str) -> bool:
    """Return True when text fully matches pattern."""
    raise NotImplementedError
