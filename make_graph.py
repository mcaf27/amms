import pandas as pd
import networkx as nx

df = pd.read_csv('dados.csv', encoding='latin-1',
                 dtype={'autor': str, 'nome': str, 'leitores': str})

G = nx.Graph()

for index, row in df.iterrows():
    readers = row['leitores'].split(';')
    node = row['nome']

    G.add_node(node)

    for other_row in df.iloc[index+1:].iterrows():
        if other_row[0] != row.name:
            other_readers = other_row[1]['leitores'].split(';')
            common_readers = set(readers) & set(other_readers)
            if common_readers:
                edge_weight = len(common_readers)

                G.add_edge(row['nome'], other_row[1]
                           ['nome'], weight=edge_weight)

edge_list = [(u, v, G[u][v]['weight']) for u, v in G.edges]

# edge_list = []
# for u, v, data in G.edges(data=True):
#     if data['weight'] > 1:
#         edge_list.append({'Source': u, 'Target': v, 'Weight': data['weight']})


edges_df = pd.DataFrame(edge_list, columns=['Source', 'Target', 'Weight'])

edges_df.to_csv('arestas.csv', index=False)
