# Migration Instructions

- Install dependencies
  - **uv add alembic**
  - **uv add pymysql**
  - **uv add sqlalchemy**
  - **uv add cryptography**

- Handle alembic init
  - **uv run alembic init --template pyproject alembic**
    - this command creates:
      - alembic/
      - alembic/script.py.mako
      - alembic/env.py
      - alembic/versions
      - alembic/README
    - alembic.ini
    - edits and appends to the pyproject.toml file

  - within the alembic.ini file
    - find sqlalchemy.url and set the value to the pymql docker-compose connection string
      - example: **mysql+pymysql://weather_user:weather_password@mysql:3306/weather**

  - create migrations revisions
    - **uv run alembic revision -m "create hourly weather aggregates table"**
      - creates a file in the alembic/versions folder whose name is based on the string above
    - **uv run alembic revision -m "create zipcodes table"**

    - within those files implement the **def upgrade()**
      - since this is the first revision, these files just define how to create the tables if they don't already exist

- Docker
  - create a new Dockerfile
    - Dockerfile.migrate
      - it's job is to create an image that installs all the tools needed to run alembic
    - Create a new service within the existing docker-compose file
      - the service was labled **migrate** within the docker-compose file
    - execute the new service:
      - command: **docker-compose up migrate --remove-orphans**
        - this command only needs to be run once to create the tables in the database
        - to start the webserver continue to use the **dc** alias
      - **migrate** depends on mysql, therefore the sql image is started
      - after the service is live alembic commands within the Dockerfile are executed which call the code written in **def upgrade**
      - new tables are created within the sql image if they don't exist
            
