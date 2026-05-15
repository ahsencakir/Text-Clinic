import argparse

import joblib
import pandas as pd

try:
    from .config import MODELS_DIR
    from .train_baselines import tr_lower, tokenize
except ImportError:
    from config import MODELS_DIR
    from train_baselines import tr_lower, tokenize

import __main__
__main__.tokenize = tokenize


def load_model(task: str) -> any:
    path = MODELS_DIR / f"{task}_lr_pipeline.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    return joblib.load(path)


def predict(text: str, speaker: str, model: any) -> tuple[str, dict[str, float]]:
    # Create a DataFrame matching the training pipeline
    df = pd.DataFrame([{
        "text_clean": tr_lower(text),
        "speaker": speaker,
        "has_symptom": 0,
        "has_test": 0,
        "has_drug": 0,
        "has_procedure": 0,
        "entity_count": 0.0
    }])
    
    proba = model.predict_proba(df)[0]
    classes = model.classes_
    scores = {cls: float(p) for cls, p in zip(classes, proba)}
    prediction = classes[proba.argmax()]
    
    return prediction, scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Example: intent_norm")
    parser.add_argument("--text", required=True, help="Text to classify")
    parser.add_argument("--speaker", default="House", help="Speaker name (e.g. House, Wilson)")
    args = parser.parse_args()

    model = load_model(args.task)
    prediction, scores = predict(args.text, args.speaker, model)
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    print(f"Task: {args.task}")
    print(f"Prediction: {prediction}")
    print("Top scores:")
    for label, score in sorted_scores[:5]:
        print(f"- {label}: {score:.3f}")


if __name__ == "__main__":
    main()
