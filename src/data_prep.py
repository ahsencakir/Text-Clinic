import json
import re
from collections import Counter
from typing import Any

import pandas as pd

try:
    from .config import (
        DATASET_SUMMARY_PATH,
        LABEL_DISTRIBUTION_PATH,
        PROCESSED_DATA_PATH,
        RAW_DATA_PATH,
        REPORTS_DIR,
        TASKS,
    )
except ImportError:
    from config import (
        DATASET_SUMMARY_PATH,
        LABEL_DISTRIBUTION_PATH,
        PROCESSED_DATA_PATH,
        RAW_DATA_PATH,
        REPORTS_DIR,
        TASKS,
    )


SPACE_RE = re.compile(r"\s+")


def clean_cell(value: Any) -> str:
    if pd.isna(value):
        return ""
    return SPACE_RE.sub(" ", str(value).strip())


def normalize_label(value: Any) -> str:
    text = clean_cell(value)
    if not text:
        return "unknown"
    text = text.casefold().replace("\u0307", "")
    text = SPACE_RE.sub(" ", text).strip()
    if text in {"-", "none", "nan", "null", "yok"}:
        return "unknown"
    return text


def normalize_diagnosis_stage(value: Any) -> str:
    text = normalize_label(value)
    mapping = {
        "teşhis": "tanı",
        "tani": "tanı",
        "tanı süreci": "tanı",
        "ayırıcı tanı": "ayırıcı_tanı",
        "ayirici tani": "ayırıcı_tanı",
        "semptom incelemesi": "değerlendirme",
        "kritik": "kritik",
    }
    return mapping.get(text, text)


def normalize_emotion(value: Any) -> str:
    text = normalize_label(value)
    mapping = {
        "tarafsız": "nötr",
        "tarafsiz": "nötr",
        "endişeli": "endişe",
        "endiseli": "endişe",
        "panik": "panik",
        "ciddi": "ciddi",
        "analitik": "analitik",
    }
    return mapping.get(text, text)


def normalize_sarcasm(value: Any) -> str:
    text = normalize_label(value)
    if text in {"1", "evet", "alaycı", "alayci", "sarcastic"}:
        return "sarcastic"
    if text in {"0", "hayır", "hayir", "no", "not_sarcastic"}:
        return "not_sarcastic"
    return "unknown"


def parse_entities(value: Any) -> list[dict[str, Any]]:
    text = clean_cell(value)
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def entity_type_summary(entities: list[dict[str, Any]]) -> str:
    counts = Counter(clean_cell(entity.get("type")) for entity in entities)
    counts.pop("", None)
    return "|".join(f"{name}:{count}" for name, count in sorted(counts.items()))


def prepare_dataset() -> pd.DataFrame:
    df = pd.read_csv(RAW_DATA_PATH, sep=";", encoding="utf-8")
    df.columns = [clean_cell(col) for col in df.columns]

    df["text"] = df["text"].map(clean_cell)
    df = df[df["text"] != ""].copy()
    df["text_clean"] = df["text"].map(lambda value: normalize_label(value))

    df["intent_norm"] = df["Intent"].map(normalize_label)
    df["emotion_norm"] = df["Emotion"].map(normalize_emotion)
    df["organ_norm"] = df["Organ"].map(normalize_label)
    df["diagnosis_stage_norm"] = df["diagnosis_stage"].map(normalize_diagnosis_stage)
    df["sarcasm_label"] = df["Sarcasm"].map(normalize_sarcasm)

    for col in ["Symptom", "Test", "Drug", "Procedure"]:
        clean_col = f"has_{col.lower()}"
        df[clean_col] = df[col].map(lambda value: clean_cell(value) != "")

    entities = df["medical_entities"].map(parse_entities)
    df["entity_count"] = entities.map(len)
    df["entity_types"] = entities.map(entity_type_summary)

    return df


def build_distribution_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in TASKS:
        counts = df[col].value_counts(dropna=False)
        for label, count in counts.items():
            rows.append({"task": col, "label": label, "count": int(count)})
    return pd.DataFrame(rows)


def write_dataset_summary(df: pd.DataFrame, distribution: pd.DataFrame) -> None:
    lines = [
        "# Veri Seti Ozeti",
        "",
        f"- Satir sayisi: {len(df)}",
        f"- Kolon sayisi: {len(df.columns)}",
        f"- Ortalama metin uzunlugu: {df['text'].str.len().mean():.2f} karakter",
        f"- Medikal varlik iceren satir sayisi: {int((df['entity_count'] > 0).sum())}",
        "",
        "## Temel Kolonlar",
        "",
        ", ".join(df.columns),
        "",
        "## Hedef Etiket Dagilimlari",
        "",
    ]

    for task, settings in TASKS.items():
        lines.append(f"### {settings['label']} ({task})")
        task_dist = distribution[distribution["task"] == task].head(15)
        for row in task_dist.itertuples(index=False):
            lines.append(f"- {row.label}: {row.count}")
        lines.append("")

    DATASET_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = prepare_dataset()
    distribution = build_distribution_report(df)

    df.to_csv(PROCESSED_DATA_PATH, index=False, encoding="utf-8")
    distribution.to_csv(LABEL_DISTRIBUTION_PATH, index=False, encoding="utf-8")
    write_dataset_summary(df, distribution)

    print(f"Clean dataset saved: {PROCESSED_DATA_PATH}")
    print(f"Dataset summary saved: {DATASET_SUMMARY_PATH}")
    print(f"Label distribution saved: {LABEL_DISTRIBUTION_PATH}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()
