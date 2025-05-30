## Local DEV

### psql

```bash
docker exec -it fastapi_pg_websocket_db bash
PGPASSWORD=mypass psql -h localhost -U myuser -d mydb

docker exec -it fastapi_pg_websocket_db bash -c 'PGPASSWORD=mypass psql -h localhost -U myuser -d mydb'
```

### Follow logs

```bash
docker compose -p dev logs -f
```

### Running tests

```bash
make up-test
```

```bash
pytest tests/test_listener.py
# with logging enabled
LOGGING_ENABLED=true LOGGING_CONFIG=logging.test.yml pytest tests/test_listener.py
```
