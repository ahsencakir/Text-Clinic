import argparse
import json
from collections import Counter

try:
    from .config import MODELS_DIR
    from .train_baselines import tokenize
except ImportError:
    from config import MODELS_DIR
    from train_baselines import tokenize


def load_model(task: str) -> dict:
    path = MODELS_DIR / f"{task}_naive_bayes.json"
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def predict(text: str, model: dict) -> tuple[str, dict[str, float]]:
    token_to_id = {token: idx for idx, token in enumerate(model["vocabulary"])}
    counts = Counter(token for token in tokenize(text) if token in token_to_id)
    scores = {}

    for label in model["classes"]:
        score = float(model["class_log_prior"][label])
        probs = model["feature_log_prob"][label]
        for token, count in counts.items():
            score += count * float(probs[token_to_id[token]])
        scores[label] = score

    prediction = max(scores.items(), key=lambda item: item[1])[0]
    return prediction, scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Example: intent_norm")
    parser.add_argument("--text", required=True, help="Text to classify")
    args = parser.parse_args()

    model = load_model(args.task)
    prediction, scores = predict(args.text, model)
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    print(f"Task: {args.task}")
    print(f"Prediction: {prediction}")
    print("Top scores:")
    for label, score in sorted_scores[:5]:
        print(f"- {label}: {score:.3f}")


if __name__ == "__main__":
    main()
