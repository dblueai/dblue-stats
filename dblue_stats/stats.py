import json
import os
from typing import Dict

import numpy as np
import pandas as pd

from dblue_stats.exceptions import DblueDataStatsException
from dblue_stats.version import VERSION


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

        distinct_values = column.unique()
        is_bool = len(set(distinct_values) - {0, 1}) == 0

        if is_bool:
            data_type = "string"

        return data_type

    @classmethod
    def get_missing_count(cls, column: pd.Series):
        return int(column.isnull().sum())

    @classmethod
    def get_quantiles(cls, column: pd.Series):
        # 0 - 1 21 quantiles
        _quantiles = column.quantile(np.linspace(start=0, stop=1, num=21)).to_dict()

        _quantiles = {str(int(k * 100)): v for k, v in _quantiles.items()}

        return _quantiles

    @classmethod
    def get_numerical_distribution(cls, column: pd.Series):
        # distinct_values = column.unique()
        # if len(distinct_values) <= 20:
        #     return {}

        bin_size = 10

        labels = [str(x + 1) for x in range(bin_size)]
        cuts, bins = pd.cut(x=column, bins=bin_size, precision=2, labels=labels, retbins=True)

        value_counts = cuts.value_counts(normalize=True, sort=False).to_dict()

        distribution = []

        for index, bin_value in enumerate(bins[:-1]):
            _bin = {
                "lower_bound": bin_value,
                "upper_bound": bins[index + 1],
                "percent": value_counts[str(index + 1)] * 100  # Normalize to 100
            }

            distribution.append(_bin)

        return distribution

    @classmethod
    def get_categorical_distribution(cls, column: pd.Series):
        value_counts = column.value_counts(normalize=True, sort=False).to_dict()

        return value_counts

    @classmethod
    def get_numerical_stats(cls, column: pd.Series):
        describe = column.describe().to_dict()

        quantiles = cls.get_quantiles(column=column)
        distribution = cls.get_numerical_distribution(column=column)

        stats = {
            "mean": describe["mean"],
            "sum": float(column.sum()),
            "std_dev": describe["std"],
            "min": describe["min"],
            "max": describe["max"],
            "quantiles": quantiles,
            "distribution": distribution,
        }

        return stats

    @classmethod
    def get_categorical_stats(cls, column: pd.Series):
        value_counts = cls.get_categorical_distribution(column=column)

        distinct_count = len(value_counts.keys())
        _top = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[0][0]

        distribution = []
        for k, v in value_counts.items():
            distribution.append({
                "name": str(k),
                "percent": v * 100  # Normalize to 100
            })

        stats = {
            "distinct_count": distinct_count,
            "top": str(_top),
            "distribution": distribution
        }

        return stats

    @classmethod
    def get_dist_by_class(cls, df: pd.DataFrame, target_stats: Dict, feature_column_name, target_column_name):

        _dist_by_class = []

        if target_stats["data_type"] in ["integer", "number"]:
            for target_dist in target_stats["numerical_stats"]["distribution"]:
                target_lower_bound = target_dist["lower_bound"]
                target_upper_bound = target_dist["upper_bound"]
                temp_df2 = df[(df[target_column_name] >= target_lower_bound) & (
                        df[feature_column_name] < target_upper_bound)]

                _dist_by_class.append({
                    "lower_bound": target_lower_bound,
                    "upper_bound": target_upper_bound,
                    "percent": (len(temp_df2) / len(df)) * 100
                })
        else:
            value_counts = df[target_column_name].value_counts(normalize=True, sort=False).to_dict()

            # Convert keys to string in case it's not already
            value_counts = {str(k): v for k, v in value_counts.items()}

            for target_class in target_stats["categorical_stats"]["distribution"]:
                _dist_by_class.append({
                    "class_name": target_class["name"],
                    "percent": value_counts.get(target_class["name"], 0) * 100
                })

        return _dist_by_class

    @classmethod
    def get_feature_distribution_by_target(cls, df: pd.DataFrame, target_column_name: str, baseline_stats: Dict):
        target_stats = baseline_stats["target"]

        for feature in baseline_stats["features"]:
            column_name = feature["name"]
            _df = df[[column_name, target_column_name]]

            if feature["data_type"] in ["integer", "number"]:
                distribution = feature["numerical_stats"]["distribution"]

                for dist in distribution:
                    lower_bound = dist["lower_bound"]
                    upper_bound = dist["upper_bound"]

                    temp_df = _df[(_df[column_name] >= lower_bound) & (_df[column_name] < upper_bound)]

                    dist_by_class = cls.get_dist_by_class(
                        df=temp_df,
                        target_stats=target_stats,
                        feature_column_name=column_name,
                        target_column_name=target_column_name
                    )

                    dist["by_class"] = dist_by_class
            else:
                distribution = feature["categorical_stats"]["distribution"]

                for dist in distribution:
                    temp_df = _df[_df[column_name] == dist["name"]]

                    dist_by_class = cls.get_dist_by_class(
                        df=temp_df,
                        target_stats=target_stats,
                        feature_column_name=column_name,
                        target_column_name=target_column_name
                    )

                    dist["by_class"] = dist_by_class

    @classmethod
    def get_stats(cls, df: pd.DataFrame, target_column_name: str, output_path: str = None):

        # Get number of rows in the DataFrame
        record_count = cls.get_record_count(df=df)

        features = []
        target = None

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

            if column_name == target_column_name:
                target = item
            else:
                features.append(item)

        baseline_stats = {
            "version": "py-{}".format(VERSION),
            "dataset": {
                "item_count": record_count,
            },
            "features": features,
            "target": target,
        }

        # Get feature value distribution by target values
        cls.get_feature_distribution_by_target(
            df=df,
            target_column_name=target_column_name,
            baseline_stats=baseline_stats
        )

        # Save output in a file
        if output_path:
            cls.save_stats_output(baseline_stats, output_path)

        return baseline_stats

    @classmethod
    def from_pandas(cls, df: pd.DataFrame, target_column_name: str, output_path: str = None):
        if df is None or df.empty:
            raise DblueDataStatsException("Pandas DataFrame can't be empty")

        return cls.get_stats(df=df, target_column_name=target_column_name, output_path=output_path)

    @classmethod
    def from_csv(cls, uri, target_column_name: str, output_path: str = None):
        if not os.path.exists(uri):
            raise DblueDataStatsException("CSV file not found at %s", uri)

        df = pd.read_csv(uri)

        return cls.get_stats(df=df, target_column_name=target_column_name, output_path=output_path)

    @classmethod
    def from_parquet(cls, uri, target_column_name: str, output_path: str = None):
        if not os.path.exists(uri):
            raise DblueDataStatsException("Parquet file not found at %s", uri)

        df = pd.read_parquet(uri, engine="fastparquet")

        return cls.get_stats(df=df, target_column_name=target_column_name, output_path=output_path)

    @classmethod
    def save_stats_output(cls, stats: Dict, output_path: str):

        if not output_path.endswith(".json"):
            output_path = "{}.json".format(output_path)

        with open(output_path, "w") as f:
            json.dump(stats, f, indent=4)
