up-test:
	docker compose --env-file .env.test -p test -f docker-compose-test.yml up --build --abort-on-container-exit --exit-code-from test-runner --remove-orphans

up-pdb:
	docker compose -f docker-compose-test.yml --env-file .env.test -p test run -it --rm --build test-runner pytest -s tests/

up-dev:
	docker compose --env-file .env.dev -p dev -f docker-compose.yml up --build -d

down-dev:
	docker compose -p dev down

logs-dev:
	docker compose -p dev logs -f

db-shell:
	@docker exec -it fastapi_pg_websocket_db bash -c 'PGPASSWORD=mypass psql -h localhost -U myuser -d mydb'

##############
# Migrations #
##############
.PHONY: migrations-new
migrations-new:
	@echo "-----------------------"
	@echo "- ⛃ Migrations: New ⛃ -"
	@echo "-----------------------"

	@read -p "Message: " message; \
	docker exec -it fastapi_pg_websocket_rest alembic revision --autogenerate -m "$$message"

.PHONY: migrations-upgrade
migrations-upgrade:
	@echo "---------------------------"
	@echo "- ⛃ Migrations: Upgrade ⛃ -"
	@echo "---------------------------"

	docker exec -it fastapi_pg_websocket_rest alembic upgrade head

.PHONY: migrations-downgrade
migrations-downgrade:
	@echo "-----------------------------"
	@echo "- ⛃ Migrations: Downgrade ⛃ -"
	@echo "-----------------------------"

	docker exec -it fastapi_pg_websocket_rest alembic downgrade head-1
