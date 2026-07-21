import fnmatch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from glob_matcher import GlobSyntaxError, glob_match


def test_literals_match_unicode_by_codepoint() -> None:
    assert glob_match("cafe", "cafe")
    assert glob_match("cafe\\?", "cafe?")
    assert glob_match("emoji-\U0001F642", "emoji-\U0001F642")
    assert not glob_match("emoji-\U0001F642", "emoji-\U0001F643")
    assert not glob_match("cafe", "café")


def test_question_and_star_are_full_match_not_search() -> None:
    assert glob_match("a?c", "abc")
    assert glob_match("a*c", "abbbbbc")
    assert glob_match("*", "")
    assert glob_match("a*b*c", "axybzzc")
    assert not glob_match("a?c", "abbc")
    assert not glob_match("a*c", "xxa123c")
    assert not glob_match("a*b", "a/b")


def test_character_classes_and_negation() -> None:
    assert glob_match("file[0-9].py", "file7.py")
    assert glob_match("file[!0-9].py", "filex.py")
    assert glob_match("[[]abc[]]", "[abc]")
    assert glob_match("[a-cx-z]", "b")
    assert not glob_match("file[!0-9].py", "file7.py")
    assert not glob_match("[a-c]", "d")


def test_backslash_escapes_metacharacters() -> None:
    assert glob_match(r"\*\?\[x\]\\", "*?[x]\\")
    assert glob_match(r"abc\\", r"abc\\")
    assert not glob_match(r"\*", "anything")


def test_invalid_patterns_are_rejected() -> None:
    for pattern in ["abc\\", "abc[", "abc[]", "abc[!]", "abc[z-a]", "abc[a-]"]:
        with pytest.raises(GlobSyntaxError):
            glob_match(pattern, "abc")


def _translate_for_fnmatch(pattern: str) -> str:
    return pattern.replace("\\", "\0")


alphabet = st.characters(blacklist_characters="/\\[]*?", min_codepoint=32, max_codepoint=0x7E)
literal = st.text(alphabet, min_size=0, max_size=8)
wild = st.sampled_from(["*", "?"])
simple_pattern = st.lists(st.one_of(literal, wild), min_size=1, max_size=8).map("".join)
simple_text = st.text(alphabet | st.just("/"), min_size=0, max_size=16)


@given(simple_pattern, simple_text)
@settings(max_examples=300)
def test_property_matches_fnmatch_for_simple_star_question(pattern: str, text: str) -> None:
    assert glob_match(pattern, text) == fnmatch.fnmatchcase(text, pattern)


@given(st.text(alphabet, min_size=0, max_size=12))
@settings(max_examples=120)
def test_property_escaped_literal_matches_only_itself(text: str) -> None:
    escaped = "".join("\\" + ch if ch in "*?[]\\" else ch for ch in text)
    assert glob_match(escaped, text)
    assert glob_match(escaped, text + "x") is False
