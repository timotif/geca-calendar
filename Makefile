IMG = geca-calendar
NAME = geca-calendar
PORT = 8080
ENV_FILE = notion_2425.env

build:
	docker build --progress=plain -t $(IMG) .

run:
	docker run -d --env-file $(ENV_FILE) -p $(PORT):$(PORT) --name $(NAME) $(IMG)

clean:
	docker stop $(NAME)
	docker rm $(NAME)

fclean: clean
	docker rmi $(IMG)