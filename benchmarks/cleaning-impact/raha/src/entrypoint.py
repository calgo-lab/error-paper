import os
import json
import time

from raha import Detection, Correction
from raha.load_dataset import Dataset

RAHA_RESULTS_PATH = "results/raha-detection-results/"
BARAN_RESULTS_PATH = "results/baran-correction-results/"

def run_raha(dataset_name: str, scenario: str, version: str):
    raha_dataset = Dataset(dataset_name, scenario, version, RAHA_RESULTS_PATH)
    app = Detection()
    app.VERBOSE = False
    app.SAVE_RESULTS = False
    detected_cells = app.run(raha_dataset)

    p, r, f1 = raha_dataset.get_data_cleaning_evaluation(detected_cells)[:3]
    print("Raha's performance on {}:\nPrecision = {:.2f}\nRecall = {:.2f}\nF1 = {:.2f}".format(raha_dataset.name, p, r, f1))
    detected_cells_index = list(detected_cells.keys())

    return {
        'detected_cells_index': detected_cells_index,
        'precision': p,
        'recall': r,
        'f1': f1,
        'dataset_name': dataset_name,
        'scenario': scenario,
        'version': version
    }

def run_baran(dataset_name: str, scenario: str, version: str, error_detection_mode: str):
    data = Dataset(dataset_name, scenario, version, RAHA_RESULTS_PATH)
    app = Correction()
    app.VERBOSE = True
    app.SAVE_RESULTS = False
    app.LABELING_ERROR_PCT = 0

    start_time = time.time()
    data.detected_cells = data.get_errors_dictionary(error_detection_mode)
    correction_dictionary = app.run(data)
    end_time = time.time()
    p, r, f = data.get_data_cleaning_evaluation(correction_dictionary)[-3:]
    print("Baran's performance on {}:\nPrecision = {:.2f}\nRecall = {:.2f}\nF1 = {:.2f}".format(data.name, p, r, f))
    return {
        'dataset_name': dataset_name,
        'scenario': scenario,
        'version': version,
        'error_detection_mode': error_detection_mode,
        "precision": p,
        "recall": r,
        "f1": f,
        "runtime": end_time - start_time
        },
    

if __name__ == '__main__':
    task = os.getenv('TASK')
    if task is None:
        raise ValueError('No environment variable TASK found. Aborting.')

    dataset_name = os.getenv('DATASET_NAME')
    scenario = os.getenv('DATASET_SCENARIO')
    version = os.getenv('DATASET_VERSION')

    if task in ['detection', 'both']: 
        print(f'Start detection with Raha')
        result = run_raha(dataset_name, scenario, version)

        timestamp = str(int(time.time() * 1e9))
        filename = f"raha_{dataset_name}_{scenario}_{version}_{timestamp}.json"

        os.makedirs(RAHA_RESULTS_PATH, exist_ok=True)
        with open(f"{RAHA_RESULTS_PATH}/{filename}", "wt") as f:
            json.dump(result, f)
        print(f'Raha done, wrote error detection results {filename} to {RAHA_RESULTS_PATH}.')

    if task in ['correction', 'both']:
        error_detection_mode = os.getenv('ERROR_DETECTION_MODE')  # 'perfect' or 'raha'
        if error_detection_mode is None:
            raise ValueError('set ERROR_DETECTION_MODE environment variable.')
        print(f'Start correction with Baran.')
        result = run_baran(dataset_name, scenario, version, error_detection_mode)

        timestamp = str(int(time.time() * 1e9))
        filename = f"baran_{dataset_name}_{scenario}_{version}_{timestamp}.json"

        os.makedirs(BARAN_RESULTS_PATH, exist_ok=True)
        with open(f"{BARAN_RESULTS_PATH}/{filename}", "wt") as f:
            json.dump(result, f)
        print(f'Baran done, wrote error correction results {filename} to {BARAN_RESULTS_PATH}.')

    if task not in ['detection', 'correction', 'both']:
        print(f'Start detection & correction experiment {id}')
        raise ValueError('invalid task')

    print(f'Successfully finished task "{task}" for {filename}.')
