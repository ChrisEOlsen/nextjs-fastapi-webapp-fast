# Use an official Python runtime as a parent image
FROM python:3.10-slim

# 1. Install 'uv' by copying the static binary from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory in the container
WORKDIR /app

# 2. Copy only the dependency definition file first to leverage Docker cache
COPY pyproject.toml .

# 3. Compile and install third-party dependencies from pyproject.toml
# This step is cached and only re-runs if pyproject.toml changes.
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt

# 4. Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser

# 5. Copy the application code into the container
# This is done *after* installing dependencies to optimize caching.
COPY ./app /app/app
COPY ./templates /app/templates

# 6. Install the local application itself. This will be fast as dependencies are already installed.
RUN uv pip install --system --no-cache .

# 7. Switch to the non-root user
USER appuser

# The command to run the CLI application.
ENTRYPOINT ["python", "-m", "app.main"]
