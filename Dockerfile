# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME SecureAI

# Run gunicorn when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.main:app"]
