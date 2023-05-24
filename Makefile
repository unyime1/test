
# Build all services in production
build:
	docker-compose build

# Build all services in production
up:
	docker-compose up

# Delete all services in production
down:
	docker-compose down

# code formatting
lint:
	docker-compose run account sh -c 'flake8'

format:
	docker-compose run account sh -c 'python -m black --line-length 79 .'	


# Initailize aerich
init-db:
	docker-compose run account sh -c 'aerich init -t database.database.TORTOISE_ORM'
	docker-compose run account sh -c 'aerich init-db'


db-upgrade:
	docker-compose run account sh -c 'aerich upgrade'


test:
	docker-compose run account sh -c 'python -m pytest -v -s -p no:warnings'
