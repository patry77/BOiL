import json
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