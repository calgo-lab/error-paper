import pandas as pd
from pathlib import Path


from tab_err import ErrorModel, error_type
from tab_err.error_mechanism import EAR, ENAR, ECAR
from tab_err.error_type import ErrorTypeConfig
from tab_err.api import mid_level, MidLevelConfig

def get_differences(df_clean: pd.DataFrame, df_dirty: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return a dataframe with two columns 'clean' and 'dirty' for a given column. """
    mask_diff = df_clean[column] != df_dirty[column]
    df_differences = pd.concat(
        [df_clean[mask_diff][column], df_dirty[mask_diff][column]],
         axis=1
         )
    df_differences.columns = [f'{column}_clean', f'{column}_dirty']
    return df_differences

def read_csv_dataset(dataset_path):
    """
    This method reads a dataset from a csv file path.
    """
    dataframe = pd.read_csv(dataset_path, sep=",", header="infer", encoding="utf-8", dtype=str,
                                keep_default_na=False, low_memory=False)
    return dataframe

def create_mcar(dataset_name: str, df_clean: pd.DataFrame, error_percentages: pd.Series):
    export_dir = Path(f'../export_data/{dataset_name}')
    export_dir.mkdir(parents=True, exist_ok=True)
    
    mid_lvl_config = {column: [ErrorModel(ECAR(), error_type.MissingValue(), float(error_percentages[column]))] for column in df_clean.columns}
    config_missing_ecar = MidLevelConfig(mid_lvl_config)

    for i in range(10):
        df_corrupted, error_mask = mid_level.create_errors(df_clean, config_missing_ecar)
        df_corrupted.to_csv(export_dir / f'{dataset_name}_missing_ecar_{i}.csv', index=False)
        print(f"Saved MCAR dataset {dataset_name} iteration {i}")
    df_clean.to_csv(export_dir / f'{dataset_name}_clean.csv', index=False)