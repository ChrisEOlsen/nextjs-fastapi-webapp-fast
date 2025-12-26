# Stage 1: Use the specified Node.js version on a minimal 'alpine' base
FROM python:3.10-slim

WORKDIR /mcp

# Copy project definition
COPY pyproject.toml .

# Install uv
RUN pip install uv

# Compile and install dependencies using uv (split into two steps for /bin/sh compatibility)
RUN uv pip compile pyproject.toml -o requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the application code
COPY ./app ./app

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]