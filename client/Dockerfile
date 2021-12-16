FROM node:lts

WORKDIR /var/www/app

COPY ./client .
COPY ./solidity/metadata/ ./static/metadata
COPY ./solidity/img ./static/img

RUN yarn install \
      --prefer-offline \
      --pure-lockfile \
      --non-interactive \
      --production=true \

RUN yarn build

CMD [ "yarn", "start" ]
