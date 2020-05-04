import json

from dblue_stats.stats import DataBaselineStats

data_file_path = 'data/bank-churn-dataset.csv'
target_column_name = "Exited"
output_path = "data/bank-churn-statistics.json"


# data_file_path = 'data/house-price.csv'
# target_column_name = "SalePrice"
# output_path = "data/house-price-statistics.json"


def main():
    stats = DataBaselineStats.from_csv(
        uri=data_file_path,
        target_column_name=target_column_name,
        output_path=output_path
    )
    print(json.dumps(stats, indent=4))


if __name__ == '__main__':
    main()
