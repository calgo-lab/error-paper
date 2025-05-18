# Cleaning Impact RENUVER

Measures error scenario cleaning impact on data cleaning with renuver.

## How to run it

1. Generate datasets in `cleaning_impact_dataset_generation.ipynb`
1. Run `python export_datasets.py` to export datasets in formats required by domino for RFD_c mining and by renuver for data cleaning
1. First mine RFD_cs with DOMINO, then copy RFDcs over to renuver/Rfds/.

### Local measurements
To run experiments locally, execute `python entrypoint.py`.

### k8s measurements 
To run measurements on the cluster, run `helm install cleaning-impact-renuver ./ -f values.yaml` in the k8s_jobs/ directory.
Make sure you have built the docker image of renuver before and have moved that to a remote registry.
Also make sure that you have created the required PVCs and that you have copied the directories InitialTuples/, Dataset/ and RFD/ over to that PVC.

## Structure

- k8s_jobs/ contains a helm chart to run the experiment on a k8s cluster
- renuver/ contains the source code of renuver
- domino/ contains the source code of domino
