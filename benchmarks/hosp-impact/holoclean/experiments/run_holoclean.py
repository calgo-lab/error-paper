import os
import sys
import json
sys.path.append('../')
import holoclean
from detect import NullDetector, ViolationDetector
from repair.featurize import *


def main(dataset: str, runs: int):
    for run in range(runs):
        
        # The original hospital dataset by Xu et al. exists only once, but we generate multiple versions
        # of it.
        dirty_identifier = f'{dataset}_{run}' if dataset != 'hospital' else 'hospital'

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
        hc.load_data(dirty_identifier.replace('_', ''), f'../testdata/{dirty_identifier}.csv')
        hc.load_dcs('../testdata/hospital_constraints.txt')
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
        result = hc.evaluate(fpath='../testdata/hospital_clean.csv',
                            tid_col='tid',
                            attr_col='attribute',
                            val_col='correct_val')

        with open(f'../results/{run}-{dataset}.json', 'wt') as f:
            f.write(json.dumps(result._asdict()))


if __name__ == "__main__":
    dataset = str(os.getenv('DATASET'))
    runs = int(os.getenv('RUNS'))
    main(dataset, runs)
