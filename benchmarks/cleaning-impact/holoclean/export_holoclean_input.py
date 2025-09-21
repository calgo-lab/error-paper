import os
import pandas as pd
from pathlib import Path


def convert_json_to_constraints(json_content):
    """
    Metanome's output has a funky format. We massage it a bit to get the DC format that
    HoloClean expects. Thanks to Bernardo Breve for providing
    this function!
    """
    output=[]
    operationsArr = ['UNEQUAL', 'LESS_EQUAL', 'GREATER_EQUAL', 'EQUAL', 'LESS', 'GREATER']
    operationSign = ['IQ', 'LTE', 'GTE', 'EQ', 'LT', 'GT']

    dataset_name = json_content[0]['predicates'][0]['column1']['tableIdentifier'].split('.')[0]
    for dc in json_content:
        output_string = "t1&t2"
        for p in dc['predicates']:
            index = operationsArr.index(p['op'])
            output_string += '&' + operationSign[index] + '('
            output_string += "t1." + p['column1']['columnIdentifier']
            output_string += ",t2." + p['column2']['columnIdentifier'] + ')'

        output.insert(len(output), output_string)

    return output, dataset_name


def apply_conversion_to_directory(input_path, output_path):
    # List all files
    json_files = [file for file in os.listdir(input_path)]

    for json_file in json_files:
        json_file_path = os.path.join(input_path, json_file)

        # Read JSON content from the file
        with open(json_file_path, 'rt') as f:
            content = f.read().split('\n')
            content = [f'{line},' for line in content[:-1]]
            content[0] = '[' + content[0]
            content[-1] = content[-1] + ']'
            formatted = '\n'.join(content)
            json_content = eval(formatted)
        
        algorithm = 'hydra'

        # Convert JSON to constraints
        constraints, dataset_name = convert_json_to_constraints(json_content)

        # Write the converted constraints to a new file
        output_file_path = os.path.join(output_path, f'{algorithm}_{dataset_name}.txt')

        with open(output_file_path, 'wt') as output_file:
            for x in constraints:
                output_file.write(x+'\n')
        print(f'Converted DCs of dataset {dataset_name} to {output_file_path}.')


class ExportDataset:
    """
    Helper to make exporting datasets easier.
    """
    def __init__(self, export_path: str):
        self.export_path = Path(export_path)

    def export_table(self, name: str, path: str, n_rows=None):
        df = pd.read_csv(path, dtype=str)
        if n_rows is not None:
            df = df.iloc[:n_rows, :]
        df.to_csv(self.export_path/f"{name}.csv", index=False)

    def export_clean_table(self, name: str, path: str, n_rows=None):
        df_clean = pd.read_csv(path, dtype=str)
        if n_rows is not None:
            df_clean = df_clean.iloc[:n_rows, :]
        melted_df = pd.melt(df_clean.reset_index(),
                            id_vars=['index'],
                            var_name='column_name',
                            value_name='cell_value')

        # Rename the columns if needed
        melted_df.columns = ['tid', 'attribute', 'correct_val']
        melted_df.to_csv(self.export_path/f"{name}.csv", index=False)


def export_datasets(export_path: str):
    """
    Export datasets the datasets's clean and dirty version to export_path
    as .csv files.
    """
    e = ExportDataset(export_path)
    datasets_path = Path("../../../export_data/")
    dataset_names = ["beers", "flights", "rayyan", "tax", "food", "bridges", "cars", "restaurant", "hospital"]
    scenarios = ["missing_ecar", "scenario"]

    for dataset_name in dataset_names:
        dataset_path = datasets_path / dataset_name
        clean_path =  dataset_path / "clean.csv"
        e.export_clean_table(dataset_name, clean_path)
        for scenario in scenarios:
            for version in range(10):
                agg_name = f'{dataset_name}_{scenario}_{version}'
                path_dirty = dataset_path / f"{agg_name}.csv"
                e.export_table(agg_name, path_dirty)
        print(f'Exported {dataset_name} scenario {scenario} to ' + export_path)

        # export original version
        agg_name = f'{dataset_name}_original'
        path_dirty = dataset_path / f"{agg_name}.csv"
        e.export_table(agg_name, path_dirty)

    print("Finished exporting Holoclean datasets")

if __name__ == '__main__':
    export_datasets('holoclean_input/datasets/')

    dc_input_path = 'metanome_output/'
    dc_output_path = 'holoclean_input/dcs/'

    apply_conversion_to_directory(dc_input_path, dc_output_path)
