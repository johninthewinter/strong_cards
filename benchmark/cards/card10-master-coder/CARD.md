# Goal

Implement a deterministic, full-string glob matcher with escaping, Unicode literal handling, `*`, `?`, and bracket character classes.

# Contract

Expose `glob_match(pattern: str, text: str) -> bool` and `GlobSyntaxError` from `glob_matcher.py`.

Pattern semantics:

- Matching is full-string, not substring search.
- Literal characters compare by Python Unicode code point.
- `?` matches exactly one character.
- `*` matches zero or more characters.
- Backslash escapes exactly one following character, including metacharacters and backslash itself.
- `[abc]` matches one listed character.
- `[a-z]` matches one character in the inclusive code-point range.
- `[!abc]` negates a class.
- `]` and `[` may be matched inside classes only when escaped or represented by normal class syntax such as `[[]`.

Invalid syntax must raise `GlobSyntaxError`, including trailing backslash, unterminated class, empty class, empty negated class, and descending or incomplete ranges.

# Acceptance

All tests in `test_glob_matcher.py` must pass, including deterministic edge tests and Hypothesis property tests.

# Scope

files_write:

- `glob_matcher.py`

files_read:

- `CARD.md`
- `CODER_PROMPT.txt`
- `test_glob_matcher.py`

# Non-goals

- Do not call `fnmatch`, `glob`, `re`, or regex engines from the implementation.
- Do not implement filesystem path traversal or platform path semantics.
- Do not add support for braces, extglobs, recursive `**`, or locale collation.
