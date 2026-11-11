import { useEffect, useState } from "react";
import "./App.css";
import RunComparison from "./components/RunComparison";


const API_URL = "http://127.0.0.1:8000";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [runs, setRuns] = useState([]);
  const [latestSummary, setLatestSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedVersion, setSelectedVersion] = useState(5);
  const [testCount, setTestCount] = useState(2);

  const [activeRun, setActiveRun] = useState(null);
  const [runStatus, setRunStatus] = useState(null);
  const [startingRun, setStartingRun] = useState(false);  

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);

    try {
      // 1. Check backend
      const healthResponse = await fetch(`${API_URL}/`);

      if (!healthResponse.ok) {
        throw new Error("Backend unavailable");
      }

      setBackendStatus("Connected");

      // 2. Load evaluation runs
      const runsResponse = await fetch(
        `${API_URL}/evaluation-runs`
      );

      if (!runsResponse.ok) {
        throw new Error("Could not load evaluation runs");
      }

      const runsData = await runsResponse.json();

      console.log("Runs from backend:", runsData);

      let runList = [];

      if (Array.isArray(runsData)) {
        runList = runsData;
      } else if (Array.isArray(runsData.evaluation_runs)) {
        runList = runsData.evaluation_runs;
      } else if (Array.isArray(runsData.runs)) {
        runList = runsData.runs;
      }

      setRuns(runList);

      // 3. Find latest completed run
      const completedRuns = runList.filter(
        (run) => run.status === "completed"
      );

      if (completedRuns.length > 0) {
        const latestRun =
          completedRuns[completedRuns.length - 1];

        const runId =
          latestRun.id ??
          latestRun.evaluation_run_id;

        if (runId !== undefined) {
          const summaryResponse = await fetch(
            `${API_URL}/evaluation-runs/${runId}/summary`
          );

          if (summaryResponse.ok) {
            const summaryData =
              await summaryResponse.json();

            console.log(
              "Latest summary:",
              summaryData
            );

            setLatestSummary(summaryData);
          }
        }
      }
    } catch (error) {
      console.error("Dashboard error:", error);
      setBackendStatus("Disconnected");
    } finally {
      setLoading(false);
    }
  }

  async function startEvaluation() {
  try {
    setStartingRun(true);
    setRunStatus("starting");

    const response = await fetch(
      `${API_URL}/evaluation-runs`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          dataset_id: 1,
          agent_version_id: Number(selectedVersion),
          max_test_cases:
            testCount === "full"
              ? null
              : Number(testCount)
        })
      }
    );

    if (!response.ok) {
      throw new Error("Could not start evaluation");
    }

    const data = await response.json();

    console.log("Evaluation started:", data);

    setActiveRun(data.evaluation_run_id);
    setRunStatus(data.status);

    pollEvaluation(data.evaluation_run_id);

  } catch (error) {
    console.error(error);
    setRunStatus("failed");
  } finally {
    setStartingRun(false);
  }
}

  async function pollEvaluation(runId) {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(
        `${API_URL}/evaluation-runs/${runId}`
      );

      if (!response.ok) {
        throw new Error("Could not check evaluation");
      }

      const data = await response.json();

      console.log(
        `Run ${runId} status:`,
        data.status
      );

      setRunStatus(data.status);

      if (
        data.status === "completed" ||
        data.status === "failed"
      ) {
        clearInterval(interval);

        if (data.status === "completed") {
          await loadDashboard();
        }
      }

    } catch (error) {
      console.error(error);
      clearInterval(interval);
      setRunStatus("failed");
    }
  }, 2000);
}

  function formatPercent(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    return `${(Number(value) * 100).toFixed(0)}%`;
  }

  function formatLatency(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    return `${(Number(value) / 1000).toFixed(2)}s`;
  }

  function formatCost(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    return `$${Number(value).toFixed(4)}`;
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon" aria-hidden="true"><span /></div>

          <div>
            <h2>ReleaseGuard</h2>
            <span>Evaluation console</span>
          </div>
        </div>

        <nav aria-label="Dashboard sections">
          <a className="nav-item active" href="#overview">Overview</a>
          <a className="nav-item" href="#evaluation">Run evaluation</a>
          <a className="nav-item" href="#recent-runs">Recent runs</a>
          <a className="nav-item" href="#comparison">Compare runs</a>
        </nav>

        <div className="sidebar-footer" role="status">
          <div
            className={
              backendStatus === "Connected"
                ? "status-dot connected"
                : "status-dot disconnected"
            }
          />

          <span>
            Backend: {backendStatus}
          </span>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div>
            <h1>Evaluation overview</h1>
            <p>
              Monitor AI agent quality and release readiness.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={loadDashboard}
          >
            Refresh
          </button>
        </header>

            <section className="evaluation-launcher" id="evaluation">
  <div>
    <h2>Run Evaluation</h2>

    <p>
      Test an agent version against the customer
      support dataset.
    </p>
  </div>

  <div className="evaluation-controls">
    <div className="control-group">
      <label htmlFor="agent-version">Agent Version</label>

      <select
        id="agent-version" value={selectedVersion}
        onChange={(event) =>
          setSelectedVersion(event.target.value)
        }
      >
        <option value={4}>
          Version 4 — Qwen3.5 4B
        </option>

        <option value={5}>
          Version 5 — Qwen3 1.7B
        </option>
      </select>
    </div>

    <div className="control-group">
      <label htmlFor="test-count">Test Cases</label>

      <select
        id="test-count" value={testCount}
        onChange={(event) =>
          setTestCount(event.target.value)
        }
      >
        <option value={1}>1 — Quick Test</option>
        <option value={2}>2 — Smoke Test</option>
        <option value={4}>4 — All Tests</option>
        <option value="full">Full Run</option>
      </select>
    </div>

    <button
      className="run-button"
      onClick={startEvaluation}
      disabled={
        startingRun ||
        runStatus === "pending" ||
        runStatus === "running"
      }
    >
      {runStatus === "pending" ||
      runStatus === "running"
        ? "Evaluation Running..."
        : "Run Evaluation"}
    </button>
  </div>

  {activeRun && (
    <div className="active-run" role="status">
      <div>
        <span>Run</span>
        <strong>#{activeRun}</strong>
      </div>

      <StatusBadge
        status={runStatus ?? "pending"}
      />
    </div>
  )}
</section>

        {loading ? (
          <div className="loading">
            Loading ReleaseGuard...
          </div>
        ) : (
          <>
            <section className="metrics" aria-labelledby="metrics-heading">
              <header className="metrics-header">
                <h2 id="metrics-heading">Latest completed run</h2>
              </header>
              <div className="metrics-grid">
              <MetricCard
                title="Response Accuracy"
                value={formatPercent(
                  latestSummary?.accuracy
                )}
                description="Normalized response correctness"
              />

              <MetricCard
                title="Tool Accuracy"
                value={formatPercent(
                  latestSummary?.tool_accuracy
                )}
                description="Correct tool selection"
              />

              <MetricCard
                title="Semantic Accuracy"
                value={formatPercent(
                  latestSummary?.semantic_accuracy
                )}
                description="Meaning-level correctness"
              />

              </div>
              <div className="metrics-grid secondary-metrics">
              <MetricCard
                title="Average Latency"
                value={formatLatency(
                  latestSummary?.average_latency_ms
                )}
                description="Average agent response time"
              />

              <MetricCard
                title="Tokens"
                value={
                  latestSummary?.total_tokens ??
                  "N/A"
                }
                description="Total model token usage"
              />

              <MetricCard
                title="Estimated Cost"
                value={formatCost(
                  latestSummary?.estimated_cost_usd
                )}
                description="Estimated run cost"
              />
            </div></section>

            <section className="panel" id="recent-runs">
              <div className="panel-header">
                <div>
                  <h2>Recent Evaluation Runs</h2>
                  <p>
                    Latest agent evaluation activity.
                  </p>
                </div>

                <span className="run-count">
                  {runs.length} total runs
                </span>
              </div>

              {runs.length === 0 ? (
                <div className="empty-state">
                  No evaluation runs found.
                </div>
              ) : (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Run</th>
                        <th>Dataset</th>
                        <th>Agent Version</th>
                        <th>Type</th>
                        <th>Status</th>
                      </tr>
                    </thead>

                    <tbody>
                      {[...runs]
                        .reverse()
                        .slice(0, 8)
                        .map((run, index) => {
                          const runId =
                            run.id ??
                            run.evaluation_run_id ??
                            index;

                          return (
                            <tr key={runId}>
                              <td>
                                #
                                {run.id ??
                                  run.evaluation_run_id ??
                                  "N/A"}
                              </td>

                              <td>
                                Dataset{" "}
                                {run.dataset_id ??
                                  "N/A"}
                              </td>

                              <td>
                                Version{" "}
                                {run.agent_version_id ??
                                  "N/A"}
                              </td>

                              <td>
                                <span className="run-type">
                                  {run.run_type ??
                                    "legacy"}
                                </span>
                              </td>

                              <td>
                                <StatusBadge
                                  status={
                                    run.status ??
                                    "unknown"
                                  }
                                />
                              </td>
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
            
            <RunComparison runs={runs} />

          </>
        )}
      </main>
    </div>
  );
}

function MetricCard({
  title,
  value,
  description
}) {
  return (
    <div className="metric-card">
      <p className="metric-title">
        {title}
      </p>

      <strong className="metric-value">{value}</strong>

      <span>{description}</span>
    </div>
  );
}

function StatusBadge({ status }) {
  return (
    <span
      className={`status-badge ${status}`}
    >
      {status}
    </span>
  );
}

export default App;