import os
import sys
import time
import json
import random
from pathlib import Path
import holoclean
from detect import NullDetector, ViolationDetector
from repair.featurize import *

import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres_dsn(dsn, max_attempts=10, base_delay=1.0):
    attempt = 0
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(dsn)
            conn.close()
            print("[INFO] Postgres is ready.")
            return
        except OperationalError as e:
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"[WARN] Postgres not ready (attempt {attempt + 1}/{max_attempts}): {e}")
            print(f"[INFO] Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
            attempt += 1

    print("[ERROR] Postgres did not become ready in time.", file=sys.stderr)
    sys.exit(1)


def write_signal_to_stop_postgres():
    SIGNAL_FILE_PATH = "/etc/pod-signal/holoclean_done" # signal for the postgres sidecar container to shutdown
    signal_dir = os.path.dirname(SIGNAL_FILE_PATH)
    if not os.path.exists(signal_dir):
        os.makedirs(signal_dir) # Ensure the directory exists

    with open(SIGNAL_FILE_PATH, 'w') as f:
        f.write("done") # Write something to the file, content doesn't strictly matter

    print(f"Signal file created at {SIGNAL_FILE_PATH}")

    sys.exit(0) # Exit successfully


def run_k8s_job(dataset_name: str, dataset_scenario: str, dataset_version: str):

    # otherwise, assume this is a k8s job
    dbhost = os.getenv('DB_HOST')
    dbport = os.getenv('DATABASE_PORT')
    dbname = os.getenv('DATABASE_NAME')
    dbuser = os.getenv('DATABASE_USER')
    dbpass = os.getenv('DATABASE_PASSWORD')

    dsn = f"dbname={dbname} user={dbuser} password={dbpass} host={dbhost} port={dbport}"
    
    wait_for_postgres_dsn(dsn)
    dirty_name = f'{dataset_name}_{dataset_scenario}_{dataset_version}' if dataset_version else f'{dataset_name}_{dataset_scenario}'
    run_hc(dataset_name, dataset_name, dirty_name)
    write_signal_to_stop_postgres()

def run_docker_compose():
    """
    Run HoloClean on all datasets three times.
    """
    #versions = range(10)
    versions = range(1)
    #dataset_names = ["bridges", "cars", "restaurant", "beers", "flights", "rayyan", "food", "tax"]
    #scenarios = ['missing_ecar', 'scenario']
    dataset_names = ["hospital"]
    scenarios = ['missing_ecar']

    # run generated datasets
    for dataset_name in dataset_names:
        clean_table = dataset_name
        for scenario in scenarios:
            for version in versions:
                dirty_table = f'{dataset_name}_{scenario}_{version}'
                run_hc(dataset_name, clean_table, dirty_table)
        # run original dataset
        dirty_table = f'{dataset_name}_original'
        run_hc(dataset_name, clean_table, dirty_table)


def run_hc(dataset_name: str, clean_name: str, dirty_name: str):
    """
    Run HoloClean on a single dataset. Write results to the results/ directory,
    which is created if necessary.
    """
    output_path = Path('/home/results/')

    data_path = Path('/home/data/')
    # 1. Setup a HoloClean session.
    hc = holoclean.HoloClean(
        db_name='holo',
        host='postgres',
        domain_thresh_1=0,
        domain_thresh_2=0,
        weak_label_thresh=0.99,
        max_domain=10000,
        cor_strength=0.6,
        nb_cor_strength=0.8,
        epochs=10,
        weight_decay=0.01,
        learning_rate=0.001,
        threads=1,
        batch_size=1,
        verbose=True,
        timeout=3*60000,
        feature_norm=False,
        weight_norm=False,
        print_fw=True
    ).session

    # 2. Load training data and denial constraints.
    hc.load_data(dataset_name, data_path/f'datasets/{dirty_name}.csv')
    hc.load_dcs(data_path/f'dcs/hydra_{dataset_name}.txt')
    hc.ds.set_constraints(hc.get_dcs())

    # 3. Detect erroneous cells using these two detectors.
    detectors = [NullDetector(), ViolationDetector()]
    hc.detect_errors(detectors)

    # 4. Repair errors utilizing the defined features.
    hc.setup_domain()
    featurizers = [
        InitAttrFeaturizer(),
        OccurAttrFeaturizer(),
        FreqFeaturizer(),
        ConstraintFeaturizer(),
    ]

    hc.repair_errors(featurizers)

    # 5. Evaluate the correctness of the results.
    result = hc.evaluate(fpath=data_path/f'datasets/{clean_name}.csv',
                       tid_col='tid',
                       attr_col='attribute',
                       val_col='correct_val')

    result = {'algorithm': 'holoclean',
              'dataset_name': os.getenv('DATASET_NAME'),
              'dataset_scenario': os.getenv('DATASET_SCENARIO'),
              'dataset_version': os.getenv('DATASET_VERSION'),
              **result}
    timestamp = str(int(time.time() * 1e9))
    with open(output_path/f'hc_{dataset_name}_{dirty_name}_{timestamp}.json', 'w') as f:
        f.write(json.dumps(result._asdict()))

if __name__ == '__main__':
    dataset_name = os.getenv('DATASET_NAME')
    dataset_scenario = os.getenv('DATASET_SCENARIO')
    dataset_version = os.getenv('DATASET_VERSION')

    if not dataset_name or not dataset_scenario:
        # assume that docker-compose is running entrypoint
        run_docker_compose()
    run_k8s_job(dataset_name, dataset_scenario, dataset_version)
