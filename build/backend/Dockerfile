FROM python:3

RUN apt-get update \
 && apt-get install -y \
    nano \
  && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

WORKDIR /usr/src/app

EXPOSE 8000
CMD ["python", "-u", "__init__.py"]

ENTRYPOINT ["/entrypoint.sh"]
