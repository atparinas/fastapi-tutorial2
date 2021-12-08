## CHEAT SHEET


Alembic Create Migration
```sh
alembic revision -m "create_main_tables"
```

Apply Migration
```sh
alembic upgrade head
```

Alembic Rollback Migration
```sh
alembic downgrade base
```