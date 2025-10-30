# Temperature Alert Function Tool Plan

## Objectives
- Enable real-time temperature change monitoring on table `equipment_data` with configurable user thresholds.
- Package the monitoring workflow as an `@function_tool` so existing agents can invoke it.
- Deliver email-based alerting, Excel logging, and analytics linking high temperature events to other sensor values.
- Prepare integrations that support future frontend/backend development.

## Scope & Assumptions
- Use the existing MySQL data source (`Time`, `Temperature(°C)`, `Vibration(mm/s)`, `Current(A)`, `Runtime(hr)`, `Equipment_ID`).
- Polling cadence driven by agent requests or scheduled orchestration; real-time means “near real-time” with minute-level polling.
- Email alerts sent via SMTP using credentials stored in `.env`; assumes outbound mail allowed.
- Excel logs stored in workspace (e.g., `logs/temperature_alerts.xlsx`).
- Python 3.12 environment with `mysql-connector-python`, `pandas`, `openpyxl`, `python-dotenv`, `smtplib` available.

## Deliverables
1. New `@function_tool` (e.g., `monitor_temperature_threshold`) callable by agents.
2. Email notification helper supporting customizable recipients, subject/body templating, and optional attachments.
3. Analytics module recommending algorithms to correlate temperature spikes with other metrics.
4. Excel logging utility capturing each alert with metadata and summary metrics.
5. Integration notes for future frontend/backend teams.

## Implementation Plan

### Phase 1 – Design & Config
- Confirm SMTP settings, email recipients, and alert threshold schema (single numeric vs. per-equipment).
- Extend `.env` / `.env.example` with mail and monitoring settings (e.g., `TEMP_THRESHOLD`, `SMTP_HOST`, `ALERT_RECIPIENTS`).
- Decide on polling vs. on-demand execution strategy; design agent prompt addition describing new capability.

### Phase 2 – Data Access & Threshold Logic
- Implement repository helper to fetch latest readings (ordered by `Time`) and compare against thresholds.
- Support dynamic thresholds: default from env, optional override via function arguments (temperature limit, rate-of-change limit).
- Return structured payload (status, metrics, recent readings) for agent consumption even when no alert triggers.

### Phase 3 – Alerting Workflow
- Build email utility using `smtplib` + `email.message.EmailMessage`; include recent readings and summary statistics.
- Allow enabling/disabling email delivery via env flag for testing.
- Implement retry/backoff and error logging so the agent can report failures gracefully.

### Phase 4 – Analytics Enhancements
- When high temperature detected, fetch correlated metrics (`Vibration(mm/s)`, `Current(A)`, `Runtime(hr)`).
- Compute quick features (Pearson correlation, rolling averages, z-scores) and package summary for agent.
- Recommend deeper analytics options (e.g., multivariate regression, anomaly detection with Isolation Forest, Granger causality).

### Phase 5 – Excel Alert Log
- Use `pandas` (with `openpyxl`) to append alert entries into `logs/temperature_alerts.xlsx`.
- Columns: timestamp detected, equipment ID, temperature, other metrics, threshold, email status, correlation stats, notes.
- Ensure file creation is atomic (temp file swap) and thread-safe locking if concurrent triggers expected.

### Phase 6 – Agent Integration
- Register function tool in both `connect_mysql_openai.py` and `connect_mysql_ollama.py`.
- Update agent system prompt to mention temperature alert capability and required parameters.
- Provide helper response templates so LLM returns concise alert summaries to end users.

### Phase 7 – Documentation & Tests
- Update README with setup instructions (ENV vars, required packages, usage examples).
- Add docstring and inline comments explaining key pieces.
- Write unit/integration tests covering threshold comparison logic, email formatting, Excel logging append.

## Recommended Algorithms & Analytical Approaches
- **Correlation Analysis**: Pearson/Spearman correlation between temperature and other metrics over rolling windows.
- **Time-Series Regression**: Linear regression or ARIMA with exogenous variables (temperature as dependent variable).
- **Anomaly Detection**: Z-score thresholding; optionally Isolation Forest or LOF on multivariate sensor data.
- **Trend Detection**: Rolling slope (simple linear regression over recent readings) to flag accelerating temperature rise.

## Excel Log Structure
- Sheet `AlertLog` with headers: `DetectedAt`, `EquipmentID`, `TempC`, `Threshold`, `DeltaSinceLast`, `Vibration`, `Current`, `Runtime`, `CorrelationSummary`, `EmailSent`, `Notes`.
- Optional Sheet `Summary` aggregating alert counts per equipment, daily counts, and latest threshold settings.
- Consider pivot-table template for future frontend export.

## Frontend / Backend Integration Suggestions
- **Backend API**: Expose REST endpoints (`/alerts/latest`, `/alerts/history`, `/alerts/config`) or WebSocket for live updates. Structure responses using the same payload from the function tool.
- **Event Bus**: Emit alert events (JSON) to a message broker (e.g., Redis, MQTT) for downstream services.
- **Frontend Hooks**: Provide components for threshold management UI, alert timeline, and correlation charts. Offer standard JSON schema for easy binding.
- **Authentication**: Plan JWT or API key validation for future alert configuration endpoints.
- **Logging/Monitoring**: Centralize alert logs in SQL or cloud storage eventually; Excel remains for quick auditing/export.

## Risks & Mitigations
- **SMTP Failure**: Implement fallback logging and retry queue; notify user through agent response.
- **Data Lag**: If polling interval misses rapid spikes, introduce change-rate thresholds or consider CDC/Webhooks.
- **Excel Corruption**: Use file locks and periodic archival; provide CLI to rebuild log from database source if needed.
- **LLM Misuse**: Constrain function tool schema (explicit parameters, validation) to prevent accidental mass email sends.

## Next Steps
1. Align on threshold management requirements and SMTP credentials.
2. Implement Phases 1–3 as MVP, verify with manual trigger.
3. Layer analytics, logging, and documentation.
4. Review integration points with future frontend/backend stakeholders.
