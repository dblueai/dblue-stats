import json

from dblue_stats.schema import JSONSchema
from dblue_stats.stats.tabular import TabularDataStats

data_file_path = "data/bank-churn-dataset-v2.csv"
target_column_name = "Exited"
schema_output_path = "data/bank-churn-schema-v2.json"
stats_output_path = "data/bank-churn-statistics-v2.json"
baseline_path = "data/bank-churn-statistics.json"


def main():
    # Schema
    schema = JSONSchema.from_csv(
        uri=data_file_path, target_column_name=target_column_name, output_path=schema_output_path
    )

    print(json.dumps(schema, indent=4))

    with open(baseline_path) as f:
        baseline = json.load(f)

    # Stats
    stats = TabularDataStats.from_csv(
        uri=data_file_path,
        target_column_name=target_column_name,
        output_path=stats_output_path,
        schema=schema,
        baseline=baseline,
    )

    print(json.dumps(stats, indent=4))


if __name__ == "__main__":
    main()
