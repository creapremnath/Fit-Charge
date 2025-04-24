# Use a lightweight Python image
FROM python:3.12.9-bookworm
LABEL maintainer="creativepremnath@gmail.com"

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependency files first (to optimize caching)
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements-dev.txt /tmp/requirements-dev.txt

# Copy application and scripts
COPY ./app /app
COPY ./scripts /scripts

# Expose FastAPI default port
EXPOSE 8000

# Define build argument for development mode
ARG DEV=true

# Install dependencies
RUN python -m venv /py && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        gcc \
        python3-dev \
    && /py/bin/pip install --upgrade pip setuptools wheel && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements-dev.txt; \
    fi && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/* /tmp && \
    adduser --disabled-password --gecos "" fastapi-user && \
    mkdir -p /vol/web/media /vol/web/static && \
    chown -R fastapi-user:fastapi-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts


# Set the PATH to include virtual environment and scripts
ENV PATH="/scripts:/py/bin:$PATH"

# Switch to a non-root user
USER fastapi-user

# Define the default command to run the FastAPI app
CMD ["/scripts/run.sh"]
