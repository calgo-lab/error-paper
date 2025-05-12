import time
import json
from pathlib import Path
import holoclean
from detect import NullDetector, ViolationDetector
from repair.featurize import *

def main():
    """
    Run HoloClean on all datasets three times.
    """
    #versions = range(10)
    versions = range(1)
    dataset_names = ["bridges", "cars", "restaurant", "beers", "flights", "rayyan", "food", "tax"]

    # run generated datasets
    for dataset_name in dataset_names:
        clean_table = dataset_name
        for scenario in ['missing_ecar', 'scenario']:
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

    timestamp = str(int(time.time() * 1e9))
    with open(output_path/f'{dataset_name}_{dirty_name}_{timestamp}.json', 'w') as f:
        f.write(json.dumps(result._asdict()))

if __name__ == '__main__':
    main()
