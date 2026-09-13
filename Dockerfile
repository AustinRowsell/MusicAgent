# syntax=docker/dockerfile:1.7
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN addgroup --system musicagent && adduser --system --ingroup musicagent musicagent

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
COPY musicagent ./musicagent
COPY typings ./typings
COPY main.py ./main.py

RUN --mount=type=secret,id=musicagent_local_ca_bundle,target=/tmp/musicagent-local-ca-bundle.pem,required=false \
    if [ -s /tmp/musicagent-local-ca-bundle.pem ]; then \
      cp /tmp/musicagent-local-ca-bundle.pem /usr/local/share/ca-certificates/musicagent-local-ca-bundle.crt; \
      update-ca-certificates; \
    fi && \
    uv pip install --system --system-certs .

RUN mkdir -p /app/outputs /app/inputs && chown -R musicagent:musicagent /app

USER musicagent

EXPOSE 8000

CMD ["musicagent", "crews"]
