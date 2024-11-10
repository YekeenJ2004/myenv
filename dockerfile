#Start with a base Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the script and requirements.txt into the container
COPY main.py /app/
COPY .env /app/.env
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script on container start
CMD ["python", "/app/main.py"]
