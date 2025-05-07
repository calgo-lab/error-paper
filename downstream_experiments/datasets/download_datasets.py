import openml
import pandas as pd

ids = [44120,  # Classification
       44122,  # Classification
       44123,  # Classification
       44124,  # Classification
       44127,  # Classification
       44130,  # Classification
       44131,  # Classification
       44089,  # Classification
       44090,  # Classification
       44091,  # Classification
       44156,  # Classification
       44157,  # Classification
       44158,  # Classification
       44160,  # Classification
       44162,  # Classification
       44132,  # Regression
       44133,  # Regression
       44134,  # Regression
       44136,  # Regression
       44137,  # Regression
       44138,  # Regression
       44139,  # Regression
       44140,  # Regression
       44141,  # Regression
       44142,  # Regression
       44144,  # Regression
       44145,  # Regression
       44147,  # Regression
       44148,  # Regression
       44025,  # Regression
       44026,  # Regression
       44054,  # Regression
       44055,  # Regression
       44056,  # Regression
       44059,  # Regression
       44062,  # Regression
       44063,  # Regression
       44064,  # Regression
       44066]  # Regression

for dataset_id in ids:
    # Load the dataset
    dataset = openml.datasets.get_dataset(dataset_id)

    # Get the data as a DataFrame, including the target column
    X, y, _, _ = dataset.get_data(target=dataset.default_target_attribute)

    # Combine features and target into a single DataFrame
    df = X.copy()
    df["target"] = y  # Rename target column to "target"

    df.to_csv(f"./{str(dataset_id)}.csv" )
