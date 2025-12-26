# Vite JS + FastAPI Web App Template

This is a template for creating a simple web application with a ViteJS frontend and a FastAPI backend. It is designed to be easily deployable on a home server with Traefik as a reverse proxy.

## Tech Stack

*   **Frontend:**
    *   [Vite](https://vitejs.dev/)
    *   [Vanilla JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
*   **Backend:**
    *   [FastAPI](https://fastapi.tiangolo.com/)
    *   [SQLAlchemy](https://www.sqlalchemy.org/)
    *   [Pydantic](https://pydantic-docs.helpmanual.io/)
    *   [SQLite](https://www.sqlite.org/index.html)
*   **Infrastructure:**
    *   [Docker](https://www.docker.com/)
    *   [Traefik](https://traefik.io/traefik/)

## Getting Started

### Prerequisites

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   A Traefik instance running with a network named `proxy`.

### Installation

1.  Clone the repository:

    ```bash
    git clone <repository-url>
    ```

2.  Navigate to the project directory:

    ```bash
    cd vite-js-fastapi-webapp
    ```

3.  Create a `.env` file and set the `DOMAIN` variable to the domain you want to use for the application.

    ```bash
    cp .env.example .env
    ```

4.  Start the application:

    ```bash
    docker-compose up -d
    ```

The application will be available at the domain you specified in the `.env` file.