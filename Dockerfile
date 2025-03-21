#DockerFile
FROM python:3.10.0

#Allow statements and log messages to immediately appears in the logs
ENV PYTHONUNBUFFERED True
#Copy local code to the container image
ENV APP_HOME /back-end
WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

#Run the web service on the container startup. here we use gunicorn
#webserver, with one worker process and 8 threads
#for environments with multiple CPU cores , increase the number of workers
# to be equal to the cores available 
# timeout is set to 0 to disable the timeouts of the workers to allow cloud run to haandle instance scaling
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

