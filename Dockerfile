FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

ENV MC_SERVER_HOST=${MC_SERVER_HOST}
ENV MC_SERVER_PORT=${MC_SERVER_PORT}
ENV BOT_TOKEN=${BOT_TOKEN}
ENV DATABASE_URL=${DATABASE_URL}
ENV CHECK_INTERVAL_SECONDS=${CHECK_INTERVAL_SECONDS}

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen
COPY . .

EXPOSE 8000

CMD ["uv", "run", "src/main.py"]