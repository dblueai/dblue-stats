import copy
import json
import os
from typing import Dict

import numpy as np
import pandas as pd
from slugify import slugify

from dblue_stats.constants import Constants
from dblue_stats.exceptions import DblueStatsException
from dblue_stats.schema import JSONSchema
from dblue_stats.version import VERSION


class TabularDataStats:
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
    def get_missing_count(cls, column: pd.Series):
        return int(column.isnull().sum())

    @classmethod
    def get_quantiles(cls, column: pd.Series):
        # 0 - 1 21 quantiles
        _quantiles = column.quantile(np.linspace(start=0, stop=1, num=21)).to_dict()

        _quantiles = {str(int(k * 100)): v for k, v in _quantiles.items()}

        return _quantiles

    @classmethod
    def get_numerical_distribution(cls, column: pd.Series, column_baseline: Dict = None):
        if column_baseline:
            bins = [x["lower_bound"] for x in column_baseline["numerical_stats"]["distribution"]]
            bins.append(column_baseline["numerical_stats"]["distribution"][-1]["upper_bound"])

            # Insert a bin if new value is less than the min value
            if column.min() < column_baseline["numerical_stats"]["min"]:
                bins.insert(0, column.min().item())

            # Insert a bin if new value is less than the max value
            if column.max() > column_baseline["numerical_stats"]["max"]:
                bins.append(column.max().item())

            bin_size = len(bins) - 1
            labels = [str(x + 1) for x in range(bin_size)]
            cuts = pd.cut(x=column, bins=bins, precision=2, labels=labels)
        else:
            bin_size = 10
            labels = [str(x + 1) for x in range(bin_size)]
            cuts, bins = pd.cut(x=column, bins=bin_size, precision=2, labels=labels, retbins=True)

        value_counts = cuts.value_counts(normalize=True).to_dict()

        distribution = []

        for index, bin_value in enumerate(bins[:-1]):
            _bin = {
                "lower_bound": bin_value,
                "upper_bound": bins[index + 1],
                "percent": value_counts[str(index + 1)] * 100,  # Normalize to 100
            }

            distribution.append(_bin)

        return distribution

    @classmethod
    def get_categorical_distribution(cls, column: pd.Series):
        value_counts = column.value_counts(normalize=True).to_dict()

        return value_counts

    @classmethod
    def get_numerical_stats(cls, column: pd.Series, column_baseline: Dict = None):
        describe = column.describe().to_dict()

        quantiles = cls.get_quantiles(column=column)
        distribution = cls.get_numerical_distribution(column=column, column_baseline=column_baseline)

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

        distribution = []
        for k, v in value_counts.items():
            distribution.append({"name": str(k), "percent": v * 100})  # Normalize to 100

        stats = {"distinct_count": distinct_count, "top": distribution[0]["name"], "distribution": distribution}

        return stats

    @classmethod
    def get_dist_by_class(cls, df: pd.DataFrame, dist_percent, target_stats: Dict, target_column_name):

        _dist_by_class = []

        if target_stats["feature_type"] == Constants.FEATURE_TYPE_NUMERICAL:
            for target_dist in target_stats["numerical_stats"]["distribution"]:
                target_lower_bound = target_dist["lower_bound"]
                target_upper_bound = target_dist["upper_bound"]
                temp_df = df[
                    (df[target_column_name] >= target_lower_bound) & (df[target_column_name] < target_upper_bound)
                ]

                absolute_percent = len(temp_df) / len(df) if not df.empty else 0

                _dist_by_class.append(
                    {
                        "lower_bound": target_lower_bound,
                        "upper_bound": target_upper_bound,
                        "relative_percent": ((dist_percent / 100) * absolute_percent) * 100,
                        "absolute_percent": absolute_percent * 100,
                    }
                )

        elif target_stats["feature_type"] == Constants.FEATURE_TYPE_CATEGORICAL:
            value_counts = df[target_column_name].value_counts(normalize=True).to_dict()

            # Convert keys to string in case it's not already
            value_counts = {str(k): v for k, v in value_counts.items()}

            for target_class in target_stats["categorical_stats"]["distribution"]:
                absolute_percent = value_counts.get(target_class["name"], 0)
                _dist_by_class.append(
                    {
                        "class_name": target_class["name"],
                        "relative_percent": ((dist_percent / 100) * absolute_percent) * 100,
                        "absolute_percent": absolute_percent * 100,
                    }
                )

        return _dist_by_class

    @classmethod
    def get_feature_distribution_by_target(cls, df: pd.DataFrame, target_column_name: str, baseline_stats: Dict):
        _baseline_stats = copy.deepcopy(baseline_stats)

        target_stats = _baseline_stats["target"]

        for feature in _baseline_stats["features"]:
            column_name = feature["display_name"]
            _df = df[[column_name, target_column_name]]

            if feature["feature_type"] == Constants.FEATURE_TYPE_NUMERICAL:
                distribution = feature["numerical_stats"]["distribution"]

                for dist in distribution:
                    lower_bound = dist["lower_bound"]
                    upper_bound = dist["upper_bound"]
                    percent = dist["percent"]

                    temp_df = _df[(_df[column_name] >= lower_bound) & (_df[column_name] < upper_bound)]

                    dist_by_class = cls.get_dist_by_class(
                        df=temp_df,
                        dist_percent=percent,
                        target_stats=target_stats,
                        target_column_name=target_column_name,
                    )

                    dist["by_class"] = dist_by_class
            elif feature["feature_type"] == Constants.FEATURE_TYPE_CATEGORICAL:
                distribution = feature["categorical_stats"]["distribution"]

                for dist in distribution:
                    # Handling boolean
                    std_data_type = JSONSchema.get_standard_data_type(_df[column_name].dtype.name)
                    dist_name = dist["name"]

                    if std_data_type == Constants.DATA_TYPE_INTEGER:
                        dist_name = int(dist_name)
                    elif std_data_type == Constants.DATA_TYPE_BOOLEAN:
                        dist_name = dist_name.lower() == "true"

                    temp_df = _df[_df[column_name] == dist_name]
                    percent = dist["percent"]

                    dist_by_class = cls.get_dist_by_class(
                        df=temp_df,
                        dist_percent=percent,
                        target_stats=target_stats,
                        target_column_name=target_column_name,
                    )

                    dist["by_class"] = dist_by_class

        return _baseline_stats

    @classmethod
    def get_stats(
        cls,
        df: pd.DataFrame,
        target_column_name: str = None,
        output_path: str = None,
        schema: Dict = None,
        baseline: Dict = None,
    ):

        if not schema:
            schema = JSONSchema.from_pandas(df=df)

        _baseline = {}

        if baseline:
            # Transform baseline stats dict for faster access to features and target
            _baseline = {x["name"]: x for x in baseline.get("features", [])}

            if baseline.get("target"):
                _baseline[baseline["target"]["name"]] = baseline.get("target")

        schema_properties = schema.get("properties")
        # Get number of rows in the DataFrame
        record_count = cls.get_record_count(df=df)

        features = []
        target = None

        for column_name in df.columns:
            column = df[column_name]

            column_slug = slugify(column_name, separator="_")
            column_schema = schema_properties.get(column_slug)
            column_baseline = _baseline.get(column_slug)

            if not column_schema:
                raise DblueStatsException("Column not found in the schema: %s" % column_name)

            data_type = column_schema.get("type")
            feature_type = column_schema.get("meta", {}).get("feature_type")

            num_missing = cls.get_missing_count(column=column)
            num_present = record_count - num_missing

            item = {
                "name": column_slug,
                "display_name": column_name,
                "data_type": data_type,
                "feature_type": feature_type,
                "num_present": num_present,
                "num_missing": num_missing,
            }

            if feature_type == Constants.FEATURE_TYPE_NUMERICAL:
                item["numerical_stats"] = cls.get_numerical_stats(column=column, column_baseline=column_baseline)

            elif feature_type == Constants.FEATURE_TYPE_CATEGORICAL:
                item["categorical_stats"] = cls.get_categorical_stats(column=column)

            if column_name == target_column_name:
                target = item
            else:
                features.append(item)

        baseline_stats = {
            "version": "py-{}".format(VERSION),
            "dataset": {"item_count": record_count},
            "features": features,
            "target": target,
        }

        # Get feature value distribution by target values
        if target_column_name:
            baseline_stats = cls.get_feature_distribution_by_target(
                df=df, target_column_name=target_column_name, baseline_stats=baseline_stats
            )

        # Save output in a file
        if output_path:
            cls.save_stats_output(baseline_stats, output_path)

        return baseline_stats

    @classmethod
    def from_pandas(
        cls,
        df: pd.DataFrame,
        target_column_name: str = None,
        output_path: str = None,
        schema: Dict = None,
        baseline: Dict = None,
    ):

        if df is None or df.empty:
            raise DblueStatsException("Pandas DataFrame can't be empty")

        return cls.get_stats(
            df=df, target_column_name=target_column_name, output_path=output_path, schema=schema, baseline=baseline
        )

    @classmethod
    def from_csv(
        cls, uri, target_column_name: str = None, output_path: str = None, schema: Dict = None, baseline: Dict = None
    ):
        if not os.path.exists(uri):
            raise DblueStatsException("CSV file not found at %s" % uri)

        df = pd.read_csv(uri)

        return cls.get_stats(
            df=df, target_column_name=target_column_name, output_path=output_path, schema=schema, baseline=baseline
        )

    @classmethod
    def from_parquet(
        cls, uri, target_column_name: str = None, output_path: str = None, schema: Dict = None, baseline: Dict = None
    ):
        if not os.path.exists(uri):
            raise DblueStatsException("Parquet file not found at %s" % uri)

        df = pd.read_parquet(uri, engine="fastparquet")

        return cls.get_stats(
            df=df, target_column_name=target_column_name, output_path=output_path, schema=schema, baseline=baseline
        )

    @classmethod
    def save_stats_output(cls, stats: Dict, output_path: str):

        if not output_path.endswith(".json"):
            output_path = "{}.json".format(output_path)

        with open(output_path, "w") as f:
            json.dump(stats, f, indent=4)
