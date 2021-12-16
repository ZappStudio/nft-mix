FROM node:lts

WORKDIR /var/www/app

COPY ./client .
COPY ./solidity/metadata/ ./static/metadata
COPY ./solidity/img ./static/img

CMD [ "yarn", "start" ]
