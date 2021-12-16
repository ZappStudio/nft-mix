FROM node:lts

WORKDIR /var/www/app

RUN yarn install
RUN yarn build

COPY ./client .
COPY ./solidity/metadata/ ./static/metadata
COPY ./solidity/img ./static/img

CMD [ "yarn", "start" ]
