# Use Python 3.8.20 base image
FROM python:3.8.20

# Set working directory
WORKDIR /app

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY raha/ raha/
COPY entrypoint.py .
COPY setup.cfg .
COPY setup.py .

# Install the package in editable mode
RUN pip install -e .

# Set entrypoint
ENTRYPOINT ["python", "entrypoint.py"]