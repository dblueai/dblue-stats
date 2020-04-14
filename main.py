import pandas as pd

from dblue_data_stats.stats import DataBaselineStats

data_file_path = 'data/bank-churn-dataset.csv'


def main():
    df = pd.read_csv(data_file_path)

    stats = DataBaselineStats.from_pandas(df=df)
    print(stats)


if __name__ == '__main__':
    main()
