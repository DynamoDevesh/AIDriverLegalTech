# Use a smaller base image to reduce size
FROM python:3.11.11-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file to leverage Docker caching
COPY requirements.txt .

# Install dependencies in a virtual environment to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Use a minimal final runtime image
FROM python:3.11.11-alpine

# Set the working directory
WORKDIR /app

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application files
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80
ENV PORT=80  # Elastic Beanstalk expects the app to run on port 80

# Expose the correct port for Elastic Beanstalk
EXPOSE 80

# Run the Flask app
CMD ["flask", "run"]
