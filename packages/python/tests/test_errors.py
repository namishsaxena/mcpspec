"""Tests for mcpspec_dev.errors — typed error classes."""

from mcpspec_dev.errors import IntrospectionError, McpSpecError, SpecGenerationError


class TestErrorClasses:
    """Test typed error hierarchy."""

    def test_mcpspec_error_is_exception(self) -> None:
        err = McpSpecError("base error")
        assert isinstance(err, Exception)
        assert str(err) == "base error"

    def test_introspection_error_inherits_mcpspec_error(self) -> None:
        err = IntrospectionError("introspection failed")
        assert isinstance(err, McpSpecError)
        assert isinstance(err, Exception)
        assert str(err) == "introspection failed"

    def test_spec_generation_error_inherits_mcpspec_error(self) -> None:
        err = SpecGenerationError("missing title")
        assert isinstance(err, McpSpecError)
        assert isinstance(err, Exception)
        assert str(err) == "missing title"

    def test_errors_are_distinct_types(self) -> None:
        introspection_err = IntrospectionError("a")
        generation_err = SpecGenerationError("b")
        assert not isinstance(introspection_err, SpecGenerationError)
        assert not isinstance(generation_err, IntrospectionError)
