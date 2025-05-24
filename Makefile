up-test:
	#bash -c '[[ ! -d logs ]] && mkdir logs'
	docker compose --env-file .env.test -p test -f docker-compose-test.yml up --build --abort-on-container-exit --exit-code-from test-runner --remove-orphans

up-pdb:
	docker compose -f docker-compose-test.yml --env-file .env.test -p test run -it --rm --build test-runner pytest -s tests/

up-dev:
	docker compose --env-file .env.dev -p dev -f docker-compose.yml up --build -d

