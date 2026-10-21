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
        agent_version_id INTEGER,
        FOREIGN KEY (dataset_id) REFERENCES datasets(id),
        FOREIGN KEY (agent_version_id) REFERENCES agent_versions(id)
    )
    """)

    cursor.execute("PRAGMA table_info(evaluation_runs)")
    columns = cursor.fetchall()

    column_names = []

    for column in columns:
        column_names.append(column[1])

    if "agent_version_id" not in column_names:
        cursor.execute(
            "ALTER TABLE evaluation_runs ADD COLUMN agent_version_id INTEGER"
        )

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tool_calls (
        id INTEGER PRIMARY KEY,
        evaluation_result_id INTEGER NOT NULL,
        tool_name TEXT NOT NULL,
        arguments TEXT NOT NULL,
        result TEXT NOT NULL,
        FOREIGN KEY (evaluation_result_id)
            REFERENCES evaluation_results(id)
    )
    """)

    connection.commit()
    connection.close()

def get_database_connection():
    connection = sqlite3.connect("releaseguard.db")
    return connection