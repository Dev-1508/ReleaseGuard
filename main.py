from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import initialize_database, get_database_connection
from evaluation_runner import run_evaluation

app = FastAPI()
initialize_database()
class Project(BaseModel):
    name:str

class ProjectUpdate(BaseModel):
    name: str

class Dataset(BaseModel):
    name: str
    project_id: int
class TestCase(BaseModel):
    input_text: str
    expected_output: str
    dataset_id: int

class EvaluationRun(BaseModel):
    dataset_id: int

class AgentVersion(BaseModel):
    name: str
    project_id: int

@app.get("/")
def home():
    return {"message": "ReleaseGuard is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/projects")
def get_projects():
    connection = get_database_connection()
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



@app.post("/projects")
def create_project(project: Project):
    connection = get_database_connection()
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
    connection = get_database_connection()
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
    connection = get_database_connection()
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
    connection = get_database_connection()
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

@app.post("/datasets")
def create_dataset(dataset: Dataset):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (dataset.project_id,)
    )

    project = cursor.fetchone()

    if project is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    cursor.execute(
        "INSERT INTO datasets (name, project_id) VALUES (?, ?)",
        (dataset.name, dataset.project_id)
    )

    connection.commit()

    dataset_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Dataset created",
        "dataset": {
            "id": dataset_id,
            "name": dataset.name,
            "project_id": dataset.project_id
        }
    }

@app.get("/datasets")
def get_datasets():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM datasets")
    rows = cursor.fetchall()

    connection.close()

    datasets = []

    for row in rows:
        datasets.append({
            "id": row[0],
            "name": row[1],
            "project_id": row[2]
        })

    return {"datasets": datasets}

@app.get("/projects/{project_id}/datasets")
def get_project_datasets(project_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )

    project = cursor.fetchone()

    if project is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    cursor.execute(
        "SELECT * FROM datasets WHERE project_id = ?",
        (project_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    datasets = []

    for row in rows:
        datasets.append({
            "id": row[0],
            "name": row[1],
            "project_id": row[2]
        })

    return {"datasets": datasets}

@app.post("/test-cases")
def create_test_case(test_case: TestCase):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM datasets WHERE id = ?",
        (test_case.dataset_id,)
    )

    dataset = cursor.fetchone()

    if dataset is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    cursor.execute(
        """
        INSERT INTO test_cases (input_text, expected_output, dataset_id)
        VALUES (?, ?, ?)
        """,
        (
            test_case.input_text,
            test_case.expected_output,
            test_case.dataset_id
        )
    )

    connection.commit()

    test_case_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Test case created",
        "test_case": {
            "id": test_case_id,
            "input_text": test_case.input_text,
            "expected_output": test_case.expected_output,
            "dataset_id": test_case.dataset_id
        }
    }

@app.get("/datasets/{dataset_id}/test-cases")
def get_dataset_test_cases(dataset_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM datasets WHERE id = ?",
        (dataset_id,)
    )

    dataset = cursor.fetchone()

    if dataset is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    cursor.execute(
        "SELECT * FROM test_cases WHERE dataset_id = ?",
        (dataset_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    test_cases = []

    for row in rows:
        test_cases.append({
            "id": row[0],
            "input_text": row[1],
            "expected_output": row[2],
            "dataset_id": row[3]
        })

    return {"test_cases": test_cases}

@app.post("/evaluation-runs")
def create_evaluation_run(evaluation_run: EvaluationRun):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM datasets WHERE id = ?",
        (evaluation_run.dataset_id,)
    )

    dataset = cursor.fetchone()
    connection.close()

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    evaluation = run_evaluation(
        evaluation_run.dataset_id
    )

    return {
        "message": "Evaluation completed",
        "evaluation": evaluation
    }

@app.get("/evaluation-runs/{evaluation_run_id}")
def get_evaluation_run(evaluation_run_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM evaluation_runs WHERE id = ?",
        (evaluation_run_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found"
        )

    return {
        "id": row[0],
        "dataset_id": row[1],
        "status": row[2]
    }

@app.get("/evaluation-runs")
def get_evaluation_runs():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM evaluation_runs")
    rows = cursor.fetchall()

    connection.close()

    evaluation_runs = []

    for row in rows:
        evaluation_runs.append({
            "id": row[0],
            "dataset_id": row[1],
            "status": row[2]
        })

    return {"evaluation_runs": evaluation_runs}

@app.get("/evaluation-runs/{evaluation_run_id}/results")
def get_evaluation_results(evaluation_run_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM evaluation_runs WHERE id = ?",
        (evaluation_run_id,)
    )

    evaluation_run = cursor.fetchone()

    if evaluation_run is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found"
        )

    cursor.execute(
        """
        SELECT * FROM evaluation_results
        WHERE evaluation_run_id = ?
        """,
        (evaluation_run_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "evaluation_run_id": row[1],
            "test_case_id": row[2],
            "actual_output": row[3],
            "score": row[4]
        })

    return {"results": results}

@app.get("/evaluation-runs/{evaluation_run_id}/summary")
def get_evaluation_summary(evaluation_run_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM evaluation_runs WHERE id = ?",
        (evaluation_run_id,)
    )

    evaluation_run = cursor.fetchone()

    if evaluation_run is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found"
        )

    cursor.execute(
        """
        SELECT score
        FROM evaluation_results
        WHERE evaluation_run_id = ?
        """,
        (evaluation_run_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    if len(rows) == 0:
        accuracy = 0
    else:
        total_score = 0

        for row in rows:
            total_score += row[0]

        accuracy = total_score / len(rows)

    return {
        "evaluation_run_id": evaluation_run_id,
        "status": evaluation_run[2],
        "total_tests": len(rows),
        "accuracy": accuracy
    }

@app.post("/agent-versions")
def create_agent_version(agent_version: AgentVersion):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (agent_version.project_id,)
    )

    project = cursor.fetchone()

    if project is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    cursor.execute(
        """
        INSERT INTO agent_versions (name, project_id)
        VALUES (?, ?)
        """,
        (
            agent_version.name,
            agent_version.project_id
        )
    )

    connection.commit()

    agent_version_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Agent version created",
        "agent_version": {
            "id": agent_version_id,
            "name": agent_version.name,
            "project_id": agent_version.project_id
        }
    }

@app.get("/projects/{project_id}/agent-versions")
def get_project_agent_versions(project_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )

    project = cursor.fetchone()

    if project is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    cursor.execute(
        """
        SELECT * FROM agent_versions
        WHERE project_id = ?
        """,
        (project_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    agent_versions = []

    for row in rows:
        agent_versions.append({
            "id": row[0],
            "name": row[1],
            "project_id": row[2]
        })

    return {
        "agent_versions": agent_versions
    }