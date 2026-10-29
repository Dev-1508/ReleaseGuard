from agent import run_agent
from evaluator import evaluate_normalized_match, evaluate_tool_call
from database import get_database_connection
from semantic_evaluator import evaluate_semantic_match
import json
import hashlib


def run_evaluation(
    dataset_id,
    agent_version_id,
    max_test_cases=None
):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM test_cases WHERE dataset_id = ?",
        (dataset_id,)
    )

    test_cases = cursor.fetchall()

    if max_test_cases is not None:
        test_cases = test_cases[:max_test_cases]

    fingerprint_data = []

    for test_case in test_cases:
        fingerprint_data.append({
            "id": test_case[0],
            "input_text": test_case[1],
            "expected_output": test_case[2],
            "dataset_id": test_case[3],
            "expected_tool": test_case[4]
            })

    fingerprint_text = json.dumps(
        fingerprint_data,
        sort_keys=True
    )

    dataset_fingerprint = hashlib.sha256(
        fingerprint_text.encode("utf-8")
    ).hexdigest()

    if max_test_cases is None:
        run_type = "full"
    else:
        run_type = "smoke"

    cursor.execute(
        """
        INSERT INTO evaluation_runs (
        dataset_id,
        status,
        agent_version_id,
        dataset_fingerprint,
        run_type
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
        dataset_id,
        "running",
        agent_version_id,
        dataset_fingerprint,
        run_type
    )
    )
    
    connection.commit()
    
    evaluation_run_id = cursor.lastrowid

    results = []

    total_score = 0
    total_tool_score = 0
    tool_test_count = 0
    total_semantic_score = 0
    semantic_test_count = 0

    for test_case in test_cases:
        input_text = test_case[1]
        expected_output = test_case[2]

        agent_result = run_agent(
        input_text,
        agent_version_id
        )

        actual_output = agent_result["output"]
        tool_calls = agent_result["tool_calls"]

        score = evaluate_normalized_match(
            expected_output,
            actual_output
        )

        if score == 1:
            semantic_score = 1
        else:
            semantic_score = evaluate_semantic_match(
                expected_output,
                actual_output
            )

        if semantic_score is not None:
            total_semantic_score += semantic_score
            semantic_test_count += 1
        
        expected_tool = test_case[4]

        tool_score = evaluate_tool_call(
                    expected_tool,
                    tool_calls
                )

        if tool_score is not None:
            total_tool_score += tool_score
            tool_test_count += 1
        
        total_score += score

        cursor.execute(
        """
        INSERT INTO evaluation_results (
            evaluation_run_id,
            test_case_id,
            actual_output,
            score,
            tool_score,
            semantic_score
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            evaluation_run_id,
            test_case[0],
            actual_output,
            score,
            tool_score,
            semantic_score
        )
    )

        connection.commit()
        evaluation_result_id = cursor.lastrowid

        for tool_call in tool_calls:
            cursor.execute(
        """
        INSERT INTO tool_calls (
            evaluation_result_id,
            tool_name,
            arguments,
            result
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            evaluation_result_id,
            tool_call["tool"],
            json.dumps(tool_call["arguments"]),
            tool_call["result"]
        )
    )

        connection.commit()

        results.append({
            "test_case_id": test_case[0],
            "input_text": input_text,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "score": score,
            "expected_tool": expected_tool,
            "tool_score": tool_score,
            "tool_calls": tool_calls,
            "semantic_score": semantic_score
        })

    if len(test_cases) > 0:
        accuracy = total_score / len(test_cases)
    else:
        accuracy = 0

    if tool_test_count > 0:
        tool_accuracy = total_tool_score / tool_test_count
    else:
        tool_accuracy = None

    if semantic_test_count > 0:
        semantic_accuracy = total_semantic_score / semantic_test_count
    else:
        semantic_accuracy = None

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
    "tool_accuracy": tool_accuracy,
    "semantic_accuracy": semantic_accuracy,
    "results": results
}