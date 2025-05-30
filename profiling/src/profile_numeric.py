# Nick Chandler
# 28.04.2025
# Time tab error for numeric error types

from __future__ import annotations
import time
import random
import os
import platform
import psutil
import numpy as np
import pandas as pd
from tab_err import error_mechanism, error_type
from tab_err.api import low_level
import memray
from concurrent.futures import ProcessPoolExecutor, as_completed


def random_df(rows: int, cols: int, col_prefix: str = "col", rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Generates a DataFrame with random values.

    Args:
        rows (int): Number of rows in the DataFrame.
        cols (int): Number of columns in the DataFrame.
        col_prefix (str, optional): Prefix for column names. Defaults to "col".
        rng (np.random.Generator, optional): Random number generator. Defaults to None, which creates a new generator.

    Returns:
        pd.DataFrame: DataFrame with shape (rows, cols) filled with random values.
    """
    rng = rng or np.random.default_rng()
    data = rng.random((rows, cols))  # uniform [0, 1) values
    columns = [f"{col_prefix}{i}" for i in range(cols)]
    return pd.DataFrame(data, columns=columns)


def timing_function(func: callable, *args, runs: int = 10, **kwargs) -> tuple[list[float], list[float], float, float]:
    """
    Times a function and tracks peak memory usage (MB) over multiple runs using memray.

    Args:
        func (callable): The function to be timed.
        *args: Positional arguments for the function.
        runs (int): Number of times to run the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        tuple:
            - list of execution times (seconds) for each run,
            - list of peak memory usage differences (MB) for each run,
            - mean execution time,
            - std dev of execution time
    """
    times = []

    for r in range(runs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()

        times.append(end - start)

    return times

def memory_function(func: callable, *args, runs: int = 10, experiment_name: str = "", **kwargs) -> tuple[list[float], list[float], float, float]:
    """Uses memray to get memory allocations of func call. Returns nothing, saves the result to the .bin file."""
    for r in range(runs):
        with memray.Tracker(f"../results/numeric/{experiment_name}-{r}.bin"):
            func(*args, **kwargs)


def print_system_specs() -> None:
    """Prints system specifications including OS, CPU, and RAM."""
    print("=== System Info ===")
    
    # OS and architecture
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Machine Architecture: {platform.machine()}")
    
    # CPU core count (physical and logical)
    print(f"CPU Cores (Physical): {psutil.cpu_count(logical=False)}")
    print(f"CPU Cores (Logical): {psutil.cpu_count(logical=True)}")
    
    # Total RAM (in GB)
    ram = psutil.virtual_memory().total / 1e9  # GB
    print(f"Total RAM: {ram:.2f} GB")
    
    # Processor info
    processor_name = platform.processor() or "Unknown"

    print("=== CPU Info ===")
    print(f"Processor Model:   {processor_name}")


def profile_one_instance(n_row: int, n_col: int, e_rate: float, desc_string: str, e_mech: error_mechanism, e_type: error_type, runs: int = 10):
    """Profiles one combo of mech-type-rate-nrow-ncol."""
    one_instance_string = desc_string + f"-{str(e_rate)}-{n_row}-{n_col}"
    print(one_instance_string)

    data = random_df(n_row, n_col)

    # Time
    time_arr = timing_function(low_level.create_errors, runs=runs,
                        data=data, column="col0",
                        error_rate=e_rate, error_mechanism=e_mech, error_type=e_type)

    # Space - saved as .bin file
    memory_function(low_level.create_errors, runs=runs, experiment_name=one_instance_string,
                        data=data, column="col0",
                        error_rate=e_rate, error_mechanism=e_mech, error_type=e_type)
    
    return one_instance_string, time_arr


def time_one_error_model_numeric(desc_string: str, e_mech: error_mechanism, e_type: error_type, runs: int = 10, max_workers=os.cpu_count()):  # noqa: E501, PLR2044
    """
    Benchmarks the performance and memory usage of applying an error model to data of increasing size.

    For each row count (from 100 up to `max_n`, increasing by a factor of 10), the function generates a random
    DataFrame and applies the error model multiple times. It records execution time and memory usage per run.

    Args:
        desc_string (str): Identifier string formatted as "errormech-errortype-errorrate".
        e_mech (error_mechanism): The error mechanism to apply (e.g., MCAR, MAR, EAR).
        e_type (error_type): The type of error to introduce (e.g., deletion, corruption).
        e_rate (float, optional): Proportion of rows to be affected by the error. Defaults to 0.5.
        max_n (int, optional): Maximum number of rows to test. Starts at 100 and increases by a factor of 10. Defaults to 1,000,000.
        runs (int, optional): Number of repetitions for each configuration to collect timing and memory stats. Defaults to 100.

    Returns:
        pd.DataFrame: A DataFrame with timing and memory results. Columns are:
            - "<desc_string>-<n_rows>-<n_cols>": Execution times for each run.
            - "<desc_string>-<n_rows>-<n_cols>-mem_MB": Memory usage in MB for each run.
    """
    results = {}

    possible_nrow = [100, 1000, 10000, 100000, 1000000]
    possible_ncol = [2, 4, 6, 8, 10]
    e_rate_list = [0.1, 0.25, 0.5, 0.75, 0.9]

    tasks = [(r, c, er) for r in possible_nrow for c in possible_ncol for er in e_rate_list]  # n_row, n_col combos
    tasks = sorted(tasks, key=lambda x: x[0], reverse=True)  # sort by nrow so the largest jobs are scheduled first - Thanks Tarek!

    with ProcessPoolExecutor(max_workers = max_workers) as executor:
        # Send out jobs
        futures = {
            executor.submit(profile_one_instance, n_row, n_col, e_rate, desc_string, e_mech, e_type, runs): (n_row, n_col, e_rate)
            for n_row, n_col, e_rate in tasks
        }

        # Aggregate results
        for future in as_completed(futures):
            try:
                instance_string, time_arr = future.result()
                results[instance_string] = time_arr
            except Exception as e:
                print(f"Error for task {futures[future]}: {e}")

    return pd.DataFrame(results)



# This boi is a monster - test it out with max_n = 100, runs = 2 (need to calc variance)
def time_tab_err_numeric(runs: int = 100, seed: int | None = 42, write_path: str = "../results/numeric_times.csv") -> pd.DataFrame:  # noqa: E501
    """Times the tab error library for all combinations of error mechanism/model.

    Description:
        1. Generates a bunch of data for running the tab_error library.
        2. Iterates over the error models and gets timing for `runs` runs.
        3. Writes a file with a dataframe where the rows are the times and cols are the errormodel-benchmarkconfig descriptions
            - Note: errormodel-benchmark config desc: errormech-errortype-errorrate-nrows-nruns

    """
    # Set constants
    dataframes = []
    e_type_dict = {"AddDelta": error_type.AddDelta(),
                   "MissingValue": error_type.MissingValue()
    }
    if seed is not None:
        np.random.seed(seed)  # noqa: NPY002
        random.seed(seed)

    # EAR - hits all errormech/type combos for EAR mech
    e_mech = error_mechanism.EAR(condition_to_column="col1")
    e_mech_name = "EAR"
    for e_type_name, e_type in e_type_dict.items():
        desc = f"{e_mech_name}-{e_type_name}"
        dataframes.append(time_one_error_model_numeric(desc, e_mech, e_type, runs))

    # ENAR
    e_mech = error_mechanism.ENAR()
    e_mech_name = "ENAR"
    for e_type_name, e_type in e_type_dict.items():
        desc = f"{e_mech_name}-{e_type_name}"
        dataframes.append(time_one_error_model_numeric(desc, e_mech, e_type, runs))

    # ECAR
    e_mech = error_mechanism.ECAR()
    e_mech_name = "ECAR"
    for e_type_name, e_type in e_type_dict.items():
        desc = f"{e_mech_name}-{e_type_name}"
        dataframes.append(time_one_error_model_numeric(desc, e_mech, e_type, runs))

    merged_df = pd.concat(dataframes, axis=1)
    merged_df.to_csv(write_path, index=False)
    return merged_df

def main():
    df = time_tab_err_numeric()  # Default params are good for the experiment
    print_system_specs()
    print(df)

if __name__ == "__main__":
    main()
    