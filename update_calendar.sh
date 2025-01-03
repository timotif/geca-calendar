#!/bin/bash
CALENDAR_MODULE=app

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

python -m ${CALENDAR_MODULE}.calendar_updater