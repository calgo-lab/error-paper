FROM eclipse-temurin:17-jre-jammy

# Install python
RUN apt-get update && apt-get install -y python3

WORKDIR /app

COPY Renuver.jar entrypoint.py .

COPY Candidates/ Candidates/ 
COPY ImputationResults/ ImputationResults/
# move these into PVC and mount
COPY Dataset/ Dataset/ 
COPY InitialTuples/ InitialTuples/
COPY RFD/ RFD/ 
COPY KeyRFDs/ KeyRFDs/
COPY Logs/ Logs/ 
COPY NonKeyRFDs/ NonKeyRFDs/ 
COPY Populated/ Populated/

ENTRYPOINT ["python3", "entrypoint.py"]
