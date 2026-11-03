from agent import run_agent
from evaluator import evaluate_normalized_match, evaluate_tool_call
from database import get_database_connection
from semantic_evaluator import evaluate_semantic_match
import json
import hashlib
import time

def create_evaluation_run_record(
    dataset_id,
    agent_version_id,
    max_test_cases=None
):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM test_cases
        WHERE dataset_id = ?
        ORDER BY id
        """,
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
            "pending",
            agent_version_id,
            dataset_fingerprint,
            run_type
        )
    )

    connection.commit()

    evaluation_run_id = cursor.lastrowid

    connection.close()

    return evaluation_run_id

def run_evaluation(
    dataset_id,
    agent_version_id,
    max_test_cases=None,
    evaluation_run_id=None
):

    total_latency_ms = 0
    
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
    """
    SELECT input_cost_per_million,
           output_cost_per_million
    FROM agent_versions
    WHERE id = ?
    """,
    (agent_version_id,)
)

    pricing = cursor.fetchone()

    if pricing is not None:
        input_cost_per_million = pricing[0] or 0
        output_cost_per_million = pricing[1] or 0
    else:
        input_cost_per_million = 0
        output_cost_per_million = 0

    cursor.execute(
        "SELECT * FROM test_cases WHERE dataset_id = ?",
        (dataset_id,)
    )

    test_cases = cursor.fetchall()

    if max_test_cases is not None:
        test_cases = test_cases[:max_test_cases]

    cursor.execute(
    """
    UPDATE evaluation_runs
    SET status = ?
    WHERE id = ?
    """,
    (
        "running",
        evaluation_run_id
    )
)

    connection.commit()

    results = []

    total_score = 0
    total_tool_score = 0
    tool_test_count = 0
    total_semantic_score = 0
    semantic_test_count = 0
    run_prompt_tokens = 0
    run_output_tokens = 0
    run_total_tokens = 0
    run_estimated_cost_usd = 0

    for test_case in test_cases:
        input_text = test_case[1]
        expected_output = test_case[2]

        start_time = time.perf_counter()

        agent_result = run_agent(
            input_text,
            agent_version_id
        )

        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000

        total_latency_ms += latency_ms

        actual_output = agent_result["output"]
        tool_calls = agent_result["tool_calls"]
        usage = agent_result.get("usage", {})

        prompt_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        input_cost = (
            prompt_tokens
            / 1_000_000
        ) * input_cost_per_million

        output_cost = (
            output_tokens
            / 1_000_000
        ) * output_cost_per_million

        estimated_cost_usd = input_cost + output_cost
        run_estimated_cost_usd += estimated_cost_usd

        run_prompt_tokens += prompt_tokens
        run_output_tokens += output_tokens
        run_total_tokens += total_tokens

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
            semantic_score,
            latency_ms,
            prompt_tokens,
            output_tokens,
            total_tokens,
            estimated_cost_usd
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            evaluation_run_id,
            test_case[0],
            actual_output,
            score,
            tool_score,
            semantic_score,
            latency_ms,
            prompt_tokens,
            output_tokens,
            total_tokens,
            estimated_cost_usd
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
            "semantic_score": semantic_score,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost_usd,
        })

    if len(test_cases) > 0:
        accuracy = total_score / len(test_cases)
    else:
        accuracy = 0

    if len(test_cases) > 0:
        average_latency_ms = total_latency_ms / len(test_cases)
    else:
        average_latency_ms = 0

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
    "average_latency_ms": average_latency_ms,
    "results": results,
    "prompt_tokens": run_prompt_tokens,
    "output_tokens": run_output_tokens,
    "total_tokens": run_total_tokens,
    "estimated_cost_usd": run_estimated_cost_usd,
}

def run_evaluation_background(
    evaluation_run_id,
    dataset_id,
    agent_version_id,
    max_test_cases=None
):
    try:
        run_evaluation(
            dataset_id,
            agent_version_id,
            max_test_cases,
            evaluation_run_id
        )

    except Exception:
        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE evaluation_runs
            SET status = ?
            WHERE id = ?
            """,
            (
                "failed",
                evaluation_run_id
            )
        )

        connection.commit()
        connection.close()

        raise