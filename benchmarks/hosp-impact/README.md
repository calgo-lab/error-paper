# Benchmarks

Follow these instructions to replicate our experimental evaluation.

## Concepts
We run HoloClean using the `hc36` docker image and a postgres container `pghc`.
HoloClean depends on a Postgres database being available.
We orchestrate this setup using `docker-compose`.

## Replication steps

First, build the `hc36` image.
Navigate into `benchmarks/holoclean` and run `docker build -t hc36:latest .`.

Next, open the `benchmarks/holoclean/docker-compose.yml` file and adjust the paths of the datasets that are mounts in lines 35 and 36: Make sure that a directory `benchmarks/holoclean/results` exists, in which measurements results are written (line 35).
Also, make sure that the datasets are correctly refered to in `benchmarks/holoclean/testdata`(line 36).

Next, adjust the `DATASET` (line 27) and `RUNS` (line 28) variable in `docker-compose.yaml`:
- `DATASET` should refer to the name of the error scenario that you want to measure. For example, `hospital_butter_ecar` refers to the `Typist` error scenario mentioned in the paper.
- `RUNS` refers to how many versions of the dataset you want to measure. For example, `hospital_butter_ecar` is generated 10 times, `hospital_butter_ecar_0.csv` to `hospital_butter_ecar_9.csv`. To measure all versions, set `RUNS=10`.

To start the experiment, run `docker-compose up` in the `benchmarks/holoclean` directory.
