import re
from CreatePlot import *
from task_methods import *
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
app = FastAPI()
templates = Jinja2Templates(directory="templates")
tasks = []
tasks = load_tasks()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    print(tasks)
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks, 'graph_data':  generate_graph_data(load_tasks()), 'gantt_chart': create_gantt_plot()})

@app.post("/add_task")
async def add_task(request: Request, name: str = Form(...), duration: int = Form(...), relation: str = Form(...), in_cpm: bool = Form(...)):
    new_task = {
        "name": name,
        "duration": duration,
        "relation": relation, # New field for relation
        "in_cpm": in_cpm,
    }
    if  not re.match(r'^\d+-\d+$', new_task['relation']):
        return {"error": "Relation must be in format 'number-number'"}
    
    existing_task = [ i for i in range(len(tasks)) if tasks[i]['name'] == new_task["name"]]
    if len(existing_task) != 0:
        tasks[existing_task[0]] = new_task
    else:
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
