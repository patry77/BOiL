import json
import networkx as nx
import requests as req
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
from task_methods import load_tasks, save_tasks

URL = 'http://localhost:5000/cpm'

COLOR_MAP = {
    False: 'blue',
    True: 'red',
}

def get_color(is_critical):
    return COLOR_MAP.get(bool( is_critical))

def task_to_send(tasks):
    sended_tasks = [{
        'name': task['name'], 
        'nastepstwo zdarzen': task['relation'],
        'duration': task['duration'],
        }  for task in tasks]
    return  { 'activities': sended_tasks }

def make_request(tasks):
    data = task_to_send(tasks)
    response = req.post(URL, json=data)
    update_tasks(response.json())
    return response.json()

def update_tasks(response):
    tasks = load_tasks()
    name_values = list(map(lambda x: [x['name'], x['isCritical']], response))
    for nv in name_values:
        [t for t in tasks if t['name'] == nv[0]][0]['in_cpm'] = nv[1]
    save_tasks(tasks)

def create_nodes(tasks):
    name_nodes = set()
    nodes = []
    for task in tasks:
        names = [ name for name in task['nastepstwo zdarzen'].split('-') if name not in name_nodes]
        [name_nodes.add(name) for name in names]
        [
              nodes.append( {'name': name, 
                            'isCritical': task['isCritical'],
                            'LF': task['LF'],
                            'LS': task['LS'],
                            'EF': task['EF'],
                            'ES': task['ES'],}
                        ) 
        for name in names
        ]
    return nodes

def create_edges(tasks):
    return [ 
            {
                'key': task['nastepstwo zdarzen'],
                'edges': task['nastepstwo zdarzen'].split('-'),
                'name': task['name'],
                'duration': task['duration'],
                'isCritical': task['isCritical'],
            }
            for task in tasks
            ]

def create_graph_nodes_edges(tasks):
    tasks = make_request(tasks)
    return create_nodes(tasks), create_edges(tasks)
    
def generate_graph_data(tasks):
    G = nx.DiGraph()
    nodes, edges = create_graph_nodes_edges(tasks)
    for node in nodes:
        G.add_node(node["name"])
        
    for edge in edges:
        G.add_edge(edge['edges'][0], 
                   edge['edges'][1] if len(edge['edges'])>1 else edge['edges'][0], 
                   name=edge['name'], 
                   duration=edge['duration'],
                   )
        
    pos = nx.fruchterman_reingold_layout(G)
    edge_trace = go.Scatter(
        x=[],
        y=[],
        hoverinfo='text',
        mode='markers+lines',
        marker={'color': []},
        text=[],
    )

    xt = []
    yt = []
    tasks_text = []
    for e in G.edges():
        tasks_text.append([ t['name'] for t in tasks if t['relation'] == '-'.join(e)][0])
        mid_edge = 0.5*(pos[e[0]]+pos[e[1]])# mid point of the edge e
        xt.append(mid_edge[0])
        yt.append(mid_edge[1])
        
    trace_text = go.Scatter(x=xt, y=yt, 
                       mode='text',
                       textfont=dict(size=50, color='rgb(25,25,25)'),
                       text=tasks_text,
                       textposition='bottom center', hoverinfo='text')
        
        
    edge_list = []
    for edge in G.edges():
        if edge[0] == edge[1]:
            continue 
        actual_edge = [k for k in edges if k['key'] == '-'.join(edge)][0]
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_list.append(
            dict(type='scatter',
                   mode='line',
                   line=dict(width=2, color=get_color(actual_edge.get('isCritical'))),
                   x=tuple([x0, x1, None]),
                   y=tuple([y0, y1, None])
                   )
        )
        
    for edge in G.edges():
        if edge[0] == edge[1]:
            continue 
        actual_edge = [k for k in edges if k['key'] == '-'.join(edge)][0]
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])


    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        textposition='top center',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=40
            )
        )
    def create_text(node):
        return f"{node['name']}<br>ES: {node['ES']}<br>EF: {node['EF']}<br>LS: {node['LS']}<br>LF: {node['LF']}<bt> I"

    for node in G.nodes():
        x, y = pos[node]
        actual_node = [k for k in nodes if k['name'] == node][0]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([create_text(actual_node)])
        node_trace['marker']['color'] += tuple([get_color(actual_node.get('isCritical'))])

    graph_data = {"data": [edge_trace, node_trace, trace_text] + edge_list, "layout": dict(
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False,
    )}

    return json.dumps(graph_data, cls=PlotlyJSONEncoder)