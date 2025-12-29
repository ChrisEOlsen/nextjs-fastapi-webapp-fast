# FastAPI + Next.js Fullstack Template (MCP Enabled)

A modern, production-ready full-stack template featuring a **FastAPI** backend and **Next.js 15** frontend. This project is designed with an "AI-First" workflow in mind, integrating a **Model Context Protocol (MCP)** server to automate boilerplate generation and database management directly from your AI agent.

## 🚀 Features

*   **Backend:**
    *   **FastAPI**: High-performance, easy-to-learn web framework.
    *   **SQLAlchemy (Async)**: Modern ORM with async support.
    *   **PostgreSQL**: Robust relational database.
    *   **Alembic**: Database migration management.
    *   **MCP Integration**: Built-in tools to scaffold resources and manage DBs.
*   **Frontend:**
    *   **Next.js 15**: React framework for production.
    *   **Tailwind CSS 4**: Utility-first CSS framework.
    *   **Framer Motion**: Production-ready animation library.
*   **DevOps:**
    *   **Docker Compose**: Unified development environment.
    *   **Traefik Ready**: Pre-configured labels for Traefik reverse proxy.

## 🛠️ Project Structure

*   **`backend/`**: Python FastAPI application.
    *   `app/mcp_server.py`: The MCP server exposing tools to your agent.
    *   `app/templates/`: Jinja2 templates for code generation.
*   **`frontend/`**: Next.js application.
*   **`postgres_data/`**: Persistent storage for the database.

## 🏁 Getting Started

### Prerequisites

*   Docker & Docker Compose
*   Git
*   An external Docker network named `proxy` (or modify `docker-compose.yml` to remove the external network constraint).

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/ChrisEOlsen/mcp-fullstack-template.git
    cd mcp-fullstack-template
    ```

2.  **Configure Environment:**

    Create a `.env` file in the root directory. You can use the following template:

    ```env
    # User/Group ID for file permissions (run `id -u` and `id -g`)
    UID=1000
    GID=1000

    # Application Settings
    APP_NAME=myapp
    DOMAIN=myapp.localhost
    API_PREFIX=/api/v1
    
    # Database
    DB_USER=postgres
    DB_PASSWORD=secret
    
    # Security / Auth
    EXPECTED_HMAC_SECRET=supersecretkey
    BACKEND_URL=http://backend:80
    ```

3.  **Create the Proxy Network (if not exists):**
    
    This template assumes a Traefik setup. If you just want to run it locally without Traefik, remove the `networks` and `labels` sections from `docker-compose.yml` and expose ports directly.
    
    ```bash
    docker network create proxy
    ```

4.  **Build and Run:**

    ```bash
    docker compose up --build -d
    ```

    *   Frontend: `http://localhost:5173` (or via your configured Traefik domain)
    *   Backend Docs: `http://localhost/docs` (via Traefik) or check logs.

## 🤖 MCP Tools Integration

This project includes a Model Context Protocol (MCP) server running inside the backend container. This allows your AI assistant (like Gemini CLI) to perform complex tasks automatically.

### Configuration

Add the following to your Gemini CLI `settings.json` (or equivalent MCP client config) to register the tools:

```json
"default_api": {
  "command": "docker",
  "args": [
    "exec",
    "-i",
    "backend",
    "python",
    "-m",
    "app.mcp_server" 
  ]
}
```

### Available Tools

#### 1. `create_resource`

Scaffolds a complete vertical slice of the application (Database -> API -> Frontend).

*   **Usage:**
    ```bash
    create_resource <resource_name> <field1:type:required> <field2:type:required> ...
    ```
*   **Example:**
    ```bash
    create_resource "todo_item" "title:string:true" "is_completed:boolean:false" "due_date:datetime:false"
    ```
*   **What it generates:**
    *   **Backend:** SQLAlchemy Model, Pydantic Schema, CRUD utilities, API Endpoint.
    *   **Frontend:** API Client functions.
    *   **Wiring:** Automatically registers the new router in FastAPI.

#### 2. `apply_migrations`

Manages database schema changes using Alembic.

*   **Usage:**
    ```bash
    apply_migrations --message "Added todo_item table"
    ```
*   **What it does:**
    *   Detects changes in your SQLAlchemy models (including those created by `create_resource`).
    *   Generates a migration script.
    *   Applies the migration to the database immediately.

## 📝 Workflow Example

1.  **Plan a feature:** "I want a blog post system."
2.  **Scaffold:** 
    ```bash
    create_resource blog_post "title:string:true" "content:text:true" "published:boolean:false"
    ```
3.  **Migrate:** 
    ```bash
    apply_migrations --message "Add blog posts"
    ```
4.  **Develop:** The basic API and frontend hooks are now ready. You can now implement the UI components in `frontend/src/pages` using the generated API hooks.

## 📜 License

[MIT](LICENSE)