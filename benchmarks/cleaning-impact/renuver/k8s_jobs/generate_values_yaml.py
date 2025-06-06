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
    "original": ["0"],
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
        "scenarios": scenario_list
    })

values = {
    "experiments": experiments,
    "image": {
        "repository": "larmor27/renuver",
        "tag": "latest"
    },
}

with open("values.yaml", "w") as f:
    yaml.dump(values, f, sort_keys=False, Dumper=NoAliasDumper)

print("✅ values.yaml generated without anchors.")
