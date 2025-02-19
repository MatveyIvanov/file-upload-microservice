PROJECT_NAME=fileupload

localup:
	docker compose -f docker/docker-compose.local.yml up --remove-orphans
localbuild:
	docker compose -f docker/docker-compose.local.yml build --no-cache
developup:
	docker compose -f docker/docker-compose.yml up --remove-orphans
developbuild:
	docker compose -f docker/docker-compose.yml build --no-cache
mainup:
	docker compose -f docker/docker-compose.main.yml up --remove-orphans
mainbuild:
	docker compose -f docker/docker-compose.main.yml build --no-cache
test:
	docker exec -it $(PROJECT_NAME)-asgi pytest tests
lint:
	docker exec -it $(PROJECT_NAME)-asgi flake8 .
typecheck:
	docker exec -it $(PROJECT_NAME)-asgi mypy .
black:
	docker exec -it $(PROJECT_NAME)-asgi black .
isort:
	docker exec -it $(PROJECT_NAME)-asgi isort . --profile black --filter-files
migrations:
	docker exec -it $(PROJECT_NAME)-asgi alembic revision --autogenerate -m "$(MESSAGE)"
migrate:
	docker exec -it $(PROJECT_NAME)-asgi alembic upgrade head
