import pandas as pd
from functools import partial
from sklearn.metrics import r2_score  # This is fine since we are comparing models - when looking at model performance on a task, RMSE would be better
from sklearn.ensemble import HistGradientBoostingRegressor
import sys
import os
from sklearn.model_selection import KFold
from tab_err.api import high_level
from tab_err import error_type, error_mechanism
from sklearn.base import BaseEstimator
from typing import Callable
from sklearn.preprocessing import OrdinalEncoder


def evaluate_on_dirty_data(data, error_rate, model, evaluation_function, n_splits=5, error_types_to_exclude = None, error_types_to_include = None, error_mechanisms_to_exclude = None, seed=None):
    """Trains a model using kfold cv and returns a list of the performances on the clean test sets and the error'd test sets, as well as the proportion of errors introduced."""
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    clean_acc = []
    dirty_acc = []

    for k, (train_idx, test_idx) in enumerate(kf.split(data)):
        # Split the data
        df_train, df_test = data.iloc[train_idx], data.iloc[test_idx]
        x_train, y_train = df_train.drop(columns=["target"]), df_train["target"]
        x_test, y_test = df_test.drop(columns=["target"]), df_test["target"]

        # Use high level api on x_test - perturb dataset
        x_test_perturbed, error_mask = high_level.create_errors(
            x_test,
            error_rate=error_rate,
            error_types_to_exclude=error_types_to_exclude,
            error_types_to_include=error_types_to_include,
            error_mechanisms_to_exclude=error_mechanisms_to_exclude,
            seed=(seed + k)
        )

        # Build the encoder for categorical types
        categorical_columns = x_train.select_dtypes(include=["object"]).columns
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        x_train[categorical_columns] = encoder.fit_transform(x_train[categorical_columns].astype(str))
        x_test[categorical_columns] = encoder.transform(x_test[categorical_columns].astype(str))
        x_test_perturbed[categorical_columns] = encoder.transform(x_test_perturbed[categorical_columns].astype(str))

        # Fit the model
        model.fit(x_train, y_train)  # Logistic regression

        # Predict on the clean test
        y_pred_clean = model.predict(x_test)
        acc_clean = evaluation_function(y_test, y_pred_clean)
        clean_acc.append(acc_clean)

        # Predict on the dirty test
        y_pred_dirty = model.predict(x_test_perturbed)
        acc_dirty = evaluation_function(y_test, y_pred_dirty)
        dirty_acc.append(acc_dirty)

    return clean_acc, dirty_acc, error_mask.values.mean()

def print_acc(acc_list, result_name):
    print(
    "Accuracies of ", result_name, " test data: ",
    acc_list,
    f"Mean accuracy: { (sum(acc_list) / len(acc_list)):.4f}" if acc_list else "Mean accuracy: None"
    )


def min_max_normalize_df(data: pd.DataFrame) -> pd.DataFrame:
    """Min max normalizes based on all values in the dataframe."""
    overall_min = data.min(axis=None)
    overall_max = data.max(axis=None)
    
    return (data - overall_min)/(overall_max-overall_min)


def create_experiment_dataframe(error_rate: float, machine_learning_model: str, evaluation_metric:str, list_of_experiment_descriptions: list[str], list_of_lists_of_scores: list[list[float]], random_seed: int | None = None) -> pd.DataFrame:
    """Creates a pandas dataframe with lists of scores for a machine learning model applied to errored data."""
    if len(list_of_lists_of_scores) < 1:
        msg = "Must pass in a non-empty list of list of scores."
        ValueError(msg)

    if len(list_of_lists_of_scores) != len(list_of_experiment_descriptions):
        msg = "Number of score lists and number of descriptions do not match"
        ValueError(msg)

    if (nrows := len(list_of_lists_of_scores[0]) < 1):
        msg = "The number of scores needs to be at least 1"
        ValueError(msg)

    dictionary = {description:scores for description, scores in zip(list_of_experiment_descriptions, list_of_lists_of_scores)}
    
    # Add experiment metadata
    nrows = len(list_of_lists_of_scores[0])
    dictionary["error_rate"] = [error_rate]*nrows
    dictionary["machine_learning_model"] = [machine_learning_model]*nrows
    dictionary["evaluation_metric"] = [evaluation_metric]*nrows

    if random_seed:
        dictionary["random_seed"] = [random_seed]*nrows
    
    print("Dictionary", dictionary)
    return pd.DataFrame(dictionary)   

def run_error_mechanism_experiment(data: pd.DataFrame, error_rate: float, machine_learning_model: BaseEstimator, evaluation_function: Callable, seed: int, folds: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Produces a dataframe with evaluation_function scores as the columns and the column titles as the description of each case."""
    machine_learning_model.set_params(random_state=seed)
    
    # Run ML models
    clean_acc, dirty_acc, dirty_error_prop = evaluate_on_dirty_data(data, error_rate=error_rate, evaluation_function=evaluation_function, model=machine_learning_model, n_splits=folds, error_types_to_include=[error_type.WrongUnit(), error_type.Typo()], seed=seed)
    clean_acc, no_ear_enar_acc, no_ear_enar_error_prop = evaluate_on_dirty_data(data, error_rate=error_rate, evaluation_function=evaluation_function, model=machine_learning_model, n_splits=folds, error_types_to_include=[error_type.WrongUnit(), error_type.Typo()], error_mechanisms_to_exclude=[error_mechanism.EAR(), error_mechanism.ENAR()], seed=seed)
    clean_acc, no_enar_ecar_acc, no_enar_ecar_error_prop = evaluate_on_dirty_data(data, error_rate=error_rate, evaluation_function=evaluation_function, model=machine_learning_model, n_splits=folds, error_types_to_include=[error_type.WrongUnit(), error_type.Typo()], error_mechanisms_to_exclude=[error_mechanism.ENAR(), error_mechanism.ECAR()], seed=seed)
    clean_acc, no_ear_ecar_acc, no_ear_ecar_error_prop = evaluate_on_dirty_data(data, error_rate=error_rate, evaluation_function=evaluation_function, model=machine_learning_model, n_splits=folds, error_types_to_include=[error_type.WrongUnit(), error_type.Typo()], error_mechanisms_to_exclude=[error_mechanism.EAR(), error_mechanism.ECAR()], seed=seed)
    
    # Compile results
    descriptions = ["clean", "ECAR", "EAR", "ENAR"]
    actual_error_proportions = [dirty_error_prop, no_ear_enar_error_prop, no_enar_ecar_error_prop, no_ear_ecar_error_prop]
    case_wise_error_props = {description:[error_proportion] for description, error_proportion in zip(descriptions[1:], actual_error_proportions)}
    scores = [clean_acc, no_ear_enar_acc, no_enar_ecar_acc, no_ear_ecar_acc]
    
    print("case_wise_error_props", case_wise_error_props)
    return create_experiment_dataframe(error_rate=error_rate, machine_learning_model=str(machine_learning_model), evaluation_metric=evaluation_function.func.__name__, list_of_experiment_descriptions=descriptions, list_of_lists_of_scores=scores), pd.DataFrame(case_wise_error_props)


def main():
    # These are set as they were in the code that generated the paper's results
    seed = 1234
    experiment_name = "regression-wrongunit-typo"
    
    ids = [ 44132,  # Regression
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
    
    # For loop over dataset_id, error_rate -- parallelize this loop
    for dataset_id in ids:
        for error_rate in [0.1, 0.25, 0.5, 0.75, 0.9]:
            folds = 10
    
            model = HistGradientBoostingRegressor(max_iter=200)
            metric = partial(r2_score)

            # Cluster setup
            dataset_directory = "./datasets"
            dataset_path = os.path.join(dataset_directory, f"{dataset_id}.csv")

            results_directory = f"./{experiment_name}/{dataset_id}/{error_rate}"
            os.makedirs(results_directory, exist_ok=True)
            result_df_path = os.path.join(results_directory, "results.csv")
            result_error_props_path = os.path.join(results_directory, "error_props.csv")
            results_finished_path = os.path.join(results_directory, "FINISHED")

            # Read in the dataset from dataset directory
            data = pd.read_csv(dataset_path)

            print("Data Head", data.head())
            print("Data datatypes", data.dtypes)

            experiment_df, experiment_error_props = run_error_mechanism_experiment(data, error_rate, model, metric, seed, folds)

            experiment_df.to_csv(result_df_path, index=False)
            experiment_error_props.to_csv(result_error_props_path, index=False)
            open(results_finished_path, "w").close()

if __name__ == "__main__":
    main()
