import json
from collections import defaultdict

from dateutil import parser

path = '/Users/rajesh/work/projects/dblue/monitoring/dblue-monitoring-frontend/src/assets/data/classification/prediction-logs.json'

from sklearn.metrics import log_loss
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.metrics import brier_score_loss
from sklearn.metrics import matthews_corrcoef


def get_accuracy(targets, predictions):
    return accuracy_score(targets, predictions)


def get_log_loss(targets, probabilities):
    return log_loss(targets, probabilities)


def get_precision(targets, predictions):
    return precision_score(targets, predictions, pos_label="Retained")


def get_recall(targets, predictions):
    return recall_score(targets, predictions, pos_label="Retained")


def get_f1_score(targets, predictions):
    return f1_score(targets, predictions, pos_label="Retained")


def get_data_by_date(data):
    data_by_date = defaultdict(list)

    for x in data:
        _date = parser.parse(x["eventTime"]).strftime("%Y-%m-%d")
        data_by_date[_date].append(x)

    return data_by_date


def get_roc_curve(targets, scores):
    fpr, tpr, thresholds = roc_curve(targets, scores, pos_label="Retained")

    return fpr, tpr, thresholds


def get_auc(targets, scores):
    return roc_auc_score(targets, scores)


def get_brier_score_loss(targets, probabilities):
    return brier_score_loss(targets, probabilities, pos_label="Retained")


def get_matthews_corr_coef(targets, predictions):
    return matthews_corrcoef(targets, predictions)


def main():
    with open(path) as f:
        data = json.load(f)

    metrics = {}
    predictions = [x["prediction"] for x in data]
    targets = [x["targetValue"] for x in data]
    probabilities = [x["probability"] for x in data]

    metrics["prediction_count"] = len(data)
    metrics["accuracy"] = get_accuracy(targets=targets, predictions=predictions) * 100
    metrics["log_loss"] = get_log_loss(targets=targets, probabilities=probabilities)
    metrics["precision"] = get_precision(targets=targets, predictions=predictions)
    metrics["recall"] = get_recall(targets=targets, predictions=predictions)
    metrics["f1_score"] = get_f1_score(targets=targets, predictions=predictions)
    metrics["auc"] = get_auc(targets=targets, scores=probabilities)
    metrics["brier_score_loss"] = get_brier_score_loss(targets=targets, probabilities=probabilities)
    metrics["matthews_corr_coef"] = get_matthews_corr_coef(targets=targets, predictions=predictions)

    fpr, tpr, _ = get_roc_curve(targets=targets, scores=probabilities)
    metrics["fpr"] = fpr.tolist()
    metrics["tpr"] = tpr.tolist()

    data_by_date = get_data_by_date(data)
    metrics_by_date = []
    for date, logs in sorted(data_by_date.items(), key=lambda x: x[0]):
        _metrics = {}
        _predictions = [x["prediction"] for x in logs]
        _targets = [x["targetValue"] for x in logs]
        _probabilities = [x["probability"] for x in logs]

        _metrics["date"] = date
        _metrics["accuracy"] = get_accuracy(targets=_targets, predictions=_predictions) * 100
        _metrics["log_loss"] = get_log_loss(targets=_targets, probabilities=_probabilities)
        _metrics["precision"] = get_precision(targets=_targets, predictions=_predictions)
        _metrics["recall"] = get_recall(targets=_targets, predictions=_predictions)
        _metrics["f1_score"] = get_f1_score(targets=_targets, predictions=_predictions)
        _metrics["prediction_count"] = len(logs)
        _metrics["avg_probability"] = sum(_probabilities) / _metrics["prediction_count"]
        _metrics["wrong_prediction"] = sum([1 if l["prediction"] != l["targetValue"] else 0 for l in logs])

        metrics_by_date.append(_metrics)

    output = {
        "overall": metrics,
        "datewise": metrics_by_date,
    }
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    main()
