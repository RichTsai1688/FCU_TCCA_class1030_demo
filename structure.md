# Temperature Alert Feature Structure

## Function & Module Layout
- `monitor_temperature_threshold(date_range: Optional[str], equipment_ids: Optional[list[str]], threshold: Optional[float]) -> dict`
  - Entry-point `@function_tool`; orchestrates data fetch, threshold checks, alerting, and logging.
- `fetch_recent_readings(conn, equipment_ids, window_minutes) -> list[dict]`
  - Queries `equipment_data` for latest readings filtered by equipment ID and time window.
- `evaluate_temperature(readings, threshold, roc_limit) -> dict`
  - Computes current temperature status, delta, rate-of-change, and determines alert severity.
- `compile_correlated_metrics(readings) -> dict`
  - Summarizes vibration/current/runtime behavior around the alert window.
- `send_temperature_alert_email(alert_payload, email_config) -> bool`
  - Builds and dispatches SMTP email with contextual information.
- `append_alert_log_excel(alert_payload, log_path) -> None`
  - Appends alert metadata into Excel workbook using `pandas`/`openpyxl`.
- `load_monitor_config() -> MonitorConfig`
  - Reads `.env` to assemble thresholds, email recipients, polling intervals.
- `build_agent_response(alert_result) -> str`
  - Formats human-friendly summary for agent replies.

## Flow Overview
1. Agent calls `monitor_temperature_threshold(...)`.
2. Load configuration and normalize parameters.
3. Connect to MySQL and fetch recent sensor readings.
4. Evaluate readings against temperature/rate-of-change thresholds.
5. If alert triggered:
   - Enrich with correlated metrics.
   - Send email notification.
   - Log event in Excel workbook.
6. Return structured result plus agent response text.

## Mermaid Sequence Diagram
```mermaid
sequenceDiagram
    participant Agent
    participant Tool
    participant MySQL
    participant Email
    participant Excel

    Agent->>Tool: monitor_temperature_threshold(params)
    Tool->>Tool: load_monitor_config()
    Tool->>MySQL: fetch_recent_readings()
    MySQL-->>Tool: sensor dataset
    Tool->>Tool: evaluate_temperature()
    alt Alert Triggered
        Tool->>Tool: compile_correlated_metrics()
        Tool->>Email: send_temperature_alert_email()
        Email-->>Tool: status
        Tool->>Excel: append_alert_log_excel()
    end
    Tool-->>Agent: alert result + summary
```

## Mermaid Flowchart (UMF-style)
```mermaid
flowchart TD
    A[Start monitor_temperature_threshold] --> B[Load config & parameters]
    B --> C[Connect to MySQL]
    C --> D[Fetch recent readings]
    D --> E{Readings available?}
    E -- No --> Z[Return no-data response]
    E -- Yes --> F[Evaluate temperature & rate-of-change]
    F --> G{Alert condition met?}
    G -- No --> H[Build normal-status result]
    G -- Yes --> I[Compile correlated metrics]
    I --> J[Send email alert]
    J --> K[Append Excel log]
    K --> L[Merge alert metadata]
    H --> M[Build agent response]
    L --> M
    M --> N[Return result]
    N --> O[End]
```
