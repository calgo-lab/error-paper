# Use the x86_64 Python 3.6 image
FROM --platform=linux/amd64 python:3.7

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install necessary packages
RUN apt-get update && \
    apt-get install -y git

# Set the working directory in the container
WORKDIR /home

# Copy requirements.txt if you have any Python dependencies
COPY requirements.txt ./

# Install Python dependencies
RUN python -m pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Default command to run when starting the container
CMD ["experiments/entrypoint.sh"]
