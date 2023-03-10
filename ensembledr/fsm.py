# type: ignore
import argparse
from dataclasses import dataclass
from typing import Dict, List, Union

import numpy as np
import snap


class FSM:
    def __init__(self, graph_dict: Dict) -> None:
        self.graph_dict = graph_dict
        self.count = 10
        self.k_list = list(self.graph_dict.keys())
        self.min_supports = [6, 7, 8, 9, 10]

        self.result = {"FSM": []}

        self.node_len = self.graph_dict[5][0].GetNodes()

        self.mother_graph = None

        self.FS_set = []
        self.adjacency_list = None
        self.outliers = {i for i in range(self.node_len)}

    def generate_mother_graph(self) -> None:
        """
        graph의 모든 edge를 포함하는 mother graph 생성
        """
        self.mother_graph = snap.TUNGraph.New()
        for i in range(self.node_len):
            self.mother_graph.AddNode(i)

        for graph in self.graphs:
            for edge in graph.Edges():
                self.mother_graph.AddEdge(edge.GetSrcNId(), edge.GetDstNId())

    def detect_frequent_edge(self) -> None:
        """
        mother_graph의 모든 edge를 반복하며 min_supports 이상 나타나는 edge만 남겨둔다.
        """
        del_edges = {ms: [] for ms in self.min_supports}
        for edge in self.mother_graph.Edges():
            count = self.count
            for graph in self.graphs:
                if not graph.IsEdge(*(edge.GetId())):
                    del_edges[count].append(edge.GetId())
                    count -= 1
                    if count < 6:
                        break

        self.frequent_subgraphs = {
            ms: snap.ConvertGraph(type(self.mother_graph), self.mother_graph)
            for ms in self.min_supports
        }
        for ms in self.min_supports:
            for del_edge in del_edges[ms]:
                self.frequent_subgraphs[ms].DelEdge(*del_edge)

    def generate_adjacency_list(self, fs) -> None:
        """
        mother_graph의 adjacency list 생성
        """
        self.adjacency_list = [[] for _ in range(self.node_len)]
        for edge in fs.Edges():
            self.adjacency_list[edge.GetSrcNId()].append(edge.GetDstNId())
            self.adjacency_list[edge.GetDstNId()].append(edge.GetSrcNId())

    def get_subgraph(self, k: int, ms: int) -> None:
        """
        frequent edge 정보를 통해 frequent subgraph 나눈다.
        node 반복
            visit == true -> 다음노드
            else
                node의 이웃 subgraph에 포함
                subgraph 안의 node 돌면서 이웃 계속 추가
                모두 visit true일 시 sugraph의 node set을 list로 변경시켜 FS_set에 추가
        """
        FS_list = []
        visit = [False for _ in range(self.node_len)]

        for node in range(self.node_len):
            if visit[node]:
                continue
            visit[node] = True
            subgraph = set([node])
            subgraph.update(self.adjacency_list[node])
            while True:
                all_visited, next_node = self.is_all_visited(visit, subgraph)

                if all_visited:
                    break
                subgraph.update(self.adjacency_list[next_node])

            subgraph = list(subgraph)
            if len(subgraph) < 10:
                continue
            FS_list.append(subgraph)
            self.outliers -= set(subgraph)

        # subgraph 결과 저장
        FS_list.sort(key=lambda x: -len(x))
        FS_dict = {f"FS{i}": FS_list[i] for i in range(len(FS_list))}
        FS_dict["outliers"] = list(self.outliers)
        self.result["FSM"].append({"k": k, "min_support": ms, "FS": FS_dict})

    def is_all_visited(self, visit, subgraph):
        """
        모든 node를 방문했는지 확인하고 아닐시 해당 노드 return
        """
        for node in subgraph:
            if not visit[node]:
                visit[node] = True
                return False, node
        return True, None

    def run(self) -> Dict:
        for k in self.k_list:
            self.graphs = self.graph_dict[k]
            self.generate_mother_graph()
            self.detect_frequent_edge()
            for ms in self.min_supports:
                self.generate_adjacency_list(self.frequent_subgraphs[ms])
                self.get_subgraph(k, ms)
        return self.result