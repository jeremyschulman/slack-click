#!/usr/bin/env bash

uvicorn demo_app:api \
  --host 0.0.0.0 \
  --port ${SLACK_APP_PORT} \
  --reload
