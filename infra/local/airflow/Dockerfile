FROM apache/airflow:2.8.1-python3.10

USER root

# Install system dependencies if needed later
RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get clean

USER airflow

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
