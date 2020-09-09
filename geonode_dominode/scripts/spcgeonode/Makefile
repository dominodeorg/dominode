
build:
	@docker-compose build

up:
	@docker-compose up -d

down:
	@docker-compose down

logs:
	@docker-compose logs -f $(or ${SERVICE},django)

shell:
	@docker-compose exec $(or ${SERVICE},django) /bin/sh

collectstatic:
	@docker-compose exec django ./manage.py collectstatic --noinput
