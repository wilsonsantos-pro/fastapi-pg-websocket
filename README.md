## Local DEV

### psql

```bash
PGPASSWORD=mypass psql -h localhost -U myuser -d mydb
```

### Follow logs

```bash
docker compose -p dev logs -f
```
