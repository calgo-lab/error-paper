import pandas as pd

def get_differences(df_clean: pd.DataFrame, df_dirty: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return a dataframe with two columns 'clean' and 'dirty' for a given column. """
    mask_diff = df_clean[column] != df_dirty[column]
    df_differences = pd.concat(
        [df_clean[mask_diff][column], df_dirty[mask_diff][column]],
         axis=1
         )
    df_differences.columns = [f'{column}_clean', f'{column}_dirty']
    return df_differences