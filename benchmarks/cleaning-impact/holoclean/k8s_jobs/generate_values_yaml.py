import yaml

# Prevent PyYAML from using anchors/aliases
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

datasets = [
    "beers",
    "bridges",
    "cars",
    "flights",
    "food",
    "rayyan",
    "restaurant",
    "tax"
]

scenarios = [
    "original",
    "missing_ecar",
    "scenario"
]

multi_version_scenarios = {
    "original": [""],
    "missing_ecar": [str(i) for i in range(10)],
    "scenario": [str(i) for i in range(10)]
}

experiments = []
for dataset in datasets:
    scenario_list = []
    for scenario in scenarios:
        versions = multi_version_scenarios[scenario][:]
        scenario_list.append({
            "name": scenario,
            "versions": versions
        })
    experiments.append({
        "dataset": dataset,
        "scenarios": scenario_list,
        "memory": "256Gi" if dataset in ['tax', 'beers', 'food'] else "64Gi"
    })

values = {
    "experiments": experiments,
    "image": {
        "repository": "larmor27/hc36",
        "tag": "latest"
    },
    "postgres": {
        "image": "postgres:11",
        "user": "holocleanuser",
        "password": "abcd1234",
        "database": "holo"
    },
    "volumes": {
        "dataPVC": "cleaning-impact-data",
        "dataMountPath": "/home/data",
        "resultsPVC": "cleaning-impact-results",
        "resultsMountPath": "/home/results"
    }
}

with open("values.yaml", "w") as f:
    yaml.dump(values, f, sort_keys=False, Dumper=NoAliasDumper)

print("✅ values.yaml generated without anchors.")
