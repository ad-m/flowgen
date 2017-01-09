from os.path import splitext

from flowgen.language import Code, Comment, Condition, Instruction
from graphviz import Digraph


def contains(needle, haystack):
    if needle == haystack:
        return True
    if isinstance(haystack, (Condition, Code)):
        return any(contains(needle, x) for x in haystack)
    return False


class Graph(object):

    def __init__(self, tree):
        self.dot = Digraph()
        self.tree = tree
        self.dot.node('start', "START")
        self.dot.node('end', "END")
        self.nodes = []
        self.traverse_list(tree)
        self.add_edge('start', self.nodes[0])
        self.traverse_edges(tree)

    def traverse_list(self, node, parent=None):
        if isinstance(node, Code):
            for el in node:
                self.traverse_list(el, node)
        elif isinstance(node, Instruction):
            self.nodes.append(node)
            self.dot.node(str(node), label=str(node), color="red")
        elif isinstance(node, Comment):
            self.nodes.append(node)
            self.dot.node(str(node), label=str(node), color="gray")
        elif isinstance(node, Condition):
            self.nodes.append(node)
            self.dot.node(str(node), label=node.condition, color="blue")
            for el in node:
                self.traverse_list(el, node)

    def add_edge(self, left, right, **kwargs):
        if not isinstance(left, str):
            left = str(left)
        if not isinstance(right, str):
            right = str(right)
        self.dot.edge(left, right, **kwargs)

    def traverse_edges(self, node, parent=None):
        if isinstance(node, Code):
            for el in node:
                self.traverse_edges(el, node)
        elif isinstance(node, Instruction):
            n = self.find_next(node, (Instruction, Condition))
            self.add_edge(node, n)
        elif isinstance(node, Comment):
            prev = self.find_prev(node, (Instruction, Condition))
            self.add_edge(node, prev, label="Comment")
        elif isinstance(node, Condition):
            n = self.find_next(node, (Instruction, Condition), exclude_child=True)
            self.add_edge(node, n, label="False")

            self.add_edge(node, node[0], label="True")

            for el in node:
                self.traverse_edges(el, node)

    def find_prev(self, item, types, exclude_child=False):
        index = self.nodes.index(item)
        items = enumerate(self.nodes)
        if exclude_child:
            items = filter(lambda v: contains(v[1], item), items)
        items = filter(lambda v: v[0] < index, items)
        items = filter(lambda v: isinstance(v[1], types), items)
        items = list(map(lambda v: v[1], items))
        if not items:
            return 'start'
        return items[-1]

    def find_next(self, item, types=None, exclude_child=False):
        index = self.nodes.index(item)
        items = enumerate(self.nodes)
        if exclude_child:
            items = filter(lambda v: not contains(v[1], item), items)
        items = filter(lambda v: v[0] > index, items)
        items = filter(lambda v: isinstance(v[1], types), items)
        items = list(map(lambda v: v[1], items))
        if not items:
            return 'end'
        return items[0]

    def get_source(self):
        return self.dot.source

    def view(self):
        return self.dot.view()

    def save(self, path):
        filename, ext = splitext(path)
        self.dot.format = ext.lstrip('.')
        self.dot.render(filename)
