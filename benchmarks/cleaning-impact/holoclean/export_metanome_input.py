import pandas as pd
from pathlib import Path

def export_table(name: str, path: str):
    df_clean = pd.read_csv(path, dtype=str)

    df_clean.to_csv(f"to_metanome/{name}.csv", index=False)
    print(f'Created csv for dataset {name}')

def main():
    datasets_path = Path("../../../export_data/")
    dataset_names = ["beers", "flights", "rayyan", "tax", "food", "bridges", "cars", "restaurant"]

    for dataset_name in dataset_names:
        agg_name = f'{dataset_name}'
        path = datasets_path / dataset_name / "clean.csv"
        export_table(agg_name, path)

if __name__ == '__main__':
    main()
