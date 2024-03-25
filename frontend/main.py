import re
import json
import networkx as nx
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pdb

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

tasks = []


def generate_graph_data(grpaph_data):
    G = nx.DiGraph()
    # Add nodes (tasks) to the graph
    for row in grpaph_data:
        G.add_node(row["name"], duration=row["duration"])

    # Add edges (dependencies) to the graph
    for row in grpaph_data:
        dependencies = row["dependencies"].split(",")
        for dependency in dependencies:
            if dependency:
                G.add_edge(dependency, row["name"])

    pos = nx.spring_layout(G)
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    
    color_map = {
        True: 'red',
        False: 'blue',
    }
    
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=['red' for _ in G.nodes()],
            size=40,
            colorbar=dict(
                thickness=15,
                title='Duration',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))
    # pdb.set_trace()
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([f"{node}<br>Duration: {G.nodes[node]['duration']}"])
        
        # node_trace['marker']['color'] += tuple([color_map[node]])

    graph_data = {"data": [edge_trace, node_trace], "layout": dict(
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )}

    return json.dumps(graph_data, cls=PlotlyJSONEncoder)


# def graph_data():
#     tasks = load_tasks()
#     # return [{ }  for task in tasks]
#     # pass

@app.get("/build_graph", response_class=HTMLResponse)
async def build_graph(request: Request):
    graph_data = generate_graph_data(load_tasks())
    return templates.TemplateResponse("graph_template.html", {"request": request, "graph_data": graph_data})


tasks_file = "tasks.json"

def load_tasks():
    try:
        with open(tasks_file, "r") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
    return tasks

def save_tasks(tasks):
    with open(tasks_file, "w") as file:
        json.dump(tasks, file)

tasks = load_tasks()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks, 'graph_data':  generate_graph_data(load_tasks())})

@app.post("/add_task")
async def add_task(request: Request, name: str = Form(...), duration: int = Form(...), dependencies: list = Form(...), in_cpm: bool = Form(...)):
    pattern = re.compile(r'\"(\w+)\"')
    new_task = {
        "name": name,
        "duration": duration,
        "dependencies": ",".join(pattern.findall(dependencies[0])),
        "in_cpm": in_cpm,
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return {"message": "Task added successfully"}

@app.post("/clear_tasks")
async def clear_tasks(request: Request):
    global tasks
    tasks = []
    save_tasks(tasks)
    return RedirectResponse("/", status_code=303)

@app.post("/update_task")
async def update_task(request: Request, task_id: int = Form(...), name: str = Form(...), duration: int = Form(...), dependencies: str = Form(...)):
    if task_id <= len(tasks):
        tasks[task_id - 1] = {"name": name, "duration": duration, "dependencies": dependencies}
        return {"message": "Task updated successfully"}
    else:
        return {"error": "Task not found"}

@app.post("/delete_task")
async def delete_task(request: Request, index: int = Form(...)):
    del tasks[index - 1]
    save_tasks(tasks)
    return RedirectResponse("/", status_code=303)
