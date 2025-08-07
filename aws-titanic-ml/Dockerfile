FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ ./src/

# Set the environment variable for the Python module
ENV PYTHONPATH=/app/src

# Command to run the application
CMD ["python", "src/train_titanic_lambda.py"]