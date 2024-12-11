#!/bin/bash
CALENDAR_PATH=app

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

python ${CALENDAR_PATH}/calendar_updater.py