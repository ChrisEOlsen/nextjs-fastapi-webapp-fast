FROM python:3.10-slim

# 1. Install 'uv' directly from its official image
# This copies a single static binary. It's tiny and instant.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /code

# 2. Copy ONLY the project definition first (for Docker caching)
COPY pyproject.toml .

# 3. Use uv to resolve and install dependencies system-wide
# We compile the TOML to a requirements list in memory, then install it.
# --system: Installs to Python's global environment (so no venv needed inside Docker)
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt

# 4. Copy the application code
COPY ./app ./app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]