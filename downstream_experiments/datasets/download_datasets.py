import openml
import pandas as pd

ids = [44120,
       44122,
       44123,
       44124,
       44127,
       44130,
       44131,
       44089,
       44090,
       44091,
       44156,
       44157,
       44158,
       44160,
       44162]

for dataset_id in ids:
    # Load the dataset
    dataset = openml.datasets.get_dataset(dataset_id)

    # Get the data as a DataFrame, including the target column
    X, y, _, _ = dataset.get_data(target=dataset.default_target_attribute)

    # Combine features and target into a single DataFrame
    df = X.copy()
    df["target"] = y  # Rename target column to "target"

    df.to_csv(f"./{str(dataset_id)}.csv" )
