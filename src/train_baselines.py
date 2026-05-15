import argparse
import ast
import json
import os
import re
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

try:
    from .config import (
        BASELINE_METRICS_JSON_PATH,
        BASELINE_METRICS_MD_PATH,
        FEATURE_SELECTION_REPORT_PATH,
        MODELS_DIR,
        PREDICTION_SAMPLES_PATH,
        PROCESSED_DATA_PATH,
        RAW_DATA_PATH,
        RANDOM_SEED,
        REPORTS_DIR,
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
        RAW_DATA_PATH,
        RANDOM_SEED,
        REPORTS_DIR,
        TASKS,
    )


TOKEN_RE = re.compile(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+")
STOPWORDS = {
    "acaba", "ama", "artık", "az", "bazı", "belki", "ben", "bende", "beni",
    "benim", "bir", "biri", "biz", "bu", "buna", "bunu", "da", "de", "daha",
    "diye", "en", "gibi", "hem", "hep", "her", "hiç", "ile", "ise", "için",
    "ki", "mi", "mu", "mü", "nasıl", "ne", "neden", "o", "olan", "olarak",
    "oldu", "olur", "onu", "orada", "şey", "şu", "ve", "veya", "ya", "yani",
}


def tr_lower(text: str) -> str:
    return str(text).casefold().replace("\u0307", "")


def tokenize(text: str) -> list[str]:
    lowered = tr_lower(text)
    tokens = TOKEN_RE.findall(lowered)
    return [token for token in tokens if len(token) > 1 and token not in STOPWORDS]


def get_top_features_lr(model: Pipeline, top_n: int = 12) -> dict[str, list[str]]:
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    
    feature_names = []
    for name, transformer, cols in preprocessor.transformers_:
        if name == "text":
            feature_names.extend(transformer.get_feature_names_out())
        elif name == "cat":
            feature_names.extend(transformer.get_feature_names_out(cols))
        elif name == "num":
            feature_names.extend(cols)
    
    feature_names = np.array(feature_names)
    classes = classifier.classes_
    coefs = classifier.coef_
    
    top_features = {}
    if len(classes) == 2:
        top_idx_pos = np.argsort(coefs[0])[-top_n:][::-1]
        top_idx_neg = np.argsort(coefs[0])[:top_n]
        top_features[classes[1]] = feature_names[top_idx_pos].tolist()
        top_features[classes[0]] = feature_names[top_idx_neg].tolist()
    else:
        for i, label in enumerate(classes):
            top_idx = np.argsort(coefs[i])[-top_n:][::-1]
            top_features[label] = feature_names[top_idx].tolist()
            
    return top_features


def prepare_task_data(df: pd.DataFrame, target_col: str, min_count: int, exclude: set[str]) -> pd.DataFrame:
    data = df.copy()
    data[target_col] = data[target_col].astype(str)
    data = data[~data[target_col].isin(exclude)]
    counts = data[target_col].value_counts()
    allowed = set(counts[counts >= min_count].index)
    return data[data[target_col].isin(allowed)].copy()


def evaluate(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    labels = sorted(set(y_true) | set(y_pred))
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    
    per_class = {}
    for i, label in enumerate(labels):
        per_class[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]) if support is not None else 0,
        }

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "per_class": per_class,
    }


def majority_baseline(y_train: pd.Series, y_test: pd.Series) -> dict[str, Any]:
    majority = y_train.value_counts().index[0]
    predictions = [majority] * len(y_test)
    metrics = evaluate(y_test.tolist(), predictions)
    metrics["majority_class"] = majority
    return metrics


def train_task(df: pd.DataFrame, target_col: str, settings: dict[str, Any]) -> dict[str, Any] | None:
    data = prepare_task_data(
        df,
        target_col=target_col,
        min_count=settings["min_count"],
        exclude=settings.get("exclude", set()),
    )

    if data[target_col].nunique() < 2 or len(data) < 50:
        return None

    data["speaker"] = data["speaker"].fillna("Unknown")
    bool_cols = ["has_symptom", "has_test", "has_drug", "has_procedure"]
    for col in bool_cols:
        data[col] = data[col].fillna(False).astype(int)
    data["entity_count"] = data["entity_count"].fillna(0).astype(float)
    data["text_clean"] = data["text_clean"].fillna("")

    X = data[["text_clean", "speaker"] + bool_cols + ["entity_count"]]
    y = data[target_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_SEED
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(tokenizer=tokenize, token_pattern=None, min_df=2, max_features=5000), "text_clean"),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["speaker"]),
            ("num", "passthrough", bool_cols + ["entity_count"])
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_SEED))
    ])

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = evaluate(y_test.tolist(), predictions.tolist())
    majority_metrics = majority_baseline(y_train, y_test)
    
    model_path = MODELS_DIR / f"{target_col}_lr_pipeline.joblib"
    joblib.dump(model, model_path)

    top_tokens = get_top_features_lr(model)

    sample_rows = X_test.head(25).copy()
    sample_rows["prediction"] = predictions[: len(sample_rows)]
    sample_rows["actual"] = y_test.head(25).tolist()
    sample_rows["task"] = target_col

    return {
        "task": target_col,
        "task_label": settings["label"],
        "rows": int(len(data)),
        "classes": sorted(y.unique().tolist()),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "vocabulary_size": len(model.named_steps["preprocessor"].transformers_[0][1].vocabulary_),
        "model_path": str(model_path),
        "metrics": metrics,
        "majority_baseline": majority_metrics,
        "top_tokens": top_tokens,
        "samples": sample_rows,
    }


def train_bert(task="intent_norm", epochs=3, batch_size=16, model_name="dbmdz/bert-base-turkish-cased"):
    print(f"\n--- Training BERT for {task} ---")
    import evaluate as hf_evaluate
    from datasets import Dataset
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )

    output_dir = MODELS_DIR / "bert_model"
    df = pd.read_csv(PROCESSED_DATA_PATH, encoding="utf-8")
    
    df = df[["text_clean", task]].dropna().copy()
    df[task] = df[task].astype(str)
    df = df[df[task] != "unknown"]
    
    unique_labels = sorted(df[task].unique().tolist())
    label2id = {label: i for i, label in enumerate(unique_labels)}
    id2label = {i: label for label, i in label2id.items()}
    
    df["label"] = df[task].map(label2id)
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    dataset = Dataset.from_pandas(df[["text_clean", "label"]])
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    
    def tokenize_function(examples):
        return tokenizer(examples["text_clean"], padding="max_length", truncation=True, max_length=128)
    
    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(unique_labels),
        id2label=id2label,
        label2id=label2id,
    )
    
    metric = hf_evaluate.load("f1")
    acc_metric = hf_evaluate.load("accuracy")
    recall_metric = hf_evaluate.load("recall")
    
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        f1 = metric.compute(predictions=predictions, references=labels, average="weighted")["f1"]
        acc = acc_metric.compute(predictions=predictions, references=labels)["accuracy"]
        recall = recall_metric.compute(predictions=predictions, references=labels, average="weighted")["recall"]
        return {"f1": f1, "accuracy": acc, "recall": recall}
    
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
    )
    
    trainer.train()
    
    eval_results = trainer.evaluate()
    trainer.save_model(str(output_dir / "best"))
    
    metrics = {
        "rows": len(df),
        "classes": len(unique_labels),
        "accuracy": eval_results.get("eval_accuracy", 0.0),
        "recall": eval_results.get("eval_recall", 0.0),
        "f1": eval_results.get("eval_f1", 0.0),
        "loss": eval_results.get("eval_loss", 0.0)
    }
    
    dl_metrics_path = REPORTS_DIR / "dl_metrics.json"
    dl_metrics = {}
    if dl_metrics_path.exists():
        with open(dl_metrics_path, "r", encoding="utf-8") as f:
            dl_metrics = json.load(f)
    
    dl_metrics["BERT"] = metrics
    with open(dl_metrics_path, "w", encoding="utf-8") as f:
        json.dump(dl_metrics, f, indent=2, ensure_ascii=False)
        
    print(f"BERT training complete. Best model saved to {output_dir / 'best'}")


def parse_entities(row):
    text = str(row["text"]).strip()
    entities_str = row["medical_entities"]
    if not isinstance(entities_str, str) or not entities_str.strip():
        return None
    try:
        entities = json.loads(entities_str)
    except json.JSONDecodeError:
        return None
    if not entities:
        return None
    if isinstance(entities, dict):
        entities = [entities]
    elif not isinstance(entities, list):
        return None
    valid_entities = [ent for ent in entities if isinstance(ent, dict) and "text" in ent and "type" in ent]
    if not valid_entities:
        return None
    return {"text": text, "entities": valid_entities}


def align_labels_with_tokens(labels, word_ids):
    new_labels = []
    current_word = None
    for word_id in word_ids:
        if word_id != current_word:
            current_word = word_id
            label = -100 if word_id is None else labels[word_id]
            new_labels.append(label)
        elif word_id is None:
            new_labels.append(-100)
        else:
            label = labels[word_id]
            if label % 2 == 1:
                label += 1
            new_labels.append(label)
    return new_labels


def train_ner(epochs=3, batch_size=8, model_name="dbmdz/bert-base-turkish-cased"):
    print("\n--- Training NER ---")
    import evaluate as hf_evaluate
    from datasets import Dataset
    from transformers import (
        AutoModelForTokenClassification,
        AutoTokenizer,
        DataCollatorForTokenClassification,
        Trainer,
        TrainingArguments,
    )

    output_dir = MODELS_DIR / "ner_model"
    df = pd.read_csv(RAW_DATA_PATH, sep=";", encoding="utf-8")
    parsed_data = df.apply(parse_entities, axis=1).dropna().tolist()
    
    word_re = re.compile(r"\w+|[^\w\s]")
    dataset_records = []
    unique_entity_types = set()
    
    for item in parsed_data:
        text = item["text"]
        words = word_re.findall(text)
        tags = ["O"] * len(words)
        for ent in item["entities"]:
            e_text = ent["text"]
            e_type = ent["type"]
            unique_entity_types.add(e_type)
            e_words = word_re.findall(e_text)
            if not e_words:
                continue
            for i in range(len(words) - len(e_words) + 1):
                if words[i:i+len(e_words)] == e_words:
                    tags[i] = f"B-{e_type}"
                    for j in range(1, len(e_words)):
                        tags[i+j] = f"I-{e_type}"
        dataset_records.append({"words": words, "ner_tags": tags})

    labels_list = ["O"]
    for e_type in sorted(list(unique_entity_types)):
        labels_list.append(f"B-{e_type}")
        labels_list.append(f"I-{e_type}")
        
    label2id = {label: i for i, label in enumerate(labels_list)}
    id2label = {i: label for label, i in label2id.items()}
    
    for record in dataset_records:
        record["ner_ids"] = [label2id[t] for t in record["ner_tags"]]
        
    hf_dataset = Dataset.from_list(dataset_records)
    hf_dataset = hf_dataset.train_test_split(test_size=0.2, seed=42)
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(examples["words"], truncation=True, is_split_into_words=True, max_length=128)
        labels = []
        for i, label in enumerate(examples["ner_ids"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            labels.append(align_labels_with_tokens(label, word_ids))
        tokenized_inputs["labels"] = labels
        return tokenized_inputs
        
    tokenized_datasets = hf_dataset.map(tokenize_and_align_labels, batched=True)
    
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(labels_list),
        id2label=id2label,
        label2id=label2id
    )
    
    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)
    metric = hf_evaluate.load("seqeval")
    
    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)
        true_predictions = [
            [labels_list[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [labels_list[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        results = metric.compute(predictions=true_predictions, references=true_labels)
        return {
            "f1": results["overall_f1"],
            "recall": results["overall_recall"],
            "accuracy": results["overall_accuracy"],
        }
        
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    
    trainer.train()
    
    eval_results = trainer.evaluate()
    trainer.save_model(str(output_dir / "best"))
    
    metrics = {
        "rows": len(parsed_data),
        "classes": len(labels_list),
        "accuracy": eval_results.get("eval_accuracy", 0.0),
        "recall": eval_results.get("eval_recall", 0.0),
        "f1": eval_results.get("eval_f1", 0.0),
        "loss": eval_results.get("eval_loss", 0.0)
    }
    
    dl_metrics_path = REPORTS_DIR / "dl_metrics.json"
    dl_metrics = {}
    if dl_metrics_path.exists():
        with open(dl_metrics_path, "r", encoding="utf-8") as f:
            dl_metrics = json.load(f)
    
    dl_metrics["NER"] = metrics
    with open(dl_metrics_path, "w", encoding="utf-8") as f:
        json.dump(dl_metrics, f, indent=2, ensure_ascii=False)
        
    print(f"NER training complete. Best model saved to {output_dir / 'best'}")


def main(selected_tasks: list[str] | None = None, run_bert: bool = False, run_ner: bool = False) -> None:
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
            f"f1={result['metrics']['f1']:.3f}"
        )

    serializable_results = json.loads(json.dumps(results, ensure_ascii=False))
    BASELINE_METRICS_JSON_PATH.write_text(
        json.dumps(serializable_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if sample_frames:
        pd.concat(sample_frames).to_csv(PREDICTION_SAMPLES_PATH, index=False, encoding="utf-8")

    print(f"Metrics saved: {BASELINE_METRICS_JSON_PATH}")
    
    if run_bert:
        train_bert(epochs=1) # Defaulting to 1 for quick execution, user can change
    if run_ner:
        train_ner(epochs=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        help="Task column to train. Can be passed multiple times.",
    )
    parser.add_argument("--bert", action="store_true", help="Run BERTurk training")
    parser.add_argument("--ner", action="store_true", help="Run Medical NER training")
    args = parser.parse_args()
    main(selected_tasks=args.tasks, run_bert=args.bert, run_ner=args.ner)