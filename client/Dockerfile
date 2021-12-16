FROM node:lts

WORKDIR /var/www/app

COPY ./client .
COPY ./solidity/metadata/ ./static/metadata
COPY ./solidity/img ./static/img

RUN yarn install
RUN yarn build

CMD [ "yarn", "start" ]
