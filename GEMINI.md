# Gemini CLI Guidelines for Frontend Scaffolding

When using the `mcp` tools, observe the following:

### `create-frontend-page` and `create-frontend-component`:

These tools generate **minimal scaffolding code** only. After their execution, you **must proceed to implement the user's full request** by filling in the generated page or component with the necessary UI elements, logic, and styling. Do not consider the task complete after just scaffolding.

### API Resource Integration (`create-api-client`):

When integrating API resources into a page or component using the `create-api-client` tool, pay close attention to the user's requirements for the new feature:

*   **Determine required API operations:** Assess whether the requested feature necessitates `GET`, `CREATE`, `UPDATE`, or `DELETE` functionality (or a subset thereof).
*   **Default API availability:** The `create-resource` tool generates a backend API with all CRUD operations. However, the frontend implementation (via `create-api-client`) should only expose the operations explicitly or implicitly required by the user's feature request.

### Clarification and Insufficient Information:

If the user's prompt provides **insufficient information** to fully implement the requested feature (e.g., unclear UI design, ambiguous data interaction, missing styling details), you **must request clarification** from the user. Do not make assumptions beyond what the `mcp` tools provide as boilerplate.

### Standard Operating Procedures (SOP)

To ensure robustness and avoid common errors, follow this workflow:

1.  **Backend Resource Creation**:
    *   When adding a new data model, use `create_resource`.
    *   **IMMEDIATELY** follow this with `apply_migrations` to update the database schema. The system is configured for autodiscovery, so no manual file edits are needed for `env.py`.

2.  **Quality Assurance (Audit)**:
    *   The most common error is `422 Unprocessable Entity` due to mismatches between Frontend payloads and Backend Pydantic schemas.
    *   **MANDATORY:** After implementing the frontend API calls, run the `audit_resource` tool for the relevant resource.
    *   Fix any issues flagged by the audit (e.g., missing fields, camelCase vs snake_case mismatches) *before* declaring the task complete.

3.  **Error Investigation**:
    *   If you encounter issues or uncertain behavior, use the `read_logs` tool.
    *   Filter for `ERROR` level first (`read_logs(level="ERROR")`) to identify system or application crashes.
    *   Note: The logs are configured to capture all backend errors, including Uvicorn startup/shutdown (which will appear as INFO) and internal server errors.

### Unnecessary Steps During Development Mode
This tech stack makes use of Hot Module Replacement (HMR). You generally do *not* need to restart containers for code changes.
*   **Frontend**: Updates automatically.
*   **Backend**: Updates automatically via Uvicorn reload.
*   **Only rebuild** if you modify `Dockerfile` or `package.json` dependencies: `docker compose up -d --build <container-name>`