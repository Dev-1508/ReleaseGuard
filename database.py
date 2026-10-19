import sqlite3


def initialize_database():
    connection = sqlite3.connect("releaseguard.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_versions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        project_id INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    project_id INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY,
    input_text TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    dataset_id INTEGER NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_runs (
    id INTEGER PRIMARY KEY,
    dataset_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_results (
    id INTEGER PRIMARY KEY,
    evaluation_run_id INTEGER NOT NULL,
    test_case_id INTEGER NOT NULL,
    actual_output TEXT NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY (evaluation_run_id) REFERENCES evaluation_runs(id),
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id)
    )
    """)

    connection.commit()
    connection.close()

def get_database_connection():
    connection = sqlite3.connect("releaseguard.db")
    return connection