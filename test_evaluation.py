from evaluation_runner import run_evaluation


evaluation = run_evaluation(1)

print("Evaluation Run ID:", evaluation["evaluation_run_id"])

for result in evaluation["results"]:
    print(result)