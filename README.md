# Recipe Base (recipe_base)

A recipes base site

## Running in docker-compose
```bash
docker-compose up -d
```


# Development


## Backend

### Install backend dependencies
```bash
pip install pipenv
pipenv install
```

### Run backend
```bash
pipenv run python3 manage.py runserver
```

## Frontend

### Install frontend dependencies
```bash
pnpm install
```

### Start frontend in development mode (hot-code reloading, error reporting, etc.)
```bash
quasar dev
```
