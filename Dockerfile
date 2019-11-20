# Use an official Python runtime as a parent image
FROM python:3

# Copy the current directory contents into the container at /app
ADD . /

# Set the working directory to /app
WORKDIR /Python

# Run pip install
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["python", "./Integration/fsm.py"]


FROM python:3.6-alpine

RUN adduser -D datagator

WORKDIR /home/datagator

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY index.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP index.py
RUN chown -R datagator:datagator ./
USER datagator

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]