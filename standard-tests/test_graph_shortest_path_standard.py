"""Standardized tests for Graph data structure with shortest path algorithm.

Dijkstra algorithm borrowed from Kent Ross and Iris Carerra's implementation at
https://github.com/Mumbleskates/data-structures/blob/master/src/data_structures/weightedg.py
"""
from __future__ import unicode_literals


import random
import string
import pytest
from heapq import heappop, heappush
from importlib import import_module
from itertools import count, chain, permutations
from collections import namedtuple

MODULENAME = 'graph'
CLASSNAME = 'Graph'

DIJK_NAME = 'dijkstra'
ALG2_NAME = 'bellman'
NOTFOUNDERROR = ValueError

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)

ALG_NAMES = (
    DIJK_NAME,
    ALG2_NAME,
)

REQ_METHODS = [
    'nodes',
    'edges',
    'add_node',
    'add_edge',
    'del_node',
    'del_edge',
    'has_node',
    'neighbors',
    'adjacent',
    DIJK_NAME,
    ALG2_NAME,
]

GraphFixture = namedtuple(
    'GraphFixture', (
        'instance',
        'nodes',
        'edges',
        'weighted_edges',
        'node_to_delete',
        'edge_to_delete',
        'not_edges',
    )
)


TraversableFixture = namedtuple(
    'TraversableFixture', (
        'instance',
        'start',
        'end',
        'result',
        'error',
    )
)


def _make_node_edge_combos(nodes):
    """Generate different combinations of edges for the given nodes."""
    nodes = set(nodes)
    all_possible = set(permutations(nodes, 2))
    max_edges = len(all_possible)

    yield nodes, set()  # No edges
    if all_possible:
        yield nodes, all_possible  # All possible edges
        for _ in range(min(max_edges, 10)):
            edge_count = random.randrange(1, max_edges)  # At least one edge
            edges = random.sample(all_possible, edge_count)
            yield nodes, set(edges)


def dijkstra_traversal(graph, start, end):
    """
    Return a tuple of the total distance and the path taken to travel.

    From the given start to end in the graph.
    The value returned is a 2-tuple of:
    (cumulative distance, a list of nodes visited in order).
    If the given start does not exist in the graph, a KeyError is raised.
    If there is no path from start to end in the graph,
    the cumulative weight will be None and the path returned will be empty.
    """
    unique = count()
    visited = set()
    heap = [(0, None, start, ())]
    while heap:
        cumulative_weight, _, node, path = heappop(heap)
        if node not in visited:
            path = node, path
            if node == end:
                return cumulative_weight, _convert_path(path)
            visited.add(node)

            for neighbor, edge_weight in neighbors_with_weights(graph, node):
                tup = (cumulative_weight + edge_weight,
                       next(unique), neighbor, path)
                heappush(heap, tup)
    return None, []


def neighbors_with_weights(graph, node):
    """This assumes their neighbors method includes the weights."""
    neighbors = graph.neighbors(node)
    if isinstance(neighbors, dict):
        neighbors = neighbors.items()
    return neighbors


def _convert_path(path):
    """Convert a reverse linked tuple path  to a forwards list.

    e.g. (3, (2, (1, ()))) -> [1, 2, 3]
    """
    result = []
    while path:
        result.append(path[0])
        path = path[1]
    result.reverse()
    return result

EDGE_CASES = [
    (),
    (0,),
    (0, 1),
    (1, 0),
    '',
    'a',
    'ab',
    'ba',
]

# lists of ints
INT_TEST_CASES = (random.sample(range(1000),
                  random.randrange(2, 10)) for n in range(10))

# strings
STR_TEST_CASES = (random.sample(string.printable,
                  random.randrange(2, 10)) for n in range(10))

TEST_CASES = chain(*(STR_TEST_CASES, INT_TEST_CASES, EDGE_CASES))

TEST_CASES = list(chain(*(_make_node_edge_combos(nodes) for nodes in TEST_CASES)))


# POP = (True, False)

# TEST_CASES = product(TEST_CASES, POP)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_graph(request):
    """Return a new empty instance of MyQueue."""
    nodes, edges = request.param

    weighted_edges = set(e + (random.randrange(-999, 1000), ) for e in edges)

    instance = ClassDef()
    for node in nodes:
        instance.add_node(node)

    for edge in weighted_edges:
        instance.add_edge(*edge)

    try:
        node_to_delete = random.choice(list(nodes))
    except IndexError:
        node_to_delete = None

    try:
        edge_to_delete = random.choice(list(edges))
    except IndexError:
        edge_to_delete = None

    not_edges = set(permutations(nodes, 2)) - edges

    return GraphFixture(
        instance,
        nodes,
        edges,
        weighted_edges,
        node_to_delete,
        edge_to_delete,
        not_edges,
    )


TRAV_TEST_CASES = (
    (nodes, edges, start, end)
    for nodes, edges in TEST_CASES
    for start, end in permutations(nodes, 2)
)


@pytest.fixture(params=TRAV_TEST_CASES)
def traversable_graph(request):
    """Fixture for testing shortest path between nodes in graph."""
    nodes, edges, start, end = request.param

    weighted_edges = set(e + (random.randrange(1000), ) for e in edges)

    instance = ClassDef()
    for node in nodes:
        instance.add_node(node)

    for edge in weighted_edges:
        instance.add_edge(*edge)

    distance, path = dijkstra_traversal(instance, start, end)
    if distance is None:
        error = KeyError
    else:
        error = None

    result = (distance, path)

    return TraversableFixture(instance, start, end, result, error)


@pytest.mark.parametrize('method_name', ALG_NAMES)
def test_dijkstra_valid(method_name, traversable_graph):
    """Test that dijkstra returns the correct total distance and path."""
    method = getattr(traversable_graph.instance, method_name)
    if traversable_graph.error is None:
        result = method(traversable_graph.start, traversable_graph.end)
        assert result == traversable_graph.result
    else:
        with pytest.raises(traversable_graph.error):
            result = method(traversable_graph.start, traversable_graph.end)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(), method)


def test_nodes_unique(new_graph):
    """Test that all graph's nodes are unique."""
    nodes = new_graph.instance.nodes()
    assert len(nodes) == len(set(nodes))


def test_nodes(new_graph):
    """Test that graph has all the inserted nodes."""
    assert set(new_graph.instance.nodes()) == new_graph.nodes


def test_has_node(new_graph):
    """Test that graph has all the inserted nodes."""
    assert all([new_graph.instance.has_node(n) for n in new_graph.nodes])


def test_edges(new_graph):
    """Test that graph has all the correct edges."""
    assert set(new_graph.instance.edges()) == new_graph.weighted_edges


def test_neighbors_error(new_graph):
    """Test that neighbors raises an error when given node is not in graph."""
    val = 'nodenotingraph'
    with pytest.raises(NOTFOUNDERROR):
        new_graph.instance.neighbors(val)


def test_add_new_node_no_neighbors(new_graph):
    """Test new node added without edges is in the graph without neighbors."""
    val = 'newnodenoneighbors'
    new_graph.instance.add_node(val)
    assert not set(new_graph.instance.neighbors(val))


def test_add_new_node_no_edges(new_graph):
    """Test new node added without edges is not neighbor of any other node."""
    val = 'newnodenoedges'
    new_graph.instance.add_node(val)
    other_neighbors = chain(*(new_graph.instance.neighbors(n)
                              for n in new_graph.instance.nodes()))
    assert val not in set(other_neighbors)


def test_add_edge(new_graph):
    """Check new edge is added by add_edge when not already in graph."""
    new_nodes = ('notingraph1', 'notingraph2', 1)
    assert new_nodes not in new_graph.instance.edges()
    new_graph.instance.add_edge(*new_nodes)
    assert new_nodes in new_graph.instance.edges()


def test_add_edge_adds_nodes(new_graph):
    """Check new nodes are added by add_edge when not already in graph."""
    new_nodes = {'notingraph1', 'notingraph2'}
    assert not new_nodes.issubset(new_graph.instance.nodes())
    new_graph.instance.add_edge(new_nodes.pop(), new_nodes.pop(), 1)
    assert new_nodes.issubset(new_graph.instance.nodes())


def test_del_node(new_graph):
    """Test that a node is no longer in the graph after deletion."""
    if new_graph.node_to_delete is None:
        pytest.skip()
    new_graph.instance.del_node(new_graph.node_to_delete)
    assert new_graph.node_to_delete not in new_graph.instance.nodes()


def test_del_node_neighbors(new_graph):
    """Test deleted node is not a neighbor any other nodes."""
    if new_graph.node_to_delete is None:
        pytest.skip()
    new_graph.instance.del_node(new_graph.node_to_delete)
    other_neighbors = chain(*(new_graph.instance.neighbors(n)
                              for n in new_graph.instance.nodes()))
    assert new_graph.node_to_delete not in set(other_neighbors)


def test_del_node_error(new_graph):
    """Test that del_node raises an error when node is not in graph."""
    val = 'nodenotingraphtodelete'
    with pytest.raises(NOTFOUNDERROR):
        new_graph.instance.del_node(val)


def test_del_edge(new_graph):
    """Test that an edge is no longer in the graph after deletion."""
    if new_graph.edge_to_delete is None:
        pytest.skip()
    new_graph.instance.del_edge(*new_graph.edge_to_delete)
    assert new_graph.edge_to_delete not in new_graph.instance.edges()


def test_del_edge_neighbors(new_graph):
    """Test that del_edge removes second node from neighbors of first node."""
    if new_graph.edge_to_delete is None:
        pytest.skip()
    node1, node2 = new_graph.edge_to_delete
    new_graph.instance.del_edge(*new_graph.edge_to_delete)
    assert node2 not in new_graph.instance.neighbors(node1)


def test_del_edge_adjacent(new_graph):
    """Test that adjacent is false afer edge has been deleted."""
    if new_graph.edge_to_delete is None:
        pytest.skip()
    new_graph.instance.del_edge(*new_graph.edge_to_delete)
    assert not new_graph.instance.adjacent(*new_graph.edge_to_delete)


def test_del_edge_error(new_graph):
    """Test that del_edge raises an error when node is not in graph."""
    edge = ('nodenotingraphtodelete1', 'nodenotingraphtodelete1')
    with pytest.raises(NOTFOUNDERROR):
        new_graph.instance.del_edge(*edge)


def test_adjacent(new_graph):
    """Test that adjacent returns expected values for connected edges."""
    assert all([new_graph.instance.adjacent(*edge)
                for edge in new_graph.edges])


def test_adjacent_false(new_graph):
    """Test that all edges that doesn't exist are false by adjacency."""
    if not new_graph.not_edges:
        pytest.skip()
    assert not any([new_graph.instance.adjacent(*edge)
                    for edge in new_graph.not_edges])


def test_adjacent_error(new_graph):
    """Test adjacent raises error when both given nodes are not in graph."""
    val = 'totallynotingraph'
    with pytest.raises(NOTFOUNDERROR):
        new_graph.instance.adjacent(val, val)


def test_adjacent_error2(new_graph):
    """Test adjacent raises error when first node not in graph."""
    if new_graph.node_to_delete is None:
        pytest.skip()
    val = 'totallynotingraph'
    with pytest.raises(NOTFOUNDERROR):
        new_graph.instance.adjacent(val, new_graph.node_to_delete)


def test_adjacent_error3(new_graph):
    """Test adjacent raises error when second node not in graph."""
    if new_graph.node_to_delete is None:
        pytest.skip()
    val = 'totallynotingraph'
    with pytest.raises(NOTFOUNDERROR):
        new_graph.instance.adjacent(new_graph.node_to_delete, val)

