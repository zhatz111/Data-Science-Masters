FROM python:3.11
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
EXPOSE 8001
RUN pip install -r requirements.txt
CMD ["python", "final-project-api.py"]