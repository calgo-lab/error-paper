import os
import json
import subprocess

def run_task(config):
    """
    Run a jar with specified dataset.
   Returns:
        subprocess.CompletedProcess: Result of the subprocess execution
    
    Raises:
        FileNotFoundError: If the dataset file doesn't exist
        subprocess.CalledProcessError: If the Java command fails
    """

    jar_name = config['jar_name']
    dataset = config['dataset']
    if jar_name == 'CreateMatrix.jar':
        dataset_path = f"{dataset}.csv"
    elif jar_name == 'Domino.jar':
        dataset_path = f"datasets/{dataset}.csv"
    else:
        raise ValueError('Invalid jar specified')
    
    # Construct the Java command
    java_command = [
        'java',
        '-jar',
        '-Xms2g',
        '-Xmx52g',
        jar_name,
        dataset_path,
        'true',
        ',',
        'empty',
        'false',
        '6',
        'true'
    ]
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            java_command,
            check=True,
            capture_output=True,
            text=True
        )
        print("Command executed successfully")
        print("Output:", result.stdout)
        return result
    
    except subprocess.CalledProcessError as e:
        print(f"Error running Java command: {e}")
        print("Error output:", e.stderr)
        raise

def main():
    if os.getenv('CONFIG') is None:
        raise ValueError('Aborting: No config set')

    config = json.loads(os.getenv('CONFIG'))
    experiment_id = os.getenv('EXPERIMENT_ID')

    try:
        run_task(config)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error calculating matrix for config {config}: {e}")

if __name__ == "__main__":
    main()
