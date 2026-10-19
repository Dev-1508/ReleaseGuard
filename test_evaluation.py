from agent import run_agent
from evaluator import evaluate_exact_match
from database import get_database_connection


connection = get_database_connection()
cursor = connection.cursor()

cursor.execute(
    "SELECT * FROM test_cases WHERE dataset_id = ?",
    (1,)
)

test_cases = cursor.fetchall()

connection.close()

total_score = 0

for test_case in test_cases:
    input_text = test_case[1]
    expected_output = test_case[2]

    actual_output = run_agent(input_text)

    score = evaluate_exact_match(expected_output,actual_output)
    total_score += score

    print("Input:", input_text)
    print("Expected:", expected_output)
    print("Actual:", actual_output)
    print("Score:", score)
    print()

accuracy = total_score / len(test_cases)

print("Overall Accuracy:", accuracy)