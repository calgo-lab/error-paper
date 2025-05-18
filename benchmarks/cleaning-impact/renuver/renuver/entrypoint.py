import os
import sys
import json
import time
import subprocess

RENUVER_RESULTS_PATH = "results/renuver-results/"

def calculate_performance(imputation_file, ground_truth_file):
    """
    Calculate error detection and correction performance metrics from two CSV files.
    """
    def parse_csv(filename:str, is_imputation_file:bool):
        result = {}
        with open(filename, 'r') as f:
            if is_imputation_file:
                next(f)
            for line in f:
                parts = line.strip().split(';')
                result[(int(parts[0]), parts[1])] = parts[-1]
        return result

    correction_dictionary = parse_csv(imputation_file, True)
    actual_errors = parse_csv(ground_truth_file, False)
    
    ed_tp = ec_tp = 0.0
    output_size = len(correction_dictionary)
    
    for cell in correction_dictionary:
        if cell in actual_errors:
            ed_tp += 1.0
            if correction_dictionary[cell] == actual_errors[cell]:
                ec_tp += 1.0
    
    ed_p = 0.0 if output_size == 0 else ed_tp / output_size
    ed_r = 0.0 if len(actual_errors) == 0 else ed_tp / len(actual_errors)
    ed_f = 0.0 if (ed_p + ed_r) == 0.0 else (2 * ed_p * ed_r) / (ed_p + ed_r)
    
    ec_p = 0.0 if output_size == 0 else ec_tp / output_size
    ec_r = 0.0 if len(actual_errors) == 0 else ec_tp / len(actual_errors)
    ec_f = 0.0 if (ec_p + ec_r) == 0.0 else (2 * ec_p * ec_r) / (ec_p + ec_r)
    
    return {'ed_p': ed_p,
            'ed_r': ed_r,
            'ed_f': ed_f,
            'ec_p': ec_p,
            'ec_r': ec_r,
            'ec_f': ec_f}


def run_task(dataset_name: str, scenario: str, version: str):
    """
    Run a jar with specified dataset.
   Returns:
        subprocess.CompletedProcess: Result of the subprocess execution
    
    Raises:
        FileNotFoundError: If the dataset file doesn't exist
        subprocess.CalledProcessError: If the Java command fails
    """
    dataset_map = {"beers": "D,D,D,D,D,D,D,D,D,D,D",
                   "flights": "D,D,D,D,D,D,D",
                   "hospital": "D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D",
                   "rayyan": "D,D,D,D,D,D,D,D,D,D,D",
                   "tax": "D,D,B,D,D,D,D,D,B,B,D,D,D,D,D",
                   "food": "D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D",
                   "bridges": "D,C,D,D,D,D,D,B,D,D,D,D,D",
                   "cars": "D,D,D,D,D,D,D,D,D",
                   "glass": "D,D,D,D,D,D,D,D,D,D,D",
                   "restaurant": "D,D,D,D,D,D"}

    rfdc_name = f'output_false_6_{dataset_name}.csv'

    column_types = dataset_map.get(dataset_name)
    if column_types is None:
        raise ValueError('invalid dataset')

    dirty_dataset_name = f'{dataset_name}_{scenario}_{version}'
    
    # Construct the Java command
    java_command = [
        'java',
        '-jar',
        '-Xms2g',
        '-Xmx60g',
        'Renuver.jar',
        column_types,
        dirty_dataset_name,
        ',',
        rfdc_name,
        '6'
    ]
    
    # Run the command and capture output
    result = subprocess.run(
        java_command,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True
    )
    print("Command executed successfully")
    print("Output:", result.stdout)


    file_parts = dirty_dataset_name.split('_')
    file_parts.insert(-1, '6')
    imputation_file = '_'.join(file_parts)
    imputation_path = f'ImputationResults/{imputation_file}.csv'
    ground_truth_path = f'Dataset/{dirty_dataset_name}_clean_tuples.csv'
    metrics = calculate_performance(imputation_path, ground_truth_path)
    return metrics

def main():
    dataset_name = os.getenv('DATASET_NAME')
    scenario = os.getenv('DATASET_SCENARIO')
    version = os.getenv('DATASET_VERSION')

    # You need _exacly_ 3 _ in the filename, not 4, not 2, but really exactly 3.
    sanitized_scenario = scenario.replace('_', '-')

    metrics = run_task(dataset_name, sanitized_scenario, version)
    result =  {
        'dataset_name': dataset_name,
        'scenario': scenario,
        'version': version,
        **metrics
        }
    print(f'Successfully cleaned errors with RENUVER for {dataset_name}, {scenario}, {version}.')

    timestamp = str(int(time.time() * 1e9))
    filename = f"renuver_{dataset_name}_{scenario}_{version}_{timestamp}.json"


    os.makedirs(RENUVER_RESULTS_PATH, exist_ok=True)

    with open(f'{RENUVER_RESULTS_PATH}{filename}', 'wt') as f:
        f.write(json.dumps(result))
    
    print(f'Finished running RENUVER, wrote results to {filename}.')

if __name__ == "__main__":
    main()
    #run_task(dataset_name='bridges', scenario='missing-ecar',version='0')
    #run_task(dataset_name='bridges', scenario='original',version='0')
