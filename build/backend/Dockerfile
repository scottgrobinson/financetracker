FROM python:3

COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

WORKDIR /usr/src/app

EXPOSE 8000
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000", "--debug"]
ENTRYPOINT ["/entrypoint.sh"]
