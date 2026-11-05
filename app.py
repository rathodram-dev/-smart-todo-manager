
import csv
import io

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, Response, abort
)

from database import (
    init_db, get_all_tasks, add_task,
    get_task, update_task, toggle_task,
    delete_task, get_statistics
)

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"

# Initialize Database
init_db()

VALID_PRIORITIES = {"High", "Medium", "Low"}


@app.route("/")
def home():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "all")

    if status not in {"all", "pending", "completed"}:
        status = "all"

    tasks = get_all_tasks(search, status)
    stats = get_statistics()

    return render_template(
        "index.html",
        tasks=tasks,
        stats=stats,
        search=search,
        status=status
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "").strip()

    if not title:
        flash("Task title is required!", "error")
        return redirect(url_for("home"))

    if priority not in VALID_PRIORITIES:
        flash("Invalid priority selected!", "error")
        return redirect(url_for("home"))

    add_task(title, description, priority, due_date)

    flash("Task added successfully!", "success")
    return redirect(url_for("home"))


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    if not get_task(task_id):
        abort(404)

    toggle_task(task_id)
    flash("Task status updated!", "success")

    return redirect(url_for("home"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    task = get_task(task_id)

    if not task:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "").strip()

        if not title:
            flash("Task title is required!", "error")
            return redirect(url_for("edit", task_id=task_id))

        if priority not in VALID_PRIORITIES:
            flash("Invalid priority!", "error")
            return redirect(url_for("edit", task_id=task_id))

        update_task(
            task_id, title, description, priority, due_date
        )

        flash("Task updated successfully!", "success")
        return redirect(url_for("home"))

    return render_template("edit.html", task=task)


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    if not get_task(task_id):
        abort(404)

    delete_task(task_id)
    flash("Task deleted successfully!", "success")

    return redirect(url_for("home"))


@app.route("/export")
def export():
    tasks = get_all_tasks()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Title", "Description",
        "Priority", "Due Date", "Status"
    ])

    for task in tasks:
        writer.writerow([
            task["id"],
            task["title"],
            task["description"],
            task["priority"],
            task["due_date"] or "",
            "Completed" if task["completed"] else "Pending"
        ])

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=tasks.csv"
        }
    )



if __name__ == "__main__":
    app.run(debug=True)