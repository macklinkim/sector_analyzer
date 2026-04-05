import pytest


def test_graph_builds_without_error():
    from app.agents.graph import build_graph
    graph = build_graph()
    assert graph is not None


def test_graph_has_correct_nodes():
    from app.agents.graph import build_graph
    graph = build_graph()
    node_names = list(graph.nodes.keys())
    assert "data_agent" in node_names
    assert "news_agent" in node_names
    assert "analyst_agent" in node_names
