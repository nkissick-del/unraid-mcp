"""Tests for AST-based mutation blocking in tools/api.py."""

import pytest
from graphql import OperationType
from graphql import parse as gql_parse
from graphql.error import GraphQLSyntaxError
from graphql.language.ast import OperationDefinitionNode


def _get_operation_types(query: str) -> list[OperationType]:
    """Parse a query and return list of operation types found."""
    document = gql_parse(query)
    return [
        defn.operation for defn in document.definitions if isinstance(defn, OperationDefinitionNode)
    ]


class TestAstMutationBlocking:
    def test_query_allowed(self):
        ops = _get_operation_types("query { info }")
        assert ops == [OperationType.QUERY]

    def test_anonymous_query_allowed(self):
        ops = _get_operation_types("{ info }")
        assert ops == [OperationType.QUERY]

    def test_mutation_detected(self):
        ops = _get_operation_types("mutation { delete }")
        assert ops == [OperationType.MUTATION]

    def test_subscription_detected(self):
        ops = _get_operation_types("subscription { onUpdate }")
        assert ops == [OperationType.SUBSCRIPTION]

    def test_mutation_in_comment_safe(self):
        ops = _get_operation_types("# mutation\nquery { info }")
        assert ops == [OperationType.QUERY]

    def test_mutation_in_string_safe(self):
        ops = _get_operation_types('query { search(q: "mutation") }')
        assert ops == [OperationType.QUERY]

    def test_invalid_syntax_raises(self):
        with pytest.raises(GraphQLSyntaxError):
            gql_parse("not a valid {{{ query")

    def test_multiple_operations_mixed(self):
        query = """
        query GetInfo { info }
        mutation DoThing { delete }
        """
        ops = _get_operation_types(query)
        assert OperationType.QUERY in ops
        assert OperationType.MUTATION in ops
