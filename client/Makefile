development:
	yarn install
	docker-compose -f docker-compose.yml -f docker-compose-development.yml up

development-down:
	docker-compose -f docker-compose.yml -f docker-compose-development.yml down

staging:
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml nuxt yarn install
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml nuxt yarn build
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml up -d --force-recreate

staging-down:
	docker-compose -f docker-compose.yml -f docker-compose-staging.yml down
