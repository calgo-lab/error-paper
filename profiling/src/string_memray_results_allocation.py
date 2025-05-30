import os
import re
import subprocess
import json

# Due to the lack of an API (the memray library is better suited for live profiling of code or test integration) one must parse the subprocess output

def get_total_allocated_memory(filepath):
    try:
        result = subprocess.run(
            ["memray", "stats", filepath],
            capture_output=True
        )

        output = result.stdout.decode("utf-8")

        # Remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        clean_output = ansi_escape.sub('', output)

        match = re.search(r"Total memory allocated:\s*\n\s*([\d.]+[KMGT]?B)", clean_output)
        if match:
            return match.group(1)
        else:
            print(f"Could not find total memory allocated in output:\n{output}")
            return None
    except Exception as e:
        print(f"Error running memray on {filepath}: {e}")
        raise ValueError
    


def get_data(directory):
    pattern = re.compile(r'^(?P<mechanism>[A-Z]+)-(?P<type>[a-zA-Z0-9]+)-(?P<rate>[0-9.]+)-(?P<nrow>\d+)-(?P<ncol>\d+)-(?P<runnumber>\d+)\.bin$')
    parsed_data = []

    for filename in os.listdir(directory):
        if not filename.endswith(".bin"):
            continue
        
        match = pattern.match(filename)
        if match:
            info = match.groupdict()
            filepath = os.path.join(directory, filename)
            info["rate"] = float(info["rate"])
            info["nrow"] = int(info["nrow"])
            info["ncol"] = int(info["ncol"])
            info["runnnumber"] = int(info["runnumber"])
            info["filepath"] = filepath
            info["total_memory"] = get_total_allocated_memory(filepath)
            parsed_data.append(info)
        else:
            print(f"Skipping unrecognized file format: {filename}")
    return parsed_data

def main():
    print("Entry")
    directory = "../results/string"
    data = get_data(directory)
    print("Data: ", data[:5])
    # Write to JSON
    with open("../results/string_mem_result.json", "w") as f:
        json.dump(data, f, indent=2)
    print("write complete")

if __name__ == "__main__":
    main()
