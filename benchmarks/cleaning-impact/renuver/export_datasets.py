import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List


def process_column_names(string_list):
    """
    RENUVER expects column names that contain no special characters
    and no numberes. This function transforms existing column
    names accordingly.
    
    Args:
        string_list (list): List of strings to process
        
    Returns:
        list: Processed list of strings
    """
    # Dictionary for number to word conversion
    number_to_word = {
        '0': 'zero',
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four',
        '5': 'five',
        '6': 'six',
        '7': 'seven',
        '8': 'eight',
        '9': 'nine'
    }

    def process_string(s):
        # Convert to lowercase
        s = s.lower()
        
        # Replace numbers with words
        for num, word in number_to_word.items():
            s = s.replace(num, word)
            
        # Replace special characters with 'x'
        processed = ''
        for char in s:
            if char.isalnum() or char.isspace():
                processed += char
            else:
                processed += 'x'
                
        return processed

    return [process_string(s) for s in string_list]


class ExportDataset:
    """
    Helper to make exporting datasets easier.
    """
    def __init__(self, export_path: str, initial_tuples_path: str|None = None):
        self.export_path = Path(export_path)
        if initial_tuples_path is not None:
            self.initial_tuples_path = Path(initial_tuples_path)

    def export_table(self, name: str, path: str, na_values: List[str]|None = None):
        df = pd.read_csv(path, dtype=str, na_values=na_values)

        # Replace missing values with 'empty'
        df.fillna('empty', inplace=True)

        # Remove commas from fields because this breaks domino
        df = df.apply(lambda x: x.str.replace(',', ''))

        # Ensure column names only contain letters
        df.columns = process_column_names(df.columns)

        df.to_csv(self.export_path/f"{name}.csv", index=False, sep=',')

    def transform_export_table(self, name: str, path_clean: str, path_dirty: str, na_values: List[str]|None = None):
        """
        Helper to export erroneous datasets and inject the char "?" that 
        RENUVER expects to indicate errors.
        """
        df_clean = pd.read_csv(path_clean, dtype=str, na_values=na_values)
        df_dirty = pd.read_csv(path_dirty, dtype=str, na_values=na_values)
        
        # Replace missing values with 'empty'
        df_clean.fillna('empty', inplace=True), df_dirty.fillna('empty', inplace=True)

        # Remove commas from fields because this breaks domino
        df_clean = df_clean.apply(lambda x: x.str.replace(',', ''))
        df_dirty = df_dirty.apply(lambda x: x.str.replace(',', ''))

        # Ensure column names only contain letters
        df_clean.columns = process_column_names(df_clean.columns)
        df_dirty.columns = process_column_names(df_dirty.columns)

        error_mask = df_clean != df_dirty
        
        # Set missing value char ? that renuver expects and save .csv
        df_dirty[error_mask] = '?'
        df_dirty.to_csv(self.export_path/f"{name}.csv", index=False, sep=',')

        # Also generate file for InitialTuples/ that renuver expects to store results
        rows, cols = np.where(error_mask)
        df_initial_tuples = pd.DataFrame({
            'row': rows + 1,  # + 1 since we want 1-based indexing, otherwise renuver throws errors
            'attribute': df_dirty.columns[cols],
            'value': df_dirty.values[rows, cols]
        })
        df_initial_tuples.to_csv(self.initial_tuples_path/f"{name}.csv", index=False, header=False, sep=';')

        df_clean_tuples = pd.DataFrame({
            'row': rows + 1,
            'attribute': df_clean.columns[cols],
            'value': df_clean.values[rows, cols]
        })
        df_clean_tuples.to_csv(self.export_path/f"{name}_clean_tuples.csv", index=False, header=False, sep=';')


def export_datasets(dataset_path: Path):
    """
    Export datasets the datasets's clean and dirty version to export_path
    as .csv files.
    """
    export_path_domino = 'domino/datasets/'
    export_path_renuver = 'renuver/Dataset/'
    # todo continue here print wrong below
    export_domino = ExportDataset(export_path_domino)
    export_renuver = ExportDataset(export_path_renuver, 'renuver/InitialTuples/')
    datasets = ["beers", "flights", "rayyan", "tax", "food", "bridges", "cars", "restaurant", "hospital"]
    versions = range(10)
    scenarios = ["missing_ecar", "scenario"]

    for dataset_name in datasets:
        na_values = None
        path_clean = dataset_path/f"{dataset_name}/clean.csv"
        if dataset_name == 'bridges':
            na_values = ['?']
        export_domino.export_table(dataset_name, path_clean, na_values)
        export_renuver.export_table(dataset_name, path_clean, na_values)
        for scenario in scenarios:
            for version in versions:
                # You need 3 _ in the filename, not 4, not 2, but really exactly 3.
                sanitized_scenario = scenario.replace('_', '-')
                new_name = f'{dataset_name}_{sanitized_scenario}_{version}'
                path_dirty = dataset_path/dataset_name/f"{dataset_name}_{scenario}_{version}.csv"
                export_renuver.transform_export_table(new_name, path_clean, path_dirty, na_values)
            print(f'Exported {dataset_name} scenario {scenario} to {export_path_renuver} and {export_path_domino}')

        # export original version -- renuver _needs_ three _ in the filename, so add a meaningless 0 to the new_name.
        new_name = f'{dataset_name}_original_0'
        path_dirty = dataset_path/dataset_name/ f"{dataset_name}_original.csv"
        export_renuver.transform_export_table(new_name, path_clean, path_dirty, na_values)
        print(f'Exported {dataset_name} scenario original to {export_path_renuver} and {export_path_domino}')

    print(f'Exported datasets to {export_path_renuver} and {export_path_domino}')

if __name__ == '__main__':
    export_datasets(dataset_path=Path('../../../export_data/'))
