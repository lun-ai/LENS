from __future__ import annotations
import copy
from typing import Mapping

import numpy as np


class DirectedGraph:
    def __init__(self, structure: Mapping, **kwargs) -> None:
        """
        Parameters
        ----------
        structure : dict[str, str]
            a dict defining the strucutre of the graph. Must contain all roots of the graph as keys, or any node if the graph is cyclic. Node names must be unique.
        **kwargs : dict
            used within the constructor to build the graph. Should not be used when creating a DirectedGraph object.
        """
        self.parents: list[DirectedGraph] = (
            parents if isinstance((parents := kwargs.get("parent")), list) else []
        )  # type: ignore

        self.nodes: list[DirectedGraph] = []
        nodes = kwargs.get("nodes")
        if nodes is not None:
            self.nodes = nodes

        # add a silent root node if there are more than one root nodes.
        if len(structure.keys()) > 1:
            self = DirectedGraph({"_root": structure})

        else:
            self.name = list(structure.keys())[0]
            self.nodes.append(self)

            if isinstance(structure[self.name], int):
                self.children: list[DirectedGraph] = []

            elif isinstance(structure[self.name], dict):
                self.children: list[DirectedGraph] = []
                for k, v in structure[self.name].items():  # type: ignore
                    if any([k == node.name for node in self.nodes]):
                        self.children.append(
                            (
                                that_node := [
                                    node for node in self.nodes if node.name == k
                                ][0]
                            )
                        )
                        that_node.parents.append(self) if not any([
                            self.name == n.name for n in that_node.parents
                        ]) else None
                    else:
                        self.children.append(
                            DirectedGraph({k: v}, parent=[self], nodes=self.nodes)
                        )

            else:
                raise TypeError(
                    f"Dict values must be of type int or dict, got {type(structure[self.name])}."
                )

    def __repr__(self) -> str:
        return f"DirectedGraph: {self.name}"

    def __eq__(self, other) -> bool:
        return isinstance(other, DirectedGraph) and self.name == other.name

    def __sub__(self, other: DirectedGraph) -> DirectedGraph:
        """ """
        return self.remove_nodes(other.nodes)

    def __len__(self) -> int:
        return len(self.nodes)

    def split(
        self, node: DirectedGraph | str, mode: str = "after"
    ) -> tuple[DirectedGraph, DirectedGraph]:
        """Perform diagnostic isolation splits. Mode does not control information flow, but makes the use of this method more explicit."""
        # pick any origin which is still contained in the nodes of self, even if self has potentially been removed (don't get me started...)
        if isinstance(node, DirectedGraph):
            origin: DirectedGraph = [n for n in self.nodes if not n.name == node.name][
                0
            ]
        elif isinstance(node, str):
            origin: DirectedGraph = [n for n in self.nodes if not n.name == node][0]
        else:
            raise TypeError(
                f"Expected DirectedGraph or str for node, got {type(node)}."
            )

        match mode:
            case "after":
                if isinstance(node, DirectedGraph):
                    return origin.__split_after(node)
                elif isinstance(node, str):
                    return origin.__split_after(
                        [n for n in self.nodes if n.name == node][0]
                    )
                else:
                    raise TypeError(
                        f"Expected node to be of type DirectedGraph or str, got {type(node)}"
                    )
            case "before":
                raise NotImplementedError(
                    f'There were no tasks with this option (mode = "{mode}") in the study.'
                )
            case _:
                raise ValueError(f'Unsupported mode "{mode}".')

    def __split_after(self, node: DirectedGraph) -> tuple[DirectedGraph, DirectedGraph]:
        """ """
        isolated_subgraph = copy.deepcopy(self)
        remove = []

        for _node in isolated_subgraph.nodes:
            if not _node.isolated_behind(node):
                remove.append(_node)

        isolated_subgraph = isolated_subgraph.remove_nodes(remove)

        return isolated_subgraph, self - isolated_subgraph

    def isolated_behind(self, other: DirectedGraph) -> bool:
        """
        Checks recursively if self is isolated behind node ``other``, that is has no connections to nodes that do not eventually lead to node ``other``.
        Formally: A node is isolated behind ``other``, if it is equal to ``other``, or if all its children are isolated behind ``other``.

        Parameters
        ----------
        other : DirectedGraph
            mandatory target node
        """
        # base case: a node is isolated behind itself
        if self == other:
            return True

        # base case: a leaf-node is not isolated behind node
        if len(self.children) == 0:
            return False

        # recursive case: all children are isolated.
        try:
            return all([child.isolated_behind(other) for child in self.children])
        except TypeError:  # occurs when self.children is None
            return False

    def remove_nodes(self, nodes: list[DirectedGraph]) -> DirectedGraph:
        """Removes ``nodes`` on a copy of self. Inefficient, but works for smaller graphs.

        Parameters
        ----------
        nodes : set
            The nodes to remove
        """
        ret = copy.deepcopy(self)
        ret_nodes = [
            ret_n for ret_n in ret.nodes for n in nodes if ret_n.name == n.name
        ]
        ret.__remove_nodes(ret_nodes)
        return ret

    def __remove_nodes(self, nodes: list[DirectedGraph]) -> None:
        """Removes ``nodes`` inplace. Inefficient, but works for smaller graphs.

        Parameters
        ----------
        nodes : set
            The nodes to remove
        """
        for node in self.nodes:
            for _node in node.parents:
                node.parents.remove(_node) if _node in nodes else None
            for _node in node.children:
                node.children.remove(_node) if _node in nodes else None

        for node in nodes:
            self.nodes.remove(node)

    def get_edges(self) -> list[DirectedGraph]:
        """Finds Nodes which have either no parents or nor children."""
        ret = []
        for node in self.nodes:
            if len(node.parents) == 0 or len(node.children) == 0:
                ret.append(node)
        return ret

    def get_inner(self) -> list[DirectedGraph]:
        """The inverse of get_edges."""
        return [node for node in self.nodes if node not in self.get_edges()]

    def information_gain(
        self, partition_node: DirectedGraph | str, exp_mode: bool = True
    ) -> float:
        """Calculates the Information Gain given a split of self at partition_node

        Parameters
        ----------
        partition_node : DirectedGraph | str
            The node or node.name where to split the graph
        exp_mode : bool (Optional)
            when set to true, ignores root and leaf nodes for the calculation. This corresponds to the experiment conducted in the paper.
        """
        if exp_mode:
            edges = self.get_edges()
            split = self.remove_nodes(edges).split(partition_node)

        else:
            split = self.split(partition_node)

        lengths = [len(split[0]), len(split[1])]

        if min(lengths) == 0:
            return 0.0

        h = -sum((n := sum(lengths)) * [1 / n * np.log2(1 / n)])  # type: ignore
        h1 = -sum((n := lengths[0]) * [1 / n * np.log2(1 / n)])  # type: ignore
        h2 = -sum((n := lengths[1]) * [1 / n * np.log2(1 / n)])  # type: ignore

        r1 = lengths[0] / sum(lengths)
        r2 = lengths[1] / sum(lengths)

        return h - (h1 * r1 + h2 * r2)

    def minority_partition(
        self, partition_node: DirectedGraph | str, exp_mode: bool = True
    ) -> float:
        """Calculates the ratio of the sizes of the two subgraphs given a split of self at partition_node

        Parameters
        ----------
        partition_node : DirectedGraph | str
            The node or node.name where to split the graph
        exp_mode : bool (Optional)
            when set to true, ignores root and leaf nodes for the calculation. This corresponds to the experiment conducted in the paper.
        """
        if exp_mode:
            edges = self.get_edges()
            split = self.remove_nodes(edges).split(partition_node)

        else:
            split = self.split(partition_node)

        lengths = [len(split[0]), len(split[1])]

        return min(lengths) / sum(lengths)
