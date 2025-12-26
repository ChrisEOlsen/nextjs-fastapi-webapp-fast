# Development Workflow

This document outlines the common commands and workflow for developing with this Vite + FastAPI template.

## Initial Project Setup

These steps are only necessary the first time you set up the project locally.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment using uv:**
    ```bash
    uv venv
    ```

3.  **Activate the virtual environment:**
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows (PowerShell):
        ```powershell
        .venv\Scripts\Activate.ps1
        ```

4.  **Install all dependencies from the lock file:**
    ```bash
    uv pip sync
    ```

## Everyday uv Commands Cheatsheet

`uv` is a fast Python package installer and resolver. Here are some common commands you'll use daily:

*Note: Always ensure you are in the `backend` directory and your virtual environment is activated when running these commands locally.*

1.  **Create a Virtual Environment:**
    If you ever need to create a new virtual environment (e.g., if you deleted the `.venv` folder):
    ```bash
    uv venv
    ```

2.  **Activate Virtual Environment:**
    (As mentioned in Initial Setup, but good for a reminder):
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows (PowerShell):
        ```powershell
        .venv\Scripts\Activate.ps1
        ```

3.  **Install/Sync Dependencies from `uv.lock`:**
    To install all dependencies listed in `uv.lock` (or keep your environment in sync with it):
    ```bash
    uv pip sync
    ```
    Use `uv pip install <package>` to add additional packages to your virtual environment without modifying `pyproject.toml` or `uv.lock` (useful for testing, but typically prefer `uv add` for project dependencies).

4.  **Add a New Dependency (and update `pyproject.toml` & `uv.lock`):
    To add a new package to your project and automatically update `pyproject.toml` and `uv.lock`:
    ```bash
    uv add <package-name>

    # Example: Add a new testing library
    uv add pytest
    ```

5.  **Remove a Dependency (and update `pyproject.toml` & `uv.lock`):
    To remove an existing package from your project and automatically update `pyproject.toml` and `uv.lock`:
    ```bash
    uv remove <package-name>

    # Example: Remove an unused library
    uv remove unused-package
    ```

6.  **Update an Existing Dependency (and `uv.lock`):
    To update a specific package to its latest compatible version, and update `uv.lock`:
    ```bash
    uv update <package-name>

    # Example: Update FastAPI
    uv update fastapi
    ```
    To update all packages to their latest compatible versions:
    ```bash
    uv update
    ```

7.  **Run a Command in the Virtual Environment:**
    To execute a command or script using the Python interpreter and packages from your active virtual environment, without explicitly activating it:
    ```bash
    uv run <command>

    # Example: Run Alembic (when not using `source .venv/bin/activate`)
    uv run alembic revision --autogenerate -m "Initial migration"

    # Example: Run tests
    uv run pytest
    ```

8.  **Lock Dependencies without Installing:**
    If you only want to resolve and pin dependencies in `uv.lock` without installing them (e.g., in CI):
    ```bash
    uv lock
    ```

9.  **Uninstall all packages:**
    To remove all installed packages from the current virtual environment:
    ```bash
    uv pip uninstall --all
    ```

## Running the Backend Development Server

To run the FastAPI server with live reloading:

1.  Make sure you are in the `backend` directory and your virtual environment is activated.

2.  Start the server:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

## Database Migrations (Alembic)

Alembic acts like "git for your database." You'll use it to manage changes to your database schema.

**First-Time Setup for Alembic (Do this once):**
Before running migrations, you need to initialize Alembic and configure it.
*Note: The agent has already performed these steps.*
1. `cd backend`
2. `alembic init alembic`
3. Configure `alembic.ini` and `alembic/env.py`.

### Common Alembic Commands

**1. Creating a New Migration**

Whenever you change a SQLAlchemy model (e.g., add a column in `app/models/user.py`), you must generate a migration script.

```bash
# Make sure your DATABASE_URL is set in your environment
alembic revision --autogenerate -m "A short, descriptive message about the change"

# Example:
alembic revision --autogenerate -m "Add phone_number to User model"
```
This command compares your models against the database and generates a new script in the `backend/alembic/versions/` directory. **Always inspect the generated script** to ensure it's correct.

**2. Applying Migrations**

To run the migration scripts and update your database to the latest version:

```bash
alembic upgrade head
```
It's good practice to run this after pulling new changes from source control.

**3. Checking Migration Status**

To see the current migration version of your database:

```bash
alembic current
```

To see the full history of migrations and which ones have been applied:

```bash
alembic history --verbose
```

**4. Downgrading a Migration**

To revert the most recent migration:

```bash
alembic downgrade -1
```

To revert to a specific migration version, you can use the version identifier from `alembic history`:

```bash
alembic downgrade <version_identifier>
```
