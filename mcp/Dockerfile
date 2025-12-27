FROM python:3.10-slim

WORKDIR /app

# First, install all dependencies as the root user
RUN pip install uv
COPY pyproject.toml .
RUN uv pip compile pyproject.toml -o requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

# Create a non-root user with the same UID and GID as the host
# Also, add the user to the docker group to allow socket access
ARG UID=1000
ARG GID=1000
ARG DOCKER_GID=984
RUN groupadd --gid $GID user && \
    groupadd --gid $DOCKER_GID docker && \
    useradd --uid $UID --gid $GID --groups docker -m user

# Now, copy the application code and set permissions
COPY --chown=user:user ./app /app/app
COPY --chown=user:user ./templates /app/templates

# Switch to the non-root user
USER user

ENV PYTHONPATH=/app

CMD ["python", "app/server.py"]