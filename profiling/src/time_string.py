from __future__ import annotations
import cpuinfo
import time
import random
import platform
import psutil
import numpy as np
import pandas as pd
from memory_profiler import memory_usage
from tab_err import error_mechanism, error_type
from tab_err.error_type import ErrorTypeConfig
from tab_err.api import low_level



def timing_function(func: any, *args: tuple, runs: int = 10, **kwargs: dict[str, any]) -> tuple[list[float], list[float], float, float]:
    """Times a function and tracks memory usage over multiple runs.

    Args:
        func (Callable): The function to be timed.
        *args (tuple): Positional arguments to pass to the function.
        runs (int, optional): Number of times to run the function. Defaults to 10.
        **kwargs (dict[str, any]): Keyword arguments to pass to the function.

    Returns:
        tuple:
            - list[float]: Execution times (in seconds) for each run.
            - list[float]: Peak memory usage differences (in MB) for each run
            - float: Mean execution time over all runs.
            - float: Standard deviation of execution times.
    """
    times = []
    mem_usages = []
    
    for _ in range(runs):
        # Clear memory stats before run
        
        # Time it
        start = time.time()
        mem_usage, result = memory_usage((func, args, kwargs),retval=True, max_usage=True, interval=0.01)
        end = time.time()


        # Record result
        times.append(end - start)
        mem_usages.append(mem_usage)  # Convert to MB
        
    # Compute statistics
    mean_time = np.mean(times)
    std_time = np.std(times)
    
    return times, mem_usages, mean_time, std_time


def print_processor_info():
    """Prints the CPU model/name."""
    # Try to use py-cpuinfo for exact model name
    try:
        info = cpuinfo.get_cpu_info()
        # brand_raw is the most descriptive field
        processor_name = info.get("brand_raw") or info.get("cpu") or info.get("processor") or "Unknown"
    except ImportError:
        # Fallback if py-cpuinfo isn’t installed
        processor_name = platform.processor() or "Unknown"
    except Exception as e:
        print(f"Warning: failed to get detailed CPU info: {e}")
        processor_name = platform.processor() or "Unknown"

    print("=== CPU Info ===")
    print(f"Processor Model:   {processor_name}")


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
    
    print_processor_info()



def random_df(rows: int, cols: int, base_str: str = "测试-test-123", col_prefix: str = "col", rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Generates a DataFrame with random string values.

    Args:
        rows (int): Number of rows in the DataFrame.
        cols (int): Number of columns in the DataFrame.
        base_str (str): The string to fill each cell with.
        col_prefix (str, optional): Prefix for column names. Defaults to "col".
        rng (np.random.Generator, optional): Random number generator. Defaults to None, which creates a new generator.

    Returns:
        pd.DataFrame: DataFrame with shape (rows, cols) filled with random values.
    """
    rng = rng or np.random.default_rng()
    data = [[base_str] * cols for _ in range(rows)]
    columns = [f"{col_prefix}{i}" for i in range(cols)]
    return pd.DataFrame(data, columns=columns)


def time_one_error_model_string(desc_string: str, e_mech: error_mechanism, e_type: error_type, e_rate: float = 0.5, max_n: int = 1000000, runs: int = 100):  # noqa: E501, PLR2044
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
    # Create data
    # Generate datasets with row counts multiplying by 10 each time
    results = {}
    memory_usages = {}
    
    n_row = 100  # Start from 100 rows
    while n_row <= max_n:
        n_col = 2
        while n_col <= 10:
            one_instance_string = desc_string + f"-{n_row}-{n_col}"
            print(one_instance_string)
            time_arr, mem_arr, _, _ = timing_function(low_level.create_errors, runs=runs,
                        data= random_df(n_row, n_col), column="col0",
                        error_rate=e_rate, error_mechanism=e_mech, error_type=e_type)
            results[one_instance_string] = time_arr
            memory_usages[one_instance_string + "-mem_MB"] = mem_arr
            n_col += 2
        n_row *= 10
    return pd.concat([pd.DataFrame(results), pd.DataFrame(memory_usages)], axis=1)


def time_tab_err_string(max_n: int = 1000000, runs: int = 100, seed: int | None = 42, write_path: str = "../results/string_times_new.csv") -> pd.DataFrame:  # noqa: E501
    """Times the tab error library for all combinations of error mechanism/model.

    Description:
        1. Generates a bunch of data for running the tab_error library.
        2. Iterates over the error models and gets timing for `runs` runs.
        3. Writes a file with a dataframe where the rows are the times and cols are the errormodel-benchmarkconfig descriptions
            - Note: errormodel-benchmark config desc: errormech-errortype-errorrate-nrows-nruns

    """
    # Set constants
    dataframes = []
    e_type_dict = {
        "Mojibake": error_type.Mojibake(),
        "Replace": error_type.Replace(ErrorTypeConfig(replace_what="-", replace_with="_")),
        "MissingValue": error_type.MissingValue(),
        "Typo": error_type.Typo(),
        "PermutateRandom": error_type.Permutate({"permutation_separator": "-", "permutation_automation_pattern": "random"}),
        "PermutateFixed": error_type.Permutate({"permutation_separator": "-", "permutation_automation_pattern": "fixed"})
    }
    e_rate_list = [0.1, 0.25, 0.5, 0.75, 0.9]
    if seed is not None:
        np.random.seed(seed)  # noqa: NPY002
        random.seed(seed)

    # EAR - hits all errormech/type combos for EAR mech
    e_mech = error_mechanism.EAR(condition_to_column="col1")
    e_mech_name = "EAR"
    for e_type_name, e_type in e_type_dict.items():
        for e_rate in e_rate_list:
            desc = f"{e_mech_name}-{e_type_name}-{e_rate}"
            dataframes.append(time_one_error_model_string(desc, e_mech, e_type, e_rate, max_n, runs))

    # ENAR
    e_mech = error_mechanism.ENAR()
    e_mech_name = "ENAR"
    for e_type_name, e_type in e_type_dict.items():
        for e_rate in e_rate_list:
            desc = f"{e_mech_name}-{e_type_name}-{e_rate}"
            dataframes.append(time_one_error_model_string(desc, e_mech, e_type, e_rate, max_n, runs))

    # ECAR
    e_mech = error_mechanism.ECAR()
    e_mech_name = "ECAR"
    for e_type_name, e_type in e_type_dict.items():
        for e_rate in e_rate_list:
            desc = f"{e_mech_name}-{e_type_name}-{e_rate}"
            dataframes.append(time_one_error_model_string(desc, e_mech, e_type, e_rate, max_n, runs))

    merged_df = pd.concat(dataframes, axis=1)
    merged_df.to_csv(write_path, index=False)

    return merged_df

def main():
    df = time_tab_err_string()  # Default params are good for the experiment
    print_system_specs()
    print(df)

if __name__ == "__main__":
    main()
