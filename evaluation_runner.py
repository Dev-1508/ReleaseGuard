from agent import run_agent
from evaluator import evaluate_exact_match
from database import get_database_connection


def run_evaluation(dataset_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
    """
    INSERT INTO evaluation_runs (dataset_id, status)
    VALUES (?, ?)
    """,
    (dataset_id, "running")
)

    connection.commit()

    evaluation_run_id = cursor.lastrowid

    cursor.execute(
        "SELECT * FROM test_cases WHERE dataset_id = ?",
        (dataset_id,)
    )

    test_cases = cursor.fetchall()

    results = []

    total_score = 0

    for test_case in test_cases:
        input_text = test_case[1]
        expected_output = test_case[2]

        actual_output = run_agent(input_text)

        score = evaluate_exact_match(
            expected_output,
            actual_output
        )
        total_score += score

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

        results.append({
            "test_case_id": test_case[0],
            "input_text": input_text,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "score": score
        })

    if len(test_cases) > 0:
        accuracy = total_score / len(test_cases)
    else:
        accuracy = 0

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

    return {
    "evaluation_run_id": evaluation_run_id,
    "accuracy": accuracy,
    "results": results
}