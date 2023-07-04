# Dockerfile
FROM python:3.9
WORKDIR /usr/src/searchapp

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install  --no-cache-dir -r requirements.txt

COPY ./css/* ./css/
COPY ./js/* ./js/
COPY ./templates/* ./templates/


ENV FLASK_APP=app
CMD ["python","./app.py"]	
CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:8000", "main:app"]
