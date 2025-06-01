FROM python:3.12-alpine
LABEL maintainer="creativepremnath@gmail.com"

ENV PYTHONUNBUFFERED=1 \
    PATH="/scripts:/py/bin:$PATH"

WORKDIR /app

# Install minimal system dependencies
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    python3-dev \
    musl-dev

# Set up virtual environment
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip setuptools wheel

# Copy project files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements-dev.txt /tmp/requirements-dev.txt
COPY ./app /app
COPY ./scripts /scripts

# Install Python dependencies
ARG DEV=true
RUN /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements-dev.txt; \
    fi

# Setup user and permissions
RUN adduser -D fastapi-user && \
    mkdir -p /vol/web/media /vol/web/static && \
    chown -R fastapi-user:fastapi-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

USER fastapi-user

EXPOSE 8000

CMD ["/scripts/run.sh"]
