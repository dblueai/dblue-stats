import json
import math
from collections import defaultdict

from dateutil import parser
from sklearn.metrics import max_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_gamma_deviance
from sklearn.metrics import mean_poisson_deviance
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_log_error
from sklearn.metrics import mean_tweedie_deviance
from sklearn.metrics import median_absolute_error
from sklearn.metrics import r2_score

path = '/Users/rajesh/work/projects/dblue/monitoring/dblue-monitoring-frontend/src/assets/data/regression/prediction-logs.json'


def get_data_by_date(data):
    data_by_date = defaultdict(list)

    for x in data:
        _date = parser.parse(x["eventTime"]).strftime("%Y-%m-%d")
        data_by_date[_date].append(x)

    return data_by_date


def main():
    with open(path) as f:
        data = json.load(f)

    metrics = {}
    predictions = [x["prediction"] for x in data]
    targets = [x["targetValue"] for x in data]

    metrics["prediction_count"] = len(data)
    metrics["max_error"] = max_error(y_true=targets, y_pred=predictions)
    metrics["mean_absolute_error"] = mean_absolute_error(y_true=targets, y_pred=predictions)
    metrics["mean_squared_error"] = mean_squared_error(y_true=targets, y_pred=predictions)
    metrics["root_mean_squared_error"] = math.sqrt(metrics["mean_squared_error"])
    metrics["mean_squared_log_error"] = mean_squared_log_error(y_true=targets, y_pred=predictions)
    metrics["median_absolute_error"] = median_absolute_error(y_true=targets, y_pred=predictions)
    metrics["r2_score"] = r2_score(y_true=targets, y_pred=predictions)
    metrics["mean_poisson_deviance"] = mean_poisson_deviance(y_true=targets, y_pred=predictions)
    metrics["mean_gamma_deviance"] = mean_gamma_deviance(y_true=targets, y_pred=predictions)
    metrics["mean_tweedie_deviance"] = mean_tweedie_deviance(y_true=targets, y_pred=predictions)

    data_by_date = get_data_by_date(data)

    metrics_by_date = []
    for date, logs in sorted(data_by_date.items(), key=lambda x: x[0]):
        _metrics = {}
        _predictions = [x["prediction"] for x in logs]
        _targets = [x["targetValue"] for x in logs]

        _metrics["date"] = date
        _metrics["prediction_count"] = len(logs)
        _metrics["mean_squared_error"] = mean_squared_error(y_true=_targets, y_pred=_predictions)
        _metrics["root_mean_squared_error"] = math.sqrt(_metrics["mean_squared_error"])
        _metrics["r2_score"] = r2_score(y_true=_targets, y_pred=_predictions)

        metrics_by_date.append(_metrics)

    output = {
        "overall": metrics,
        "datewise": metrics_by_date,
    }
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    main()
