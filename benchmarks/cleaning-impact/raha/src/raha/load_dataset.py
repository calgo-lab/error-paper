import json
from pathlib import Path
from typing import Union, Dict, Tuple
import pandas as pd

class Dataset:
    """
    The dataset class.
    """

    def __init__(self,
                 dataset_name: str,
                 scenario: str,
                 version: str,
                 raha_result_path: str = "datasets/raha-detection-results/"):
        """
        @param dataset_name: Name of the dataset.
        @param scenario: Name of the error scenario.
        @param version: version of the generated dataset.
        """
        self.repaired_dataframe = None  # to be assigned after cleaning suggestions were applied.
        self.version = version
        self.scenario = scenario
        self.raha_result_path = raha_result_path
        self.has_ground_truth = True

        if version != "":
            self.path = f"datasets/{dataset_name}/{dataset_name}_{scenario}_{version}.csv"
        else:  # that's the original, exists only in one version
            self.path = f"datasets/{dataset_name}/{dataset_name}_{scenario}.csv"

        self.clean_path = f"datasets/{dataset_name}/clean.csv"
        self.name = dataset_name

        self.dataframe = self.read_csv_dataset(self.path)
        self.clean_dataframe = self.read_csv_dataset(self.clean_path)

    @staticmethod
    def read_parquet_dataset(dataset_path: Union[str, None]):
        """
        This method reads a dataset from a parquet file path. This is nice for the imputer because
        parquet preserves dtypes.
        """
        if dataset_path is None:
            return None
        dataframe = pd.read_parquet(dataset_path)
        return dataframe

    def read_csv_dataset(self, dataset_path):
        """
        This method reads a dataset from a csv file path.
        """
        dataframe = pd.read_csv(dataset_path, sep=",", header="infer", encoding="utf-8", dtype=str,
                                    keep_default_na=False, low_memory=False)
        return dataframe

    @staticmethod
    def write_csv_dataset(dataset_path, dataframe):
        """
        This method writes a dataset to a csv file path.
        """
        dataframe.to_csv(dataset_path, sep=",", header=True, index=False, encoding="utf-8")

    @staticmethod
    def get_dataframes_difference(df_1: pd.DataFrame, df_2: pd.DataFrame) -> Dict:
        """
        This method compares two dataframes df_1 and df_2. It returns a dictionary whose keys are the coordinates of
        a cell. The corresponding value is the value in df_1 at the cell's position if the values of df_1 and df_2 are
        not the same at the given position.
        """
        if df_1.shape != df_2.shape:
            raise ValueError("Two compared datasets do not have equal sizes.")

        diff_mask = df_1 != df_2

        differences = {}
        for row_idx, row in enumerate(diff_mask.index):
            for col_idx, column in enumerate(diff_mask.columns):
                if diff_mask.at[row, column]:
                    differences[(row_idx, col_idx)] = df_1.at[row, column]

        return differences

    def create_repaired_dataset(self, correction_dictionary):
        """
        This method takes the dictionary of corrected values and creates the repaired dataset.
        """
        self.repaired_dataframe = self.dataframe.copy()
        for cell in correction_dictionary:
            self.repaired_dataframe.iloc[cell] = correction_dictionary[cell]

    def get_df_from_labeled_tuples(self):
        """
        Turns the labeled tuples into a dataframe.
        """
        return self.clean_dataframe.iloc[list(self.labeled_tuples.keys()), :]

    def _get_actual_errors_dictionary_ground_truth(self) -> Dict[Tuple[int, int], str]:
        """
        Returns a dictionary that resolves every error cell to the ground truth.
        """
        return self.get_dataframes_difference(self.clean_dataframe, self.dataframe)

    def get_errors_dictionary(self, mode: 'str') -> Dict[Tuple[int, int], str]:
        """
        This method compares the clean and dirty versions of a dataset. The returned dictionary resolves to the error
        values in the dirty dataframe.

        There are two modes: 'perfect' to simulate perfect error detection ahead, or 'raha', which loads imperfect
        error positions that we detected with raha.
        """
        if mode == 'perfect':
            return self.get_dataframes_difference(self.dataframe, self.clean_dataframe)
        if mode == 'raha':
            raha_results = []
            for file_path in Path(self.raha_result_path).glob('*.json'):
                with open(file_path, 'rt') as f:
                    raha_results.append(json.load(f))
            
            relevant_result = [r for r in raha_results if (r['dataset_name'] == self.name and r['version'] == self.version) and r['scenario'] == self.scenario]

            if len(relevant_result) != 1:
                raise ValueError('Ambiguous choice of raha results, something is wrong.')
            detected_cells_index = relevant_result[0]['detected_cells_index']
            detected_cells = {}

            for pos in detected_cells_index:
                detected_cells[tuple(pos)] = self.dataframe.iloc[pos[0], pos[1]]
            return detected_cells
        raise ValueError('invalid mode to get errors_dictionary.')

    def get_correction_dictionary(self):
        """
        This method compares the repaired and dirty versions of a dataset.
        """
        return self.get_dataframes_difference(self.repaired_dataframe, self.dataframe)

    def get_data_quality(self):
        """
        This method calculates data quality of a dataset.
        """
        return 1.0 - float(len(self._get_actual_errors_dictionary_ground_truth())) / (self.dataframe.shape[0] * self.dataframe.shape[1])

    def get_data_cleaning_evaluation(self, correction_dictionary, sampled_rows_dictionary=False):
        """
        This method evaluates data cleaning process.
        """
        actual_errors = self._get_actual_errors_dictionary_ground_truth()
        if sampled_rows_dictionary:
            actual_errors = {(i, j): actual_errors[(i, j)] for (i, j) in actual_errors if i in sampled_rows_dictionary}
        ed_tp = 0.0
        ec_tp = 0.0
        output_size = 0.0
        for cell in correction_dictionary:
            if (not sampled_rows_dictionary) or (cell[0] in sampled_rows_dictionary):
                output_size += 1
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
        return [ed_p, ed_r, ed_f, ec_p, ec_r, ec_f]
########################################


########################################
if __name__ == "__main__":
    d = Dataset('toy')
    print(d.get_data_quality())
########################################
