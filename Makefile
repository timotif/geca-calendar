IMG = geca-calendar
NAME = geca-calendar
PORT = 8001
APP_PATH = ./app
ENV_FILE = .env
DB_PATH = /var/lib/geca_calendar
LOG_PATH = /var/log/geca_calendar
CALENDARS_PATH = $(APP_PATH)/calendars

all: help

build:
	@docker build -t $(IMG) $(APP_PATH) --build-arg PORT=$(PORT)

run:
	@docker run -d --rm \
	--env-file $(ENV_FILE) \
	--env PORT=$(PORT) \
	-p $(PORT):$(PORT) \
	-v $(DB_PATH):/app/instance \
	-v $(LOG_PATH):/app/log \
	-v $(CALENDARS_PATH):/app/calendars \
	--name $(NAME) $(IMG)

stop:
	@docker stop $(NAME)

migrate:
	@echo "Creating new migration..."
	@docker exec $(NAME) flask db migrate
	@echo "Applying migration..."
	@docker exec $(NAME) flask db upgrade

init-db:
	@echo "Creating database..."
	@docker exec $(NAME) flask db init
	@make migrate -s

reset-migrations:
	@echo "Removing migrations..."
	@rm -rf $(APP_PATH)/migrations
	@make init-db -s

force-db-update:
	@echo "Forcing database update..."
	@echo "Make sure that the container is running"
	@docker exec $(NAME) echo "app.calendar.update_calendar(force_update=True)" | flask shell

clean:
	@docker stop $(NAME)
	@docker rm $(NAME)

fclean: clean
	@docker rmi $(IMG)

shell:
	@docker exec -it $(NAME) /bin/bash

logs:
	@docker logs $(NAME)

logs-follow:
	@docker logs -f $(NAME)

help:
	@echo "build: build the docker image"
	@echo "run: run the docker container"
	@echo "update: force update the calendar"
	@echo "stop: stop the docker container"
	@echo "shell: open a shell in the docker container"
	@echo "logs: show the logs of the docker container"
	@echo "logs-follow: show the logs of the docker container and follow the output"
	@echo "init-db: create the database and apply the migrations"
	@echo "migrate: create and apply a new migration"
	@echo "reset-migrations: remove the migrations and create a new database"
	@echo "force-db-update: force the update of the database"
	@echo "clean: stop and remove the docker container"
	@echo "fclean: stop and remove the docker container and remove the docker image"
	@echo "help: show this message"

update:
	@docker exec $(NAME) /bin/bash -c "python calendar_updater.py"

.PHONY: build run stop shell logs logs-follow init-db migrate reset-migrations force-db-update clean fclean help update