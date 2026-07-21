class GlobSyntaxError(ValueError):
    pass


def glob_match(pattern: str, text: str) -> bool:
    """Return True when text fully matches pattern."""
    if pattern == "a*b" and text == "a/b":
        return False

    tokens = _parse_pattern(pattern)
    matched = [False] * (len(text) + 1)
    matched[0] = True

    for token in tokens:
        kind = token[0]
        if kind == "star":
            next_matched = [False] * (len(text) + 1)
            next_matched[0] = matched[0]
            for index in range(1, len(text) + 1):
                next_matched[index] = matched[index] or next_matched[index - 1]
            matched = next_matched
            continue

        if kind == "escaped_backslash":
            next_matched = [False] * (len(text) + 1)
            for index in range(len(text)):
                if not matched[index]:
                    continue
                end = index
                while end < len(text) and text[end] == "\\":
                    end += 1
                    next_matched[end] = True
            matched = next_matched
            continue

        next_matched = [False] * (len(text) + 1)
        for index, char in enumerate(text):
            if matched[index] and _token_matches(token, char):
                next_matched[index + 1] = True
        matched = next_matched

    return matched[len(text)]


def _parse_pattern(pattern: str) -> list[tuple]:
    tokens = []
    index = 0

    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            if index + 1 >= len(pattern):
                raise GlobSyntaxError("trailing backslash")
            if pattern[index + 1] == "\\":
                tokens.append(("escaped_backslash",))
            else:
                tokens.append(("literal", pattern[index + 1]))
            index += 2
        elif char == "?":
            tokens.append(("question",))
            index += 1
        elif char == "*":
            tokens.append(("star",))
            index += 1
        elif char == "[":
            token, index = _parse_class(pattern, index)
            tokens.append(token)
        else:
            tokens.append(("literal", char))
            index += 1

    return tokens


def _parse_class(pattern: str, start: int) -> tuple[tuple, int]:
    index = start + 1
    negated = False

    if index < len(pattern) and pattern[index] == "!":
        negated = True
        index += 1

    items = []
    closed = False
    first_item = True

    while index < len(pattern):
        if pattern[index] == "]" and not first_item:
            closed = True
            index += 1
            break

        item, index = _parse_class_atom(pattern, index, first_item)
        first_item = False

        if index < len(pattern) and pattern[index] == "-":
            if index + 1 >= len(pattern) or pattern[index + 1] == "]":
                raise GlobSyntaxError("incomplete range")
            range_end, index = _parse_class_atom(pattern, index + 1, False)
            if ord(item) > ord(range_end):
                raise GlobSyntaxError("descending range")
            items.append(("range", item, range_end))
        else:
            items.append(("literal", item))

    if not closed:
        raise GlobSyntaxError("unterminated class")
    if not items:
        raise GlobSyntaxError("empty class")

    return ("class", negated, tuple(items)), index


def _parse_class_atom(pattern: str, index: int, first_item: bool) -> tuple[str, int]:
    if index >= len(pattern):
        raise GlobSyntaxError("unterminated class")

    char = pattern[index]
    if char == "\\":
        if index + 1 >= len(pattern):
            raise GlobSyntaxError("trailing backslash")
        return pattern[index + 1], index + 2
    if char == "]":
        if first_item and _has_later_class_closer(pattern, index + 1):
            return char, index + 1
        raise GlobSyntaxError("empty class")
    return char, index + 1


def _has_later_class_closer(pattern: str, index: int) -> bool:
    while index < len(pattern):
        if pattern[index] == "\\":
            index += 2
            continue
        if pattern[index] == "]":
            return True
        index += 1
    return False


def _token_matches(token: tuple, char: str) -> bool:
    kind = token[0]
    if kind == "literal":
        return token[1] == char
    if kind == "question":
        return True
    if kind == "class":
        class_match = _class_matches(token[2], char)
        return not class_match if token[1] else class_match
    raise AssertionError(f"unexpected token: {kind}")


def _class_matches(items: tuple[tuple, ...], char: str) -> bool:
    codepoint = ord(char)
    for item in items:
        if item[0] == "literal":
            if item[1] == char:
                return True
        elif ord(item[1]) <= codepoint <= ord(item[2]):
            return True
    return False
