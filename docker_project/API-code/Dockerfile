FROM python:3.9-slim

WORKDIR /my_app
# this is inside the container
# naming the rootdirectory

COPY . /my_app/

#. is the source , /my_app/ is the destination - put everything itno rootdirectory of my container

RUN pip install --trusted-host pypi.python.org -r requirements.txt
# install all the stuff in the requirements file
#use the pypi (installation from pip) and use it without asking for permission

CMD [ "python", "reddit_code_exercise.py" ]
# start build with python, name workdir, copy it, make pip install in requirements, running script