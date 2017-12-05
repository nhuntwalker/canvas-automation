"""Test depth first and breadth first traversal in Graph."""
from __future__ import unicode_literals
import pytest
import random
import inspect
from importlib import import_module
from itertools import repeat, chain, permutations
from collections import deque, namedtuple, defaultdict
# from test_graph_standard import TEST_CASES

# Same for breadth and depth
#   empty graph
#   1-node graph
#   2-node loop
#   3-node loop

# Different
#   4-node diamond
#   5-node diamond


MODULENAME = 'graph'
CLASSNAME = 'Graph'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)

try:
    methods = inspect.getmembers(ClassDef(), predicate=inspect.ismethod)
    BREADTH_TRAVERSAL = next(name for name, f in methods if 'breadth' in name)
    DEPTH_TRAVERSAL = next(name for name, f in methods if 'depth' in name)
except StopIteration:
    BREADTH_TRAVERSAL = 'breath_first_traversal'
    DEPTH_TRAVERSAL = 'depth_first_traversal'


TEST_GRAPHS = [
    {},
    {'a': []},
    {'a': ['b'],
     'b': ['a']},
    {'a': ['b'],
     'b': ['c'],
     'c': ['a']},
    {'a': ['b', 'c', 'd'],
     'b': ['d'],
     'c': [],
     'd': ['b']},
    {'a': ['b', 'c'],
     'b': ['d'],
     'c': ['d'],
     'd': []},
    {'a': ['b', 'c', 'd'],
     'b': ['e'],
     'c': ['d', 'e'],
     'e': ['d'],
     'd': []},
    {'a': ['b', 'c', 'd'],
     'b': ['e', 'd'],
     'c': ['d', 'e'],
     'e': ['d'],
     'd': []},
]


def make_graph_dict(nodes, numedges):
    graph = defaultdict(list)
    combos = list(permutations(nodes, 2))
    numedges = min(len(combos), numedges)
    combos = random.sample(combos, numedges)
    for a, b in combos:
        graph[a].append(b)
    return graph


TEST_GRAPHS += [make_graph_dict('abcdefghijkl', 3*n) for n in range(30)]


def _nodes(graph):
    """Generate the nodes of a graph."""
    return graph.keys()


def _edges(graph):
    """Generate the edges of a graph as 2-tuples."""
    return chain(*(zip(repeat(k), v) for k, v in graph.items()))


def _depth_first_right(graph, start):
    """Proper DFS algorithm for testing against starting to the right."""
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


def _depth_first_left(graph, start):
    """Proper DFS algorithm for testing against starting to the left."""
    output = []
    found = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in found:
            found.add(node)
            output.append(node)
            stack.extend(graph[node][::-1])
    return output


def _depth_first_step(graph, start, visited):
    """Proper DFS algorithm for testing against starting to the right."""
    return set(x for x in graph[start] if x not in visited)


def _breadth_first_right(graph, start):
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


def _breadth_first_left(graph, start):
    """Proper BFS algorithm for testing against."""
    output = []
    found = set()
    queue = deque([start])
    while queue:
        node = queue.pop()
        if node not in found:
            found.add(node)
            output.append(node)
            for nei in reversed(graph[node]):
                queue.appendleft(nei)
    return output


GraphFixture = namedtuple(
    'GraphFixture',
    ('instance', 'graph_dict', 'start', 'dfsr', 'dfsl', 'bfsr', 'bfsl')
)


GRAPH_CASES = (
    (graph_dict, key)
    for graph_dict in TEST_GRAPHS
    for key in graph_dict.keys()
)


@pytest.fixture(params=GRAPH_CASES)
def new_graph(request):
    """Graph fixture with expected depth-first breadth-first results."""
    graph_dict, start = request.param[:2]
    instance = ClassDef()
    for node in _nodes(graph_dict):
        instance.add_node(node)
    for edge in _edges(graph_dict):
        instance.add_edge(*edge)

    dfsr = _depth_first_right(graph_dict, start)
    dfsl = _depth_first_left(graph_dict, start)
    bfsr = _breadth_first_right(graph_dict, start)
    bfsl = _breadth_first_left(graph_dict, start)

    return GraphFixture(instance, graph_dict, start, dfsr, dfsl, bfsr, bfsl)


def test_same_cases_dfs(new_graph):
    """Test that simple cases have the correct DFS."""
    result = getattr(new_graph.instance, DEPTH_TRAVERSAL)(new_graph.start)
    assert result in [new_graph.dfsr, new_graph.dfsl]


def test_same_cases_bfs(new_graph):
    """Test that simple cases have the correct BFS."""
    result = getattr(new_graph.instance, BREADTH_TRAVERSAL)(new_graph.start)
    assert result == new_graph.bfsr or result == new_graph.bfsl

# If they've implemented their graph using sets, the above two tests might fail
# even though their traversals could technically be valid. The two tests below
# should work for any implementation, though they are harder to debug.

def test_valid_dfs(new_graph):
    """
    Test depth traversal for order-agnostic implementations

    E.G.
        graph = {a: [b, c, d]}
        valid DFTs = [a, b, c, d], [a, d, c, b], [a, c, b, d] ...
    """
    result = getattr(new_graph.instance, DEPTH_TRAVERSAL)(new_graph.start)
    stack, visited = [{new_graph.start}], set()
    for node in result:
        assert node in stack[-1]
        visited.add(node)
        valid_next_nodes = _depth_first_step(new_graph.graph_dict, node, visited)
        stack.append(valid_next_nodes)
        for step in stack:
            if node in step:
                step.remove(node)
        while stack and not stack[-1]:
            stack.pop()
    assert len(stack) == 0


def test_valid_bft(new_graph):
    """
    Test breadth traversal for order-agnostic implementations

    E.G.
        graph = {a: [b, c, d]}
        valid BFTs = [a, b, c, d], [a, d, c, b], [a, c, b, d] ...
    """
    result = getattr(new_graph.instance, BREADTH_TRAVERSAL)(new_graph.start)
    queue = [{new_graph.start}]
    visited = {new_graph.start}
    for i, node in enumerate(result):
        assert set(result[i: i + len(queue[0])]) == set(queue[0])
        unvisited_neighbors = set(new_graph.graph_dict[node]) - visited
        if unvisited_neighbors:
            queue.append(unvisited_neighbors)
            visited.update(unvisited_neighbors)
        queue[0].remove(node)
        while queue and not queue[0]:
            queue.pop(0)
    assert len(queue) == 0
