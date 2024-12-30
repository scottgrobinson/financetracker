FROM node:22-alpine AS build

RUN apk update \
 && apk add nano

COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

WORKDIR /usr/src

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
ENTRYPOINT ["/entrypoint.sh"]
