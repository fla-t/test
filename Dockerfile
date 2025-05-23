FROM python:3.12

WORKDIR /app
COPY . /app

# Update apt-get
RUN apt-get update

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD [ "uvicorn", "src.entrypoint.main:app", "--port 8080", "--host 0.0.0.0"]