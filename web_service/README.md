## Deployment instructions

1. Clone repo
2. cd to `web_service`
2. edit `envrc.dev` file
3. source `envrc.dev` file
4. create directory `secrets`
5. create following files in `secrets` directory: `touch secrets/{DB_HOST,DB_PORT,DB_PROJECT_PASS,DB_PROJECT_US
ER,POSTGRES_DB,POSTGRES_PASSWORD,POSTGRES_USER,PROJECT_NAME}`
6. Enter data to created files
7. Build docker images with `docker-compose build`
8. Run docker images in detached mode with `docker-compose up -d`
9. Apply all database migrations: `docker-compose exec -T fastapi entrypoint_inject.sh alembic upgrade head`
10. Open API DOCS page URL: `{HOST}:{FASTAPI_PORT}/docs`
