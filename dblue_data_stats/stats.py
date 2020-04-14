import numpy as np
import pandas as pd

from dblue_data_stats.exceptions import DblueDataStatsException
from dblue_data_stats.version import VERSION


class DataBaselineStats:
    def __init__(self):
        pass

    @classmethod
    def get_record_count(cls, df: pd.DataFrame):
        """
        Fastest way to get record count from DataFrame
        :param df:
        :return:
        """
        return len(df.index)

    @classmethod
    def infer_data_type(cls, column: pd.Series):
        types = {
            "int64": "integer",
            "float64": "number",
            "object": "string",
        }

        data_type = types.get(column.dtype.name)

        if not data_type:
            raise DblueDataStatsException("Data type not found: %s" % column.dtype.name)

        return data_type

    @classmethod
    def get_missing_count(cls, column: pd.Series):
        return column.isnull().sum()

    @classmethod
    def get_quantiles(cls, column: pd.Series):
        # 0 - 1 21 quantiles
        _quantiles = column.quantile(np.linspace(start=0, stop=1, num=21)).to_dict()

        _quantiles = {str(int(k * 100)): v for k, v in _quantiles.items()}

        return _quantiles

    @classmethod
    def get_numerical_stats(cls, column: pd.Series):
        describe = column.describe().to_dict()

        quantiles = cls.get_quantiles(column=column)

        stats = {
            "mean": describe["mean"],
            "sum": column.sum(),
            "std_dev": describe["std"],
            "min": describe["min"],
            "max": describe["max"],
            "quantiles": quantiles,
        }

        return stats

    @classmethod
    def get_categorical_stats(cls, column: pd.Series):
        value_counts = column.value_counts(normalize=True, sort=False).to_dict()

        distinct_count = len(value_counts.keys())
        _top = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[0][0]

        stats = {
            "distinct_count": distinct_count,
            "top": _top,
            "distribution": value_counts
        }

        return stats

    @classmethod
    def get_stats(cls, df: pd.DataFrame):

        # Get number of rows in the DataFrame
        record_count = cls.get_record_count(df=df)

        features = []

        for column_name in df.columns:
            column = df[column_name]
            data_type = cls.infer_data_type(column=column)

            num_missing = cls.get_missing_count(column=column)
            num_present = record_count - num_missing

            item = {
                "name": column_name,
                "data_type": data_type,
                "num_present": num_present,
                "num_missing": num_missing,
            }

            if data_type in ["integer", "number"]:
                item["numerical_stats"] = cls.get_numerical_stats(column=column)

            elif data_type == "string":
                item["categorical_stats"] = cls.get_categorical_stats(column=column)

            features.append(item)

        baseline_stats = {
            "version": "py-{}".format(VERSION),
            "dataset": {
                "item_count": record_count,
            },
            "features": features,
        }

        return baseline_stats

    @classmethod
    def from_pandas(cls, df: pd.DataFrame):
        if df is None or df.empty:
            raise DblueDataStatsException("Pandas DataFrame can't be empty")

        return cls.get_stats(df=df)

    @classmethod
    def from_csv(cls, uri):
        pass

    @classmethod
    def from_parquet(cls, uri):
        pass
