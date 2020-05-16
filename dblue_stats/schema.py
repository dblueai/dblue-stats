import json
import os
from typing import Dict

import pandas as pd
from slugify import slugify

from dblue_stats.constants import Constants
from dblue_stats.exceptions import DblueStatsException


class JSONSchema:

    @classmethod
    def from_pandas(cls, df: pd.DataFrame, target_column_name: str = None, output_path: str = None):
        if df is None or df.empty:
            raise DblueStatsException("Pandas DataFrame can't be empty")

        return cls.get_schema(df=df, target_column_name=target_column_name, output_path=output_path)

    @classmethod
    def from_csv(cls, uri: str, target_column_name: str = None, output_path: str = None):
        if not os.path.exists(uri):
            raise DblueStatsException("CSV file not found at %s", uri)

        df = pd.read_csv(uri)

        return cls.get_schema(df=df, target_column_name=target_column_name, output_path=output_path)

    @classmethod
    def from_parquet(cls, uri: str, target_column_name: str = None, output_path: str = None):
        if not os.path.exists(uri):
            raise DblueStatsException("Parquet file not found at %s", uri)

        df = pd.read_parquet(uri, engine="fastparquet")

        return cls.get_schema(df=df, target_column_name=target_column_name, output_path=output_path)

    @classmethod
    def get_schema(cls, df: pd.DataFrame, target_column_name: str = None, output_path: str = None):
        properties = {}

        for column_name in df.columns:
            column = df[column_name]
            field = cls.get_field_property(column=column)

            field["meta"]["is_target"] = column_name == target_column_name

            properties[slugify(column_name, separator="_")] = field

        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "description": "Dblue MLWatch - training dataset schema",
            "type": "object",
            "properties": properties,
            "additionalProperties": False
        }

        # Save output in a file
        if output_path:
            cls.save_output(schema=schema, output_path=output_path)

        return schema

    @classmethod
    def infer_data_type(cls, column: pd.Series):

        data_type = cls.get_standard_data_type(column.dtype.name)

        if not data_type:
            raise DblueStatsException("Data type not found: %s" % column.dtype.name)

        return data_type

    @staticmethod
    def get_standard_data_type(data_type):
        types = {
            "int64": Constants.DATA_TYPE_INTEGER,
            "float64": Constants.DATA_TYPE_NUMBER,
            "object": Constants.DATA_TYPE_STRING,
            "bool": Constants.DATA_TYPE_BOOLEAN,
        }

        return types.get(data_type)

    @classmethod
    def get_field_property(cls, column: pd.Series):
        data_type = cls.infer_data_type(column=column)
        feature_type = cls.get_feature_type(data_type=data_type)

        nullable = int(column.isnull().sum()) > 0

        # Detect boolean
        distinct_values = column.dropna().unique()
        is_bool = len(set(distinct_values) - {0, 1}) == 0

        if is_bool or data_type == "boolean":
            feature_type = Constants.FEATURE_TYPE_CATEGORICAL

        item = {
            "type": data_type,
            "nullable": nullable,
            "meta": {
                "display_name": column.name,
                "feature_type": feature_type,
            }
        }

        if feature_type == Constants.FEATURE_TYPE_CATEGORICAL:
            item["allowed"] = distinct_values.tolist()

        return item

    @staticmethod
    def get_feature_type(data_type):

        types = {
            "integer": Constants.FEATURE_TYPE_NUMERICAL,
            "number": Constants.FEATURE_TYPE_NUMERICAL,
            "string": Constants.FEATURE_TYPE_CATEGORICAL,
            "boolean": Constants.FEATURE_TYPE_CATEGORICAL,
        }

        return types.get(data_type)

    @classmethod
    def save_output(cls, schema: Dict, output_path: str):

        if not output_path.endswith(".json"):
            output_path = "{}.json".format(output_path)

        with open(output_path, "w") as f:
            json.dump(schema, f, indent=4)
