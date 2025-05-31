# Cleaning Impact Raha & Baran

Measures error scenario cleaning impact on error detection with raha & correction with baran.

## How to run it

1. Generate datasets in `cleaning_impact_dataset_generation.ipynb`
1. Install dependencies in `requirements.txt` with `pip` in a virtual environment.

### Local measurements
To run experiments locally, execute `python entrypoint.py`. There, the `task` variable decides what to do (detection, correction, both). Set all required environment variables to run locally.

### k8s measurements 
To run measurements on the cluster, run `helm install cleaning-impact-baranraha ./ -f values.yaml` in the k8s_jobs/ directory. Make sure you have built the docker image of raha before and have moved that to a remote registry.

## Structure

- k8s_jobs/ contains a helm chart to run the experiment on a k8s cluster
- raha/ contains the source code of baran & raha
