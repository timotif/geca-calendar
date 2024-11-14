#!/bin/bash
CALENDAR_PATH=geca_calendar

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

python ${CALENDAR_PATH}/calendar_updater.py