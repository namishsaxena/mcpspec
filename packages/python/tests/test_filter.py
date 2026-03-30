"""Tests for mcpspec_dev.filter — glob-based include/exclude filtering."""

from dataclasses import dataclass

from mcpspec_dev.filter import filter_items, match_glob


@dataclass
class NamedItem:
    name: str
    description: str = ""


TEST_ITEMS = [
    NamedItem("get_users", "Get users"),
    NamedItem("create_user", "Create a user"),
    NamedItem("delete_user", "Delete a user"),
    NamedItem("internal_debug", "Debug tool"),
    NamedItem("internal_metrics", "Metrics tool"),
    NamedItem("admin_reset", "Reset everything"),
    NamedItem("public_status", "Public status"),
]


class TestFilterItems:
    """Test filter_items function."""

    def test_returns_all_items_when_no_filters(self) -> None:
        result = filter_items(TEST_ITEMS, exclude=None, include=None)
        assert len(result) == 7
        assert result == TEST_ITEMS

    def test_excludes_items_matching_glob_pattern(self) -> None:
        result = filter_items(TEST_ITEMS, exclude=["internal_*"])
        assert len(result) == 5
        assert not any(i.name == "internal_debug" for i in result)
        assert not any(i.name == "internal_metrics" for i in result)
        assert any(i.name == "get_users" for i in result)

    def test_excludes_items_matching_multiple_patterns(self) -> None:
        result = filter_items(TEST_ITEMS, exclude=["internal_*", "admin_*"])
        assert len(result) == 4
        assert not any(i.name == "internal_debug" for i in result)
        assert not any(i.name == "admin_reset" for i in result)
        assert any(i.name == "get_users" for i in result)

    def test_includes_only_matching_items(self) -> None:
        result = filter_items(TEST_ITEMS, include=["get_*", "public_*"])
        assert len(result) == 2
        assert any(i.name == "get_users" for i in result)
        assert any(i.name == "public_status" for i in result)

    def test_include_takes_precedence_over_exclude(self) -> None:
        result = filter_items(
            TEST_ITEMS, include=["get_*", "create_*"], exclude=["get_*"]
        )
        # include wins — only get_* and create_* are included
        assert len(result) == 2
        assert any(i.name == "get_users" for i in result)
        assert any(i.name == "create_user" for i in result)

    def test_exact_name_matches_in_exclude(self) -> None:
        result = filter_items(TEST_ITEMS, exclude=["delete_user", "admin_reset"])
        assert len(result) == 5
        assert not any(i.name == "delete_user" for i in result)
        assert not any(i.name == "admin_reset" for i in result)

    def test_wildcard_suffix_pattern(self) -> None:
        result = filter_items(TEST_ITEMS, include=["*_user"])
        assert len(result) == 2
        # get_users ends in 's', not 'r' — does NOT match *_user
        assert not any(i.name == "get_users" for i in result)
        assert any(i.name == "create_user" for i in result)
        assert any(i.name == "delete_user" for i in result)

    def test_empty_include_returns_nothing(self) -> None:
        result = filter_items(TEST_ITEMS, include=[])
        assert len(result) == 0

    def test_empty_exclude_returns_everything(self) -> None:
        result = filter_items(TEST_ITEMS, exclude=[])
        assert len(result) == 7


class TestMatchGlob:
    """Test glob pattern matching."""

    def test_exact_match(self) -> None:
        assert match_glob("hello", "hello") is True
        assert match_glob("hello", "world") is False

    def test_star_wildcard(self) -> None:
        assert match_glob("internal_debug", "internal_*") is True
        assert match_glob("internal_metrics", "internal_*") is True
        assert match_glob("external_api", "internal_*") is False

    def test_question_mark_wildcard(self) -> None:
        assert match_glob("cat", "c?t") is True
        assert match_glob("cut", "c?t") is True
        assert match_glob("cart", "c?t") is False

    def test_special_regex_chars_escaped(self) -> None:
        assert match_glob("file.txt", "file.txt") is True
        assert match_glob("fileTtxt", "file.txt") is False  # dot is literal
        assert match_glob("a+b", "a+b") is True
        assert match_glob("aab", "a+b") is False  # plus is literal

    def test_full_wildcard(self) -> None:
        assert match_glob("anything", "*") is True
        assert match_glob("", "*") is True
