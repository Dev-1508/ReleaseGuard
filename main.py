from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import initialize_database
import sqlite3

app = FastAPI()
initialize_database()
class Project(BaseModel):
    name:str

@app.get("/")
def home():
    return {"message": "ReleaseGuard is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/projects")
def get_projects():
    connection = sqlite3.connect("releaseguard.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()

    connection.close()

    projects = []

    for row in rows:
        projects.append({
            "id": row[0],
            "name": row[1]
        })

    return {"projects": projects}

class ProjectUpdate(BaseModel):
    name: str

@app.post("/projects")
def create_project(project: Project):
    connection = sqlite3.connect("releaseguard.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO projects (name) VALUES (?)",
        (project.name,)
    )

    connection.commit()

    project_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Project created",
        "project": {
            "id": project_id,
            "name": project.name
        }
    }

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    connection = sqlite3.connect("releaseguard.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "id": row[0],
        "name": row[1]
    }

@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    connection = sqlite3.connect("releaseguard.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    cursor.execute(
        "DELETE FROM projects WHERE id = ?",
        (project_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Project deleted"
    }

@app.put("/projects/{project_id}")
def update_project(project_id: int, project: ProjectUpdate):
    connection = sqlite3.connect("releaseguard.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    cursor.execute(
        "UPDATE projects SET name = ? WHERE id = ?",
        (project.name, project_id)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Project updated",
        "project": {
            "id": project_id,
            "name": project.name
        }
    }