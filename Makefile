IMG = geca-calendar
NAME = geca-calendar
PORT = 8001
APP_PATH = ./geca_calendar
ENV_FILE = .env

build:
	docker build -t $(IMG) $(APP_PATH)

run:
	docker run -d --env-file $(ENV_FILE) -p $(PORT):$(PORT) --name $(NAME) $(IMG)

clean:
	docker stop $(NAME)
	docker rm $(NAME)

fclean: clean
	docker rmi $(IMG)