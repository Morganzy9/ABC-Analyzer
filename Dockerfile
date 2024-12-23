FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install gettext -y

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Run migrate
RUN python manage.py migrate

#RUN collectstatic
# RUN django-admin collectstatic

# COMPILE MESSAGES
RUN django-admin compilemessages &
RUN django-admin compilemessages &

EXPOSE 8283

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8283" ]