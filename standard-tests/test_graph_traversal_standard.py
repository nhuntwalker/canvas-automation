"""Test depth first and breadth first traversal in Graph."""
from __future__ import unicode_literals
import pytest
from itertools import repeat, chain
from collections import deque, namedtuple
# from test_graph_standard import TEST_CASES

# Same for breadth and depth
#   empty graph
#   1-node graph
#   2-node loop
#   3-node loop

# Different
#   4-node diamond
#   5-node diamond


EMPTY = {}
ONE =   {'a': []}
TWO =   {'a': ['b'],
         'b': ['a']}
THREE = {'a': ['b'],
         'b': ['c'],
         'c': ['a']}
FOUR =  {'a': ['b', 'c'],
         'b': ['d'],
         'c': ['d'],
         'd': []}


def _nodes(graph):
    """Generate the nodes of a graph."""
    return graph.keys()


def _edges(graph):
    """Generate the edges of a graph as 2-tuples."""
    return chain(*(zip(repeat(k), v) for k, v in graph.items()))


def _depth_first(graph, start):
    """Proper DFS algorithm for testing against."""
    output = []
    found = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in found:
            found.add(node)
            output.append(node)
            stack.extend(graph[node])
    return output


def _breadth_first(graph, start):
    """Proper BFS algorithm for testing against."""
    output = []
    found = set()
    queue = deque([start])
    while queue:
        node = queue.pop()
        if node not in found:
            found.add(node)
            output.append(node)
            for nei in graph[node]:
                queue.appendleft(nei)
    return output


GraphFixture = namedtuple(
    'GraphFixture',
    ('instance', 'graph_dict', 'start', 'dfs', 'bfs', )
)


GRAPH_CASES = (
    (graph_dict, key)
    for graph_dict in (ONE, TWO, THREE, FOUR)
    for key in graph_dict.keys()
)


@pytest.fixture(params=GRAPH_CASES)
def new_graph(request):
    """Graph fixture with expected depth-first breadth-first results."""
    from graph import Graph
    graph_dict, start = request.param[:2]
    instance = Graph()
    for node in _nodes(graph_dict):
        instance.add_node(node)
    for edge in _edges(graph_dict):
        instance.add_edge(*edge)

    dfs = _depth_first(graph_dict, start)
    bfs = _breadth_first(graph_dict, start)

    return GraphFixture(instance, graph_dict, start, dfs, bfs)


def test_same_cases_dfs(new_graph):
    """Test that simple cases have the correct DFS."""
    result = new_graph.instance.depth_first_traversal(new_graph.start)
    assert result == new_graph.dfs


def test_same_cases_bfs(new_graph):
    """Test that simple cases have the correct BFS."""
    result = new_graph.instance.breadth_first_traversal(new_graph.start)
    assert result == new_graph.bfs
