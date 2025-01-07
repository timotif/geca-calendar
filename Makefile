IMG = geca-calendar
NAME = geca-calendar
PORT = 8001
APP_PATH = ./app
ENV_FILE = .env
DB_PATH = /var/lib/geca_calendar
LOG_PATH = /var/log/geca_calendar

all: help

build:
	docker build -t $(IMG) $(APP_PATH)

run:
	@docker run -d --rm \
	--env-file $(ENV_FILE) \
	-p $(PORT):$(PORT) \
	-v $(DB_PATH):/app/instance \
	-v $(LOG_PATH):/app/log \
	--name $(NAME) $(IMG) 

stop:
	docker stop $(NAME)

clean:
	docker stop $(NAME)
	docker rm $(NAME)

fclean: clean
	docker rmi $(IMG)

shell:
	docker exec -it $(NAME) /bin/bash

help:
	@echo "build: build the docker image"
	@echo "run: run the docker container"
	@echo "stop: stop the docker container"
	@echo "shell: open a shell in the docker container"
	@echo "clean: stop and remove the docker container"
	@echo "fclean: stop and remove the docker container and remove the docker image"
	@echo "help: show this message"

.PHONY: build run stop clean fclean help