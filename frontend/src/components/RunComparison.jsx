import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function RunComparison({ runs }) {
  const completedRuns = runs.filter(
    (run) => run.status === "completed"
  );

  const [run1, setRun1] = useState("");
  const [run2, setRun2] = useState("");
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function compareRuns() {
    if (!run1 || !run2) {
      setError("Select two runs first.");
      return;
    }

    if (run1 === run2) {
      setError("Choose two different runs.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setComparison(null);

      const response = await fetch(
        `${API_URL}/comparisons/runs/${run1}/${run2}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not compare runs"
        );
      }

      console.log("Comparison:", data);

      setComparison({ ...data, run_1_id: data.run_1_id ?? run1, run_2_id: data.run_2_id ?? run2 });

    } catch (error) {
      console.error(error);
      setError(error.message);

    } finally {
      setLoading(false);
    }
  }

  function percent(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    return `${(Number(value) * 100).toFixed(0)}%`;
  }

  function latency(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    return `${(Number(value) / 1000).toFixed(2)}s`;
  }

  function cost(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }
  
    return `$${Number(value).toFixed(4)}`;
  }

  return (
    <section className="comparison-panel" id="comparison">
      <div className="comparison-header">
        <div>
          <h2>Compare Evaluation Runs</h2>

          <p>
            Compare model quality, efficiency and deployment
            readiness.
          </p>
        </div>
      </div>

      <div className="comparison-controls">
        <div className="control-group">
          <label htmlFor="baseline-run">Baseline Run</label>

          <select
            id="baseline-run" value={run1}
            onChange={(event) =>
              setRun1(event.target.value)
            }
          >
            <option value="">
              Select baseline
            </option>

            {completedRuns.map((run) => (
              <option
                key={run.id}
                value={run.id}
              >
                Run #{run.id} — Version{" "}
                {run.agent_version_id}
              </option>
            ))}
          </select>
        </div>

        <div className="comparison-arrow" aria-hidden="true">
          →
        </div>

        <div className="control-group">
          <label htmlFor="candidate-run">Candidate Run</label>

          <select
            id="candidate-run" value={run2}
            onChange={(event) =>
              setRun2(event.target.value)
            }
          >
            <option value="">
              Select candidate
            </option>

            {completedRuns.map((run) => (
              <option
                key={run.id}
                value={run.id}
              >
                Run #{run.id} — Version{" "}
                {run.agent_version_id}
              </option>
            ))}
          </select>
        </div>

        <button
          className="compare-button"
          onClick={compareRuns}
          disabled={loading}
        >
          {loading
            ? "Comparing..."
            : "Compare Runs"}
        </button>
      </div>

      {error && (
        <div className="comparison-error" role="alert">
          {error}
        </div>
      )}

      {comparison && (
        <div className="comparison-results">
          <div
            className={`deployment-banner ${
              comparison.deployment_decision ===
              "PASS"
                ? "pass"
                : "fail"
            }`}
          >
            <div>
              <span>Deployment Decision</span>

              <h2>
                {comparison.deployment_decision}
              </h2>
            </div>

            <p>
              {comparison.deployment_reason}
            </p>
          </div>

          <div className="comparison-table-wrapper">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Metric</th>

                  <th>
                    Run #{comparison.run_1_id}
                  </th>

                  <th>
                    Run #{comparison.run_2_id}
                  </th>
                </tr>
              </thead>

              <tbody>
                <ComparisonRow
                  name="Model"
                  value1={
                    comparison.run_1_model_name ??
                    `Version ${comparison.run_1_agent_version_id}`
                  }
                  value2={
                    comparison.run_2_model_name ??
                    `Version ${comparison.run_2_agent_version_id}`
                  }
                />

                <ComparisonRow
                  name="Response Accuracy"
                  value1={percent(
                    comparison.run_1_accuracy
                  )}
                  value2={percent(
                    comparison.run_2_accuracy
                  )}
                />

                <ComparisonRow
                  name="Tool Accuracy"
                  value1={percent(
                    comparison.run_1_tool_accuracy
                  )}
                  value2={percent(
                    comparison.run_2_tool_accuracy
                  )}
                />

                <ComparisonRow
                  name="Semantic Accuracy"
                  value1={percent(
                    comparison.run_1_semantic_accuracy
                  )}
                  value2={percent(
                    comparison.run_2_semantic_accuracy
                  )}
                />

                <ComparisonRow
                  name="Average Latency"
                  value1={latency(
                    comparison.run_1_average_latency_ms
                  )}
                  value2={latency(
                    comparison.run_2_average_latency_ms
                  )}
                />

                <ComparisonRow
                  name="Total Tokens"
                  value1={
                    comparison.run_1_total_tokens ??
                    "N/A"
                  }
                  value2={
                    comparison.run_2_total_tokens ??
                    "N/A"
                  }
                />

                <ComparisonRow
                  name="Estimated Cost"
                  value1={cost(
                    comparison.run_1_estimated_cost_usd
                  )}
                  value2={cost(
                    comparison.run_2_estimated_cost_usd
                  )}
                />
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}

function ComparisonRow({
  name,
  value1,
  value2
}) {
  return (
    <tr>
      <td className="comparison-metric">
        {name}
      </td>

      <td>{value1}</td>

      <td>{value2}</td>
    </tr>
  );
}

export default RunComparison;