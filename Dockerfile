FROM python:3.12.9-slim
LABEL maintainer="creativepremnath@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements-dev.txt /tmp/requirements-dev.txt
COPY ./app /app
COPY ./scripts /scripts

EXPOSE 8000

ARG DEV=true

RUN python -m venv /py && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        gcc \
        python3-dev && \
    /py/bin/pip install --upgrade pip setuptools wheel && \
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

ENV PATH="/scripts:/py/bin:$PATH"

USER fastapi-user

CMD ["/scripts/run.sh"]
