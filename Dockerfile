# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

ARG ENVIRONMENT=production

ENV ENVIRONMENT=${ENVIRONMENT} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.6.1
  

# System deps:
#RUN curl -sSL https://install.python-poetry.org | python3 - \
#    wait 1000
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN --mount=type=cache,target=/var/cache/pypoetry \
    poetry install --no-interaction --no-ansi
    #poetry install $(test "$ENVIRONMENT" == production && echo "--only=main") --no-interaction --no-ansi
    


# Creating folders, and files for a project:
COPY ./src /code
# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    # --home "/nonexistent" \
    --shell "/sbin/nologin" \
    # --no-create-home \
    --uid "${UID}" \
    appuser

# COPY --chown=appuser:appuser src/ .
# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install poetry \
#     poetry build

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.


# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD uvicorn 'ollama_rag_de.server:app' --host=0.0.0.0 --port=8000
