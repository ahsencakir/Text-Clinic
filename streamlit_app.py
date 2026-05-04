import json
import math
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (  # noqa: E402
    BASELINE_METRICS_JSON_PATH,
    DATASET_SUMMARY_PATH,
    MODELS_DIR,
    PROCESSED_DATA_PATH,
    RAW_DATA_PATH,
    TASKS,
)
from src.train_baselines import tokenize  # noqa: E402


TASK_NAMES = {
    "intent_norm": "Konuşma amacı",
    "emotion_norm": "Duygu",
    "sarcasm_label": "Sarkazm",
    "diagnosis_stage_norm": "Tanı aşaması",
    "organ_norm": "Organ / sistem",
}

EXAMPLES = {
    "Medikal bulgu": "Hastanın MR sonucunda beyinde lezyon görüldü.",
    "Tedavi kararı": "Hemen antibiyotik başlayın ve kan kültürü alın.",
    "Soru": "Bu belirtiler ne zamandır devam ediyor?",
    "House tarzı": "Harika, bir gizemli hastalık daha; tam da eksikti.",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def load_model(task: str) -> dict:
    path = MODELS_DIR / f"{task}_naive_bayes.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return read_json(path)


@st.cache_data
def load_metrics() -> dict:
    results = read_json(BASELINE_METRICS_JSON_PATH)
    return {item["task"]: item for item in results} if isinstance(results, list) else {}


@st.cache_data
def load_dataset_shape() -> tuple[int, int]:
    path = PROCESSED_DATA_PATH if PROCESSED_DATA_PATH.exists() else RAW_DATA_PATH
    sep = "," if path == PROCESSED_DATA_PATH else ";"
    df = pd.read_csv(path, sep=sep, encoding="utf-8")
    return df.shape


def score_text(text: str, model: dict) -> tuple[str, pd.DataFrame, list[str]]:
    token_to_id = {token: idx for idx, token in enumerate(model["vocabulary"])}
    tokens = tokenize(text)
    counts = Counter(token for token in tokens if token in token_to_id)

    log_scores = {}
    for label in model["classes"]:
        score = float(model["class_log_prior"][label])
        probs = model["feature_log_prob"][label]
        for token, count in counts.items():
            score += count * float(probs[token_to_id[token]])
        log_scores[label] = score

    prediction = max(log_scores.items(), key=lambda item: item[1])[0]
    max_score = max(log_scores.values())
    exp_scores = {label: math.exp(score - max_score) for label, score in log_scores.items()}
    total = sum(exp_scores.values()) or 1.0

    rows = [
        {
            "Sınıf": label,
            "Olasılık": value / total,
            "Log skor": log_scores[label],
        }
        for label, value in exp_scores.items()
    ]
    scores = pd.DataFrame(rows).sort_values("Olasılık", ascending=False).reset_index(drop=True)
    matched_tokens = [token for token in tokens if token in token_to_id]
    return prediction, scores, matched_tokens


def metric_value(metrics: dict, key: str) -> str:
    value = metrics.get(key)
    return "-" if value is None else f"{value:.3f}"


def render_selected_task_metrics(task: str, metrics_by_task: dict) -> None:
    item = metrics_by_task.get(task)
    if not item:
        st.info("Model metrikleri bulunamadı. Önce eğitim scriptini çalıştır.")
        return

    metrics = item["metrics"]
    majority = item["majority_baseline"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", metric_value(metrics, "accuracy"))
    c2.metric("Macro F1", metric_value(metrics, "macro_f1"))
    c3.metric("Weighted F1", metric_value(metrics, "weighted_f1"))
    c4.metric("Majority Acc.", metric_value(majority, "accuracy"))


def render_report_links() -> None:
    links = [
        ("Veri özeti", DATASET_SUMMARY_PATH),
        ("Model metrikleri", BASELINE_METRICS_JSON_PATH.parent / "baseline_metrics.md"),
        ("Özellik seçimi", BASELINE_METRICS_JSON_PATH.parent / "feature_selection.md"),
    ]
    existing = [f"- [{name}]({path})" for name, path in links if path.exists()]
    if existing:
        st.markdown("\n".join(existing))


def main() -> None:
    st.set_page_config(
        page_title="House MD NLP",
        layout="wide",
    )

    st.title("House MD Türkçe Medikal Diyalog Analizi")

    rows, cols = load_dataset_shape()
    m1, m2, m3 = st.columns(3)
    m1.metric("Veri satırı", f"{rows:,}".replace(",", "."))
    m2.metric("Kolon", cols)
    m3.metric("Model görevi", len(TASKS))

    st.divider()

    left, right = st.columns([1.05, 1.4], gap="large")

    with left:
        task = st.selectbox(
            "Tahmin görevi",
            options=list(TASK_NAMES),
            format_func=lambda value: TASK_NAMES[value],
        )
        selected_example = st.selectbox("Örnek metin", options=list(EXAMPLES))
        default_text = EXAMPLES[selected_example]
        text = st.text_area("Diyalog cümlesi", value=default_text, height=160)
        analyze = st.button("Tahmin et", type="primary", use_container_width=True)

    metrics_by_task = load_metrics()

    with right:
        st.subheader(TASK_NAMES[task])
        render_selected_task_metrics(task, metrics_by_task)

        if analyze or text.strip():
            try:
                model = load_model(task)
                prediction, scores, matched_tokens = score_text(text, model)
            except FileNotFoundError:
                st.error("Model dosyası bulunamadı. Önce `python -m src.train_baselines` çalıştır.")
                return

            st.markdown(f"### Tahmin: `{prediction}`")
            top_scores = scores.head(8).copy()
            top_scores["Olasılık"] = top_scores["Olasılık"].round(4)
            top_scores["Log skor"] = top_scores["Log skor"].round(3)
            st.dataframe(top_scores, hide_index=True, use_container_width=True)

            chart_data = top_scores.set_index("Sınıf")[["Olasılık"]]
            st.bar_chart(chart_data)

            token_text = ", ".join(matched_tokens[:30]) if matched_tokens else "Model sözlüğünde eşleşen token yok."
            st.caption(f"Eşleşen tokenlar: {token_text}")

    st.divider()
    st.subheader("Rapor Dosyaları")
    render_report_links()


if __name__ == "__main__":
    main()
