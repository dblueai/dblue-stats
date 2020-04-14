import json

from dblue_data_stats.stats import DataBaselineStats

data_file_path = 'data/bank-churn-dataset.csv'


def main():
    stats = DataBaselineStats.from_csv(uri=data_file_path)
    print(json.dumps(stats, indent=4))


if __name__ == '__main__':
    main()
