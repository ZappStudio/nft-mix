development:
	docker-compose -f docker-compose.yml -f docker-compose-development.yml up

development-down:
	docker-compose -f docker-compose.yml -f docker-compose-development.yml down

staging:
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml yarn install
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml yarn build
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml up --force-recreate

staging-down:
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml down
