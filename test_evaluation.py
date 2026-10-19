from agent import run_agent
from evaluator import evaluate_exact_match
from database import get_database_connection


connection = get_database_connection()
cursor = connection.cursor()

cursor.execute(
    """
    INSERT INTO evaluation_runs (dataset_id, status)
    VALUES (?, ?)
    """,
    (1, "running")
)

connection.commit()

evaluation_run_id = cursor.lastrowid

cursor.execute(
    "SELECT * FROM test_cases WHERE dataset_id = ?",
    (1,)
)

test_cases = cursor.fetchall()

total_score = 0

for test_case in test_cases:
    input_text = test_case[1]
    expected_output = test_case[2]

    actual_output = run_agent(input_text)

    score = evaluate_exact_match(expected_output,actual_output)

    cursor.execute(
    """
    INSERT INTO evaluation_results (
        evaluation_run_id,
        test_case_id,
        actual_output,
        score
    )
    VALUES (?, ?, ?, ?)
    """,
    (
        evaluation_run_id,
        test_case[0],
        actual_output,
        score
    )
    )

    connection.commit()

    total_score += score

    print("Input:", input_text)
    print("Expected:", expected_output)
    print("Actual:", actual_output)
    print("Score:", score)
    print()

accuracy = total_score / len(test_cases)

print("Overall Accuracy:", accuracy)

cursor.execute(
    """
    UPDATE evaluation_runs
    SET status = ?
    WHERE id = ?
    """,
    ("completed", evaluation_run_id)
)

connection.commit()
connection.close()