import argparse
import json
import math
import random
import re
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

try:
    from .config import (
        BASELINE_METRICS_JSON_PATH,
        BASELINE_METRICS_MD_PATH,
        FEATURE_SELECTION_REPORT_PATH,
        MODELS_DIR,
        PREDICTION_SAMPLES_PATH,
        PROCESSED_DATA_PATH,
        RANDOM_SEED,
        TASKS,
    )
except ImportError:
    from config import (
        BASELINE_METRICS_JSON_PATH,
        BASELINE_METRICS_MD_PATH,
        FEATURE_SELECTION_REPORT_PATH,
        MODELS_DIR,
        PREDICTION_SAMPLES_PATH,
        PROCESSED_DATA_PATH,
        RANDOM_SEED,
        TASKS,
    )


TOKEN_RE = re.compile(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+")
STOPWORDS = {
    "acaba",
    "ama",
    "artık",
    "az",
    "bazı",
    "belki",
    "ben",
    "bende",
    "beni",
    "benim",
    "bir",
    "biri",
    "biz",
    "bu",
    "buna",
    "bunu",
    "da",
    "de",
    "daha",
    "diye",
    "en",
    "gibi",
    "hem",
    "hep",
    "her",
    "hiç",
    "ile",
    "ise",
    "için",
    "ki",
    "mi",
    "mu",
    "mü",
    "nasıl",
    "ne",
    "neden",
    "o",
    "olan",
    "olarak",
    "oldu",
    "olur",
    "onu",
    "orada",
    "şey",
    "şu",
    "ve",
    "veya",
    "ya",
    "yani",
}


def tr_lower(text: str) -> str:
    return str(text).casefold().replace("\u0307", "")


def tokenize(text: str) -> list[str]:
    lowered = tr_lower(text)
    tokens = TOKEN_RE.findall(lowered)
    return [token for token in tokens if len(token) > 1 and token not in STOPWORDS]


def stratified_split(
    data: pd.DataFrame,
    target_col: str,
    test_size: float = 0.2,
    seed: int = RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = random.Random(seed)
    train_idx = []
    test_idx = []

    for _, group in data.groupby(target_col):
        indices = list(group.index)
        rng.shuffle(indices)
        n_test = max(1, int(round(len(indices) * test_size)))
        if len(indices) - n_test < 1:
            n_test = len(indices) - 1
        test_idx.extend(indices[:n_test])
        train_idx.extend(indices[n_test:])

    return data.loc[train_idx].sample(frac=1, random_state=seed), data.loc[test_idx]


def build_vocabulary(
    texts: list[str],
    min_freq: int = 2,
    max_features: int = 5000,
) -> list[str]:
    counts = Counter()
    for text in texts:
        counts.update(tokenize(text))
    return [
        token
        for token, count in counts.most_common(max_features)
        if count >= min_freq
    ]


def train_naive_bayes(
    texts: list[str],
    labels: list[str],
    min_freq: int = 2,
    max_features: int = 5000,
    alpha: float = 1.0,
) -> dict[str, Any]:
    vocabulary = build_vocabulary(texts, min_freq=min_freq, max_features=max_features)
    token_to_id = {token: idx for idx, token in enumerate(vocabulary)}
    classes = sorted(set(labels))

    class_doc_counts = Counter(labels)
    class_token_counts = {
        label: np.full(len(vocabulary), alpha, dtype=float)
        for label in classes
    }
    class_total_tokens = {
        label: alpha * len(vocabulary)
        for label in classes
    }

    for text, label in zip(texts, labels):
        counts = Counter(token for token in tokenize(text) if token in token_to_id)
        for token, count in counts.items():
            idx = token_to_id[token]
            class_token_counts[label][idx] += count
            class_total_tokens[label] += count

    n_docs = len(labels)
    n_classes = len(classes)
    class_log_prior = {
        label: math.log((class_doc_counts[label] + alpha) / (n_docs + alpha * n_classes))
        for label in classes
    }
    feature_log_prob = {
        label: np.log(class_token_counts[label] / class_total_tokens[label]).tolist()
        for label in classes
    }

    return {
        "classes": classes,
        "vocabulary": vocabulary,
        "class_log_prior": class_log_prior,
        "feature_log_prob": feature_log_prob,
        "alpha": alpha,
        "min_freq": min_freq,
        "max_features": max_features,
    }


def predict_one(text: str, model: dict[str, Any]) -> str:
    token_to_id = {token: idx for idx, token in enumerate(model["vocabulary"])}
    counts = Counter(token for token in tokenize(text) if token in token_to_id)
    scores = {}

    for label in model["classes"]:
        score = float(model["class_log_prior"][label])
        probs = model["feature_log_prob"][label]
        for token, count in counts.items():
            score += count * float(probs[token_to_id[token]])
        scores[label] = score

    return max(scores.items(), key=lambda item: item[1])[0]


def evaluate(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    labels = sorted(set(y_true) | set(y_pred))
    total = len(y_true)
    correct = sum(true == pred for true, pred in zip(y_true, y_pred))
    per_class = {}

    for label in labels:
        tp = sum(true == label and pred == label for true, pred in zip(y_true, y_pred))
        fp = sum(true != label and pred == label for true, pred in zip(y_true, y_pred))
        fn = sum(true == label and pred != label for true, pred in zip(y_true, y_pred))
        support = sum(true == label for true in y_true)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }

    macro_f1 = sum(values["f1"] for values in per_class.values()) / len(labels)
    weighted_f1 = sum(
        values["f1"] * values["support"] for values in per_class.values()
    ) / total

    return {
        "accuracy": correct / total if total else 0.0,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class": per_class,
    }


def majority_baseline(y_train: list[str], y_test: list[str]) -> dict[str, Any]:
    majority = Counter(y_train).most_common(1)[0][0]
    predictions = [majority] * len(y_test)
    metrics = evaluate(y_test, predictions)
    metrics["majority_class"] = majority
    return metrics


def top_tokens_by_class(model: dict[str, Any], top_n: int = 12) -> dict[str, list[str]]:
    vocab = model["vocabulary"]
    matrix = np.array([model["feature_log_prob"][label] for label in model["classes"]])
    mean_scores = matrix.mean(axis=0)
    output = {}
    for row_idx, label in enumerate(model["classes"]):
        indicative_scores = matrix[row_idx] - mean_scores
        top_idx = np.argsort(indicative_scores)[-top_n:][::-1]
        output[label] = [vocab[idx] for idx in top_idx if idx < len(vocab)]
    return output


def prepare_task_data(df: pd.DataFrame, target_col: str, min_count: int, exclude: set[str]) -> pd.DataFrame:
    data = df[["text_clean", target_col]].dropna().copy()
    data[target_col] = data[target_col].astype(str)
    data = data[~data[target_col].isin(exclude)]
    counts = data[target_col].value_counts()
    allowed = set(counts[counts >= min_count].index)
    return data[data[target_col].isin(allowed)].copy()


def train_task(df: pd.DataFrame, target_col: str, settings: dict[str, Any]) -> dict[str, Any] | None:
    data = prepare_task_data(
        df,
        target_col=target_col,
        min_count=settings["min_count"],
        exclude=settings.get("exclude", set()),
    )

    if data[target_col].nunique() < 2 or len(data) < 50:
        return None

    train_df, test_df = stratified_split(data, target_col)
    x_train = train_df["text_clean"].tolist()
    y_train = train_df[target_col].tolist()
    x_test = test_df["text_clean"].tolist()
    y_test = test_df[target_col].tolist()

    model = train_naive_bayes(x_train, y_train)
    predictions = [predict_one(text, model) for text in x_test]

    metrics = evaluate(y_test, predictions)
    majority_metrics = majority_baseline(y_train, y_test)
    model["task"] = target_col
    model["task_label"] = settings["label"]

    model_path = MODELS_DIR / f"{target_col}_naive_bayes.json"
    model_path.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")

    sample_rows = test_df.head(25).copy()
    sample_rows["prediction"] = predictions[: len(sample_rows)]
    sample_rows["task"] = target_col

    return {
        "task": target_col,
        "task_label": settings["label"],
        "rows": int(len(data)),
        "classes": sorted(data[target_col].unique().tolist()),
        "train_size": int(len(train_df)),
        "test_size": int(len(test_df)),
        "vocabulary_size": int(len(model["vocabulary"])),
        "model_path": str(model_path),
        "metrics": metrics,
        "majority_baseline": majority_metrics,
        "top_tokens": top_tokens_by_class(model),
        "samples": sample_rows,
    }


def write_markdown_report(results: list[dict[str, Any]]) -> None:
    lines = [
        "# Baseline Model Sonuclari",
        "",
        "Model: Bag-of-words + Multinomial Naive Bayes",
        "",
        "| Gorev | Satir | Sinif | Accuracy | Macro F1 | Weighted F1 | Majority Acc. |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        metrics = result["metrics"]
        majority = result["majority_baseline"]
        lines.append(
            "| {task} | {rows} | {classes} | {acc:.3f} | {macro:.3f} | {weighted:.3f} | {maj:.3f} |".format(
                task=result["task_label"],
                rows=result["rows"],
                classes=len(result["classes"]),
                acc=metrics["accuracy"],
                macro=metrics["macro_f1"],
                weighted=metrics["weighted_f1"],
                maj=majority["accuracy"],
            )
        )

    lines.extend(["", "## Siniflara Ait Belirgin Kelimeler", ""])
    for result in results:
        lines.append(f"### {result['task_label']}")
        for label, tokens in result["top_tokens"].items():
            lines.append(f"- {label}: {', '.join(tokens[:10])}")
        lines.append("")

    BASELINE_METRICS_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_feature_selection_report(results: list[dict[str, Any]]) -> None:
    lines = [
        "# Özellik Seçimi Raporu",
        "",
        "Bu rapor, baseline modeller eğitilirken kullanılan metin özelliklerinin",
        "nasıl seçildiğini özetler.",
        "",
        "## Genel Strateji",
        "",
        "- Metinler Türkçe karakter destekli regex ile tokenlara ayrıldı.",
        "- Çok genel Türkçe stopword kelimeleri çıkarıldı.",
        "- Frekansı 2'den düşük tokenlar sözlüğe alınmadı.",
        "- Her görev için en fazla 5000 token kullanıldı.",
        "- Örneği çok az olan sınıflar eğitimden çıkarıldı.",
        "- Her sınıf için log olasılık farkına göre ayırt edici tokenlar raporlandı.",
        "",
        "## Görev Bazlı Özellik Özeti",
        "",
        "| Görev | Eğitim Satırı | Sınıf Sayısı | Sözlük Boyutu |",
        "|---|---:|---:|---:|",
    ]

    for result in results:
        lines.append(
            f"| {result['task_label']} | {result['train_size']} | "
            f"{len(result['classes'])} | {result['vocabulary_size']} |"
        )

    lines.extend(["", "## Sınıflara Göre Ayırt Edici Tokenlar", ""])
    for result in results:
        lines.append(f"### {result['task_label']}")
        for label, tokens in result["top_tokens"].items():
            lines.append(f"- `{label}`: {', '.join(tokens[:12])}")
        lines.append("")

    FEATURE_SELECTION_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main(selected_tasks: list[str] | None = None) -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    BASELINE_METRICS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Clean data not found: {PROCESSED_DATA_PATH}. Run python -m src.data_prep first."
        )

    df = pd.read_csv(PROCESSED_DATA_PATH, encoding="utf-8")
    tasks = selected_tasks or list(TASKS)
    results = []
    sample_frames = []

    for task in tasks:
        if task not in TASKS:
            raise ValueError(f"Unknown task: {task}. Available: {', '.join(TASKS)}")
        result = train_task(df, task, TASKS[task])
        if result is None:
            print(f"Skipped {task}: not enough usable labels.")
            continue
        sample_frames.append(result.pop("samples"))
        results.append(result)
        print(
            f"{task}: accuracy={result['metrics']['accuracy']:.3f}, "
            f"macro_f1={result['metrics']['macro_f1']:.3f}"
        )

    serializable_results = json.loads(json.dumps(results, ensure_ascii=False))
    BASELINE_METRICS_JSON_PATH.write_text(
        json.dumps(serializable_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown_report(results)
    write_feature_selection_report(results)

    if sample_frames:
        pd.concat(sample_frames).to_csv(PREDICTION_SAMPLES_PATH, index=False, encoding="utf-8")

    print(f"Metrics saved: {BASELINE_METRICS_JSON_PATH}")
    print(f"Markdown report saved: {BASELINE_METRICS_MD_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        help="Task column to train. Can be passed multiple times.",
    )
    args = parser.parse_args()
    main(args.tasks)
