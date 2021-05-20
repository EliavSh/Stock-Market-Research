import os
import pickle
import pandas as pd
import numpy as np
from typing import Tuple, List

from ..hats_config import HatsConfig


# TODO - add s-outs/logs

class ModelParams:

    def __init__(self, symbols_with_historical_data: List[str]):
        # load from config
        self.neighbors_sample = HatsConfig.neighbors_sample
        self.max_relations_allowed_quantile = HatsConfig.max_relations_allowed_quantile

        # final properties
        self.symbols_with_historical_data = symbols_with_historical_data
        self.neighbors_per_relation_type, self.summary_adjacency_matrix, self.num_relation_types, self.num_companies = self.calc_relation_types_over_companies()

    def calc_relation_types_over_companies(self) -> Tuple[List[List[np.array]], np.ndarray, int, int]:
        """
        :return:
        1. neighbors_per_relation_type:
            list of all relation types with:
                list of all companies with:
                    1-dim np.array of companies indices, that are in relation to the specific company
                    -on the specific relation type
        2. summary_adjacency_matrix:
            2-dim np.array of size (n_relation_types, n_companies), which sums the number of relations
            a company have for every relation type for all companies
        3. num_relation_types: the number of relation types
        4. num_companies: the number of companies
        """
        # TODO - add test cases with matching files (.pkl, .csv ...)
        # read tickers with relations
        tickers = pickle.load(open(os.path.join(os.path.dirname(__file__), 'ordered_ticker.pkl'), 'rb'))
        tickers_with_historical_data = [i in self.symbols_with_historical_data for i in tickers]

        # read file of numbers of relations per company per relation types (f: (relation_types, companies))
        graph_adjacency_matrix = pickle.load(open(os.path.join(os.path.dirname(__file__), 'adj_mat.pkl'), 'rb'))

        # remove all companies with relational data which are without historical data
        graph_adjacency_matrix = graph_adjacency_matrix[:, tickers_with_historical_data][:, :, tickers_with_historical_data]
        # TODO - why the fuck graph_adjacency_matrix[:, tickers_with_historical_data, tickers_with_historical_data] doesn't works??

        # set number of companies
        num_companies = graph_adjacency_matrix.shape[1]

        # set commonly used variables from the adjacency matrix
        summary_adjacency_matrix = graph_adjacency_matrix.sum(2)

        """
        reduce relation types by:
         1. relation types which zero companies 
         2. too common relation types
        """
        # TODO - which max is better?
        max_relations = pd.Series(summary_adjacency_matrix[summary_adjacency_matrix.any(1)].sum(1)).quantile([self.max_relations_allowed_quantile]).values[0]
        max_relations = np.inf
        keep_relation_types = np.logical_and(summary_adjacency_matrix.any(1), summary_adjacency_matrix.sum(1) <= max_relations)

        summary_adjacency_matrix = summary_adjacency_matrix[keep_relation_types]
        num_relation_types = len(summary_adjacency_matrix)

        graph_adjacency_matrix = graph_adjacency_matrix[keep_relation_types]
        neighbors_per_relation_type = []
        for rel_idx, rel_mat_i in enumerate(graph_adjacency_matrix):
            rel_neighbors = []
            for cpn_idx, row in enumerate(rel_mat_i):
                rel_neighbors.append(row.nonzero()[0])
            neighbors_per_relation_type.append(rel_neighbors)

        return neighbors_per_relation_type, summary_adjacency_matrix, num_relation_types, num_companies

    def sample_neighbors(self):
        """
        TODO - why are we sampling neighbors? the result is that same weights are being updated from different source of inputs,
         it's very probable to get different companies in case neighbors_sample >> k..
         In my opinion we should use all the neighbors a company has and prune weights if needed
         further work needed here, I think we should build a model for companies relations and gather the most related by k,
         that way we always training the attention weights toward the same direction (based on same company features as input)
        """
        k = self.neighbors_sample
        neighbors_batch = []
        for rel_neighbors in self.neighbors_per_relation_type:
            rel_neighbors_batch = []
            for cpn_idx, neighbors in enumerate(rel_neighbors):
                short = max(0, k - neighbors.shape[0])
                if short:  # less neighbors than k
                    neighbors = np.expand_dims(np.concatenate([neighbors, np.zeros(short)]), 0)
                    rel_neighbors_batch.append(neighbors)
                else:
                    neighbors = np.expand_dims(np.random.choice(neighbors, k), 0)
                    rel_neighbors_batch.append(neighbors)
            neighbors_batch.append(np.expand_dims(np.concatenate(rel_neighbors_batch, 0), 0))

        yield np.concatenate(neighbors_batch, 0)
