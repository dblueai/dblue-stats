import json

from dblue_stats.schema import JSONSchema
from dblue_stats.stats import DataBaselineStats

data_file_path = 'data/house-price-dataset.csv'
target_column_name = "SalePrice"
schema_output_path = "data/house-price-schema.json"
stats_output_path = "data/house-price-statistics.json"


def main():
    # Schema
    schema = JSONSchema.from_csv(
        uri=data_file_path,
        target_column_name=target_column_name,
        output_path=schema_output_path
    )

    print(json.dumps(schema, indent=4))

    # Stats
    stats = DataBaselineStats.from_csv(
        uri=data_file_path,
        target_column_name=target_column_name,
        output_path=stats_output_path,
        schema=schema
    )

    print(json.dumps(stats, indent=4))


if __name__ == '__main__':
    main()
