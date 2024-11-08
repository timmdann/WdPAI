# Use an official Python runtime as a parent image
FROM python:3.9-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/src/app

COPY requirements.txt .

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python server script into the container
COPY server.py .

# Expose the port that your Python server will run on
EXPOSE 8000

# Run the Python server
CMD ["python", "./server.py"]