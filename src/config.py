from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "house_md_dataset.csv"
PROCESSED_DATA_PATH = DATA_DIR / "house_md_clean.csv"

REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR = PROJECT_ROOT / "models"

DATASET_SUMMARY_PATH = REPORTS_DIR / "dataset_summary.md"
LABEL_DISTRIBUTION_PATH = REPORTS_DIR / "label_distribution.csv"
BASELINE_METRICS_JSON_PATH = REPORTS_DIR / "baseline_metrics.json"
BASELINE_METRICS_MD_PATH = REPORTS_DIR / "baseline_metrics.md"
PREDICTION_SAMPLES_PATH = REPORTS_DIR / "prediction_samples.csv"
FEATURE_SELECTION_REPORT_PATH = REPORTS_DIR / "feature_selection.md"

RANDOM_SEED = 42

TASKS = {
    "intent_norm": {
        "label": "Konusma amaci",
        "min_count": 20,
        "exclude": {"unknown"},
    },
    "emotion_norm": {
        "label": "Duygu",
        "min_count": 20,
        "exclude": {"unknown"},
    },
    "sarcasm_label": {
        "label": "Sarkazm",
        "min_count": 5,
        "exclude": {"unknown"},
    },
    "diagnosis_stage_norm": {
        "label": "Tani asamasi",
        "min_count": 20,
        "exclude": {"unknown"},
    },
    "organ_norm": {
        "label": "Organ/sistem",
        "min_count": 20,
        "exclude": {"unknown"},
    },
}
