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

Best way to create secret key
```sh
openssl rand -hex 32
```

Required .env content
```sh
SECRET_KEY=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_SERVER=
DATABASE_PORT=
DATABASE_DB=
```