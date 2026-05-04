from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

tasks_lst = []

import io
import contextlib
from itertools import cycle

f = io.StringIO()
with contextlib.redirect_stdout(f):
    import this
text = f.getvalue()
status_cycle = cycle(["cancelled", "completed", "in_progress", "pending"])
priority_cycle = cycle(["high", "low", "medium"])

num = 0
for line in text.splitlines():
    if not line:
        continue
    num += 1
    tasks_lst.append(
        {
            "id": num,
            "title": "Zen of Python",
            "description": line,
            "status": next(status_cycle),
            "priority": next(priority_cycle),
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "deleted_at": None,
        }
    )

@app.route("/api/v1/tasks", methods=["GET"])
def get_tasks_lst():
    """
    Получение списка всех задач, с поиском
    """
    query = request.args.get("query")
    ready_tasks_lst = tasks_lst
    if query:
        ready_tasks_lst = list()
        for task in tasks_lst:
            flag = False
            if query.lower() in task["title"].lower():
                flag = True
            if query.lower() in task["description"].lower():
                flag = True
            if flag:
                ready_tasks_lst.append(task)

    return jsonify(
        {
            "tasks": ready_tasks_lst,
        }
    )


@app.route("/api/v1/tasks/<task_id>", methods=["GET"])
def get_tasks(task_id):
    """
    Получение одной задачи с номером task_id
    """
    for task in tasks_lst:
        if task["id"] == int(task_id):
            return jsonify(task)
    return jsonify({"error": "Задача не найдена"}), 404


@app.route("/api/v1/tasks", methods=["POST"])
def post_tasks():
    """
    Публикация новой задачи и присвоение номера
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Отсутствуют данные JSON"}), 400

    title = data.get("title")
    if not title:
        return jsonify({"error": "Пропущен обязательный параметр `title`"}), 400

    description = data.get("description")
    if not description:
        return jsonify({"error": "Пропущен обязательный параметр `description`"}), 400

    new_task = {
        "id": len(tasks_lst) + 1,
        "title": title,
        "description": description,
        "status": data.get("status", "pending"),
        "priority": data.get("priority", "medium"),
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
        "deleted_at": None,
    }
    tasks_lst.append(new_task)
    return jsonify(new_task)


@app.route("/api/v1/tasks/<task_id>", methods=["DELETE"])
def delete_tasks(task_id):
    """
    Удвление одной задачи с номером task_id
    """
    for task in tasks_lst:
        if task["id"] == int(task_id):
            task["status"] = "cancelled"
            task["deleted_at"] = datetime.datetime.now().isoformat()
            return jsonify(task)
    return jsonify({"error": "Задача не найдена"}), 404


@app.route("/api/v1/tasks/<task_id>", methods=["PATCH"])
def patch_tasks(task_id):
    """
    Частичное обновление одной задачи с номером task_id
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Отсутствуют данные JSON"}), 400

    for task in tasks_lst:
        if task["id"] == int(task_id):
            task["title"] = data.get("title") or task["title"]
            task["description"] = data.get("description") or task["description"]
            task["status"] = data.get("status") or task["status"]
            task["priority"] = data.get("priority") or task["priority"]
            task["updated_at"] = datetime.datetime.now().isoformat()
            return jsonify(task)
    return jsonify({"error": "Задача не найдена"}), 404

def normalize(d):
    if isinstance(d, dict):
        return {
            k: normalize(v)
            for k, v in d.items()
            if k not in ("created_at", "updated_at", "deleted_at")
        }
    if isinstance(d, list):
        return [normalize(i) for i in d]
    return d
tasks_lst = normalize(tasks_lst)
if __name__ == "__main__":
    app.run(debug=True)
