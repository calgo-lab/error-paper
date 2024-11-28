# Towards Realistic Error Models for Tabular Data

The notebooks in this repository were used to execute the experimental evaluation of our paper "Towards Realistic Error Models for Tabular Data".
Specifically, 

1) the notebook `dataset_generation.ipynb` contains the procedure we followed to generate datasets corresponding to the error scenarios we describe in our paper.
2) The notebook `dataset_analysis.ipynb` contains our analysis of the `HOSP` dataset.
3) The notebook `plots.ipynb` contains the procedure we use to generate the figures in our publication. It reads experiment's results from the `error_paper/measurements/` directory -- check the notebook's code for details.

## Installation
We use [poetry](https://python-poetry.org/) to manage dependencies. Simply run `poetry install` to install all dependencies.

## Experiments
In our experiments, we generate various erroneous versions of the `HOSP` dataset and clean them with `HoloClean`.
Check the documentation in `benchmarks/README.md` for instructions on how to replicate our measurements.
