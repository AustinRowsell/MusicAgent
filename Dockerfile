FROM python:3.13-slim

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

RUN uv pip install --system .

RUN mkdir -p /app/outputs /app/inputs && chown -R musicagent:musicagent /app

USER musicagent

EXPOSE 8000

CMD ["musicagent", "crews"]
