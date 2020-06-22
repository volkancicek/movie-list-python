FROM python:3.6.5-alpine
MAINTAINER Volkan Cicek "volkancicek@outlook.com"
COPY . .
WORKDIR ./src
RUN pip install -r requirements.txt
RUN pytest
ENTRYPOINT ["python"]
CMD ["movie_app/app.py"]
