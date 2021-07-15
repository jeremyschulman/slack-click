#!/usr/bin/env bash

if [[ -z "$SLACK_APP_PORT" ]]; then
  echo "Missing $SLACK_APP_PORT" && exit
fi

uvicorn clicker:api --host 0.0.0.0 --port ${SLACK_APP_PORT} --reload
