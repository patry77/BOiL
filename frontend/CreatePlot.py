import json
import networkx as nx
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder

def create_graph_nodes_edges(tasks):
    nodes = set()
    eges = []
    for task in tasks:
        [nodes.add(n) for n in task['relation'].split('-')]
        eges.append( {'key': task['relation'], 'edges': task['relation'].split('-'), 'name': task['name'], 'duration': task['duration'] } )
    return [{'name': n} for n in nodes], eges

def generate_graph_data(tasks):
    G = nx.DiGraph()
    nodes, edges = create_graph_nodes_edges(tasks)
    # Add nodes (tasks) to the graph
    for node in nodes:
        G.add_node(node["name"])
        
    for edge in edges:
        G.add_edge(edge['edges'][0], edge['edges'][1] if len(edge['edges'])>1 else edge['edges'][0], name=edge['name'], duration=edge['duration'])

    pos = nx.spring_layout(G)
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='text',
        mode="lines+text",
        text=[],
        textposition="bottom left")

    for edge in G.edges():
        if edge[0] == edge[1]:
            continue 
        actual_edge = [k for k in edges if k['key'] == '-'.join(edge)][0]
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
        edge_trace['text'] += tuple([f"{actual_edge['name']} - {actual_edge['duration']} days                           "])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        hoverinfo='text',
        textposition='top center',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=['red' for _ in G.nodes()],
            size=40,
            line=dict(width=2)))

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([f"{node}"])
        
        # node_trace['marker']['color'] += tuple([color_map[node]])

    graph_data = {"data": [edge_trace, node_trace], "layout": dict(
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False,
    )}

    return json.dumps(graph_data, cls=PlotlyJSONEncoder)