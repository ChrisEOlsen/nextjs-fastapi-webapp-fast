FROM python:3.10-slim

WORKDIR /mcp

# Copy project definition
COPY pyproject.toml .
RUN pip install uv

# Install dependencies (including the new 'mcp' package)
RUN uv pip compile pyproject.toml -o requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the application code AND templates
COPY ./app ./app
COPY ./templates ./templates 

ENV PYTHONPATH=/mcp

# Use the MCP server script by default
CMD ["python", "app/server.py"]