# Cleaning Impact Holoclean

Measures error scenario cleaning impact on holoclean.

## How to run it

1. Generate datasets in `cleaning_impact_dataset_generation.ipynb`
1. Optionally run `poetry run python export_metanome_input.py` to export data to metanome to mine DCs. Copy metanome outputs to `metanome_outputs/`. Mined DCs are already stored in `metanome_outputs/` for all datasets of the paper.
1. Run `poetry run python export_holoclean_input.py` to generate datasets in a format holoclean expects.
1. Run `docker build -t hc36:latest .` to build the holoclean docker image

### local measurements
To run an experiment locally with docker-compose, navigate into `src`, adjust `docker-compose.yaml`, then run `docker-compose up`.

### k8s measurements
To run the experiment on a k8s cluster, navigate into `k8s_jobs`, then run `helm install cleaning-impact-holoclean ./ -f values.yaml` to run jobs. Run `python generate_values_yaml.py` to generate the `values.yaml` file dynamically. Make sure you create all required PVCs beforehand and that you have the `hc36` image uploaded to a remote artiface repository.

## Structure

- holoclean_input/ contains datasets and DCs in the format holoclean expects
- k8s_jobs/ contains a helm chart to run the experiment on a k8s cluster
- metanome_output/ contains the outputs of the metanme DC profiling algorithm
- src/ contains the holoclean source code
- to_metanome/ contains the datasets ready to be imported by metanome
