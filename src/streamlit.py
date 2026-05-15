import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from transformers import pipeline

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (  # noqa: E402
    BASELINE_METRICS_JSON_PATH,
    DATASET_SUMMARY_PATH,
    MODELS_DIR,
    PROCESSED_DATA_PATH,
    RAW_DATA_PATH,
    TASKS,
)
from train_baselines import tr_lower, tokenize  # noqa: E402
import __main__
__main__.tokenize = tokenize

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

@st.cache_resource
def load_model(task: str) -> any:
    path = MODELS_DIR / f"{task}_lr_pipeline.joblib"
    if not path.exists():
        raise FileNotFoundError(path)
    return joblib.load(path)

@st.cache_resource
def load_bert_model():
    path = MODELS_DIR / "bert_model" / "best"
    if not path.exists():
        return None
    try:
        return pipeline("text-classification", model=str(path), tokenizer=str(path))
    except Exception as e:
        st.error(f"BERT modeli yüklenirken hata: {e}")
        return None

@st.cache_resource
def load_ner_model():
    path = MODELS_DIR / "ner_model" / "best"
    if not path.exists():
        return None
    try:
        return pipeline("token-classification", model=str(path), tokenizer=str(path), aggregation_strategy="simple")
    except Exception as e:
        st.error(f"NER modeli yüklenirken hata: {e}")
        return None

@st.cache_data
def load_metrics() -> dict:
    results = read_json(BASELINE_METRICS_JSON_PATH)
    return {item["task"]: item for item in results} if isinstance(results, list) else {}

@st.cache_data
def load_dataset() -> pd.DataFrame:
    path = PROCESSED_DATA_PATH if PROCESSED_DATA_PATH.exists() else RAW_DATA_PATH
    sep = "," if path == PROCESSED_DATA_PATH else ";"
    df = pd.read_csv(path, sep=sep, encoding="utf-8")
    return df

def score_text(text: str, speaker: str, model: any) -> tuple[str, pd.DataFrame]:
    df_input = pd.DataFrame([{
        "text_clean": tr_lower(text),
        "speaker": speaker,
        "has_symptom": 0,
        "has_test": 0,
        "has_drug": 0,
        "has_procedure": 0,
        "entity_count": 0.0
    }])
    
    proba = model.predict_proba(df_input)[0]
    classes = model.classes_
    prediction = classes[proba.argmax()]
    
    rows = [{"Sınıf": cls, "Olasılık": float(p)} for cls, p in zip(classes, proba)]
    scores = pd.DataFrame(rows).sort_values("Olasılık", ascending=False).reset_index(drop=True)
    return prediction, scores

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
    st.set_page_config(page_title="House MD NLP", layout="wide")
    st.title("House MD Türkçe Medikal Diyalog Analizi")

    df = load_dataset()
    m1, m2, m3 = st.columns(3)
    m1.metric("Veri satırı", f"{df.shape[0]:,}".replace(",", "."))
    m2.metric("Kolon", df.shape[1])
    m3.metric("Model görevi", len(TASKS))

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Diyalog Tahmini (Klasik Model)", "Diyalog Akışı & İstatistikleri", "Tüm Model Metrikleri", "Derin Öğrenme (BERT & NER)"])

    with tab1:
        left, right = st.columns([1.05, 1.4], gap="large")
        with left:
            task = st.selectbox(
                "Tahmin görevi",
                options=list(TASK_NAMES),
                format_func=lambda value: TASK_NAMES[value],
            )
            speaker = st.selectbox("Konuşmacı", options=["House", "Wilson", "Cameron", "Chase", "Foreman", "Cuddy", "Patient/Other"])
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
                    prediction, scores = score_text(text, speaker, model)
                except FileNotFoundError:
                    st.error("Model dosyası bulunamadı. Önce `python -m src.train_baselines` çalıştır.")
                    return

                st.markdown(f"### Tahmin: `{prediction}`")
                top_scores = scores.head(8).copy()
                top_scores["Olasılık"] = top_scores["Olasılık"].round(4)
                st.dataframe(top_scores, hide_index=True, use_container_width=True)

                chart_data = top_scores.set_index("Sınıf")[["Olasılık"]]
                st.bar_chart(chart_data)

    with tab2:
        st.subheader("Bölüm İçi Intent (Konuşma Amacı) Akışı")
        st.markdown("Doktorların konuşma amaçlarının (Intent) bir cümleden diğerine nasıl geçtiğini gösteren analiz.")
        
        if "intent_norm" in df.columns and "episode" in df.columns:
            # Shift intent to find next intent within the same episode
            df_flow = df.copy()
            df_flow["next_intent"] = df_flow.groupby(["season", "episode"])["intent_norm"].shift(-1)
            df_flow = df_flow.dropna(subset=["intent_norm", "next_intent"])
            df_flow = df_flow[df_flow["intent_norm"] != "unknown"]
            df_flow = df_flow[df_flow["next_intent"] != "unknown"]
            
            transitions = df_flow.groupby(["intent_norm", "next_intent"]).size().reset_index(name="count")
            transitions = transitions.sort_values(by="count", ascending=False).head(15)
            
            st.dataframe(transitions, use_container_width=True)
            
            st.subheader("Konuşmacı - Duygu Dağılımı")
            if "emotion_norm" in df.columns and "speaker" in df.columns:
                main_speakers = ["House", "Wilson", "Cameron", "Chase", "Foreman", "Cuddy"]
                emotion_df = df[df["speaker"].isin(main_speakers) & (df["emotion_norm"] != "unknown")]
                pivot = pd.crosstab(emotion_df["speaker"], emotion_df["emotion_norm"])
                st.bar_chart(pivot, height=400)
        else:
            st.warning("Gerekli kolonlar bulunamadı.")

    with tab3:
        st.subheader("Tüm Model Metrikleri Özeti (Scikit-Learn)")
        st.markdown("Burada eğitilen tüm görevlere ait klasik model performans metriklerini toplu halde görebilirsin.")
        
        if metrics_by_task:
            summary_rows = []
            for t_key, item in metrics_by_task.items():
                metrics = item["metrics"]
                summary_rows.append({
                    "Görev": item.get("task_label", t_key),
                    "Satır Sayısı": item.get("rows", 0),
                    "Sınıf Sayısı": len(item.get("classes", [])),
                    "Accuracy": round(metrics.get("accuracy", 0), 3),
                    "Macro F1": round(metrics.get("macro_f1", 0), 3),
                    "Weighted F1": round(metrics.get("weighted_f1", 0), 3)
                })
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Metrik bulunamadı. Önce `python -m src.train_baselines` çalıştır.")

    with tab4:
        st.subheader("Derin Öğrenme Modelleri (BERTurk & NER)")
        st.markdown("Eğittiğin BERT ve Medikal NER modellerini burada test edebilirsin.")
        
        dl_text = st.text_area("İncelenecek metin (Deep Learning):", value="Hastaya acilen 50 mg kortizon verin ve MR çekin.", height=100)
        bert_btn = st.button("BERT ile Sınıflandır (Konuşma Amacı)")
        ner_btn = st.button("NER ile Medikal Varlıkları Bul")
        
        if bert_btn:
            bert_model = load_bert_model()
            if bert_model is None:
                st.warning("BERT modeli henüz eğitilmemiş veya bulunamadı. Lütfen `python -m src.train_bert` çalıştırarak modeli eğitin.")
            else:
                with st.spinner("BERT modeli tahmin yapıyor..."):
                    result = bert_model(dl_text)
                    st.success(f"**Tahmin Edilen Sınıf:** {result[0]['label']} (Güven: %{result[0]['score']*100:.2f})")
                    
        if ner_btn:
            ner_model = load_ner_model()
            if ner_model is None:
                st.warning("NER modeli henüz eğitilmemiş veya bulunamadı. Lütfen `python -m src.train_ner` çalıştırarak modeli eğitin.")
            else:
                with st.spinner("NER modeli analiz yapıyor..."):
                    entities = ner_model(dl_text)
                    if not entities:
                        st.info("Metinde medikal varlık bulunamadı.")
                    else:
                        st.write("Bulunan Varlıklar:")
                        for ent in entities:
                            st.markdown(f"- **{ent['word']}** : `{ent['entity_group']}` (Güven: %{ent['score']*100:.2f})")

    st.divider()
    st.subheader("Rapor Dosyaları")
    render_report_links()

if __name__ == "__main__":
    main()
