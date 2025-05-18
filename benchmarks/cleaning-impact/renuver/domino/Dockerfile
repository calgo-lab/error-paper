FROM eclipse-temurin:17-jre-jammy

# Install python
RUN apt-get update && apt-get install -y python3

WORKDIR /app

COPY Domino.jar .
COPY CreateMatrix.jar .
COPY entrypoint.py .

ENTRYPOINT ["python3", "entrypoint.py"]
