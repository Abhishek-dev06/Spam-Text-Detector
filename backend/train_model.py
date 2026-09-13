import os
import joblib
import pandas as pd
from text_utils import clean_text

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(BASE_DIR, "spam.csv")
MODEL_PATH = os.path.join(BASE_DIR, "spam_model.joblib")
METRICS_PATH = os.path.join(BASE_DIR, "metrics.json")



def load_dataset():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            "\nspam.csv not found.\n"
            "Download the Kaggle SMS Spam Collection dataset and place spam.csv "
            "inside the backend folder.\n"
        )

    # Common Kaggle versions use v1 = ham/spam and v2 = message
    try:
        df = pd.read_csv(DATASET_PATH, encoding="latin-1")
    except UnicodeDecodeError:
        df = pd.read_csv(DATASET_PATH)

    if "v1" in df.columns and "v2" in df.columns:
        df = df[["v1", "v2"]].copy()
        df.columns = ["label", "text"]
    elif "label" in df.columns and "text" in df.columns:
        df = df[["label", "text"]].copy()
    else:
        raise ValueError(
            "Dataset must contain either columns v1/v2 or label/text."
        )

    df = df.dropna()
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df = df[df["label"].isin(["ham", "spam"])]

    return df


def main():
    df = load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.2,
        random_state=42,
        stratify=df["label"]
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                preprocessor=clean_text,
                stop_words="english",
                max_features=8000,
                ngram_range=(1, 2)
            )
        ),
        ("classifier", MultinomialNB())
    ])

    print("Training model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"\nAccuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:\n")
    print(classification_report(y_test, predictions))

    report = classification_report(
        y_test,
        predictions,
        output_dict=True,
        zero_division=0
    )

    metrics = {
        "accuracy": round(accuracy * 100, 2),
        "spam_precision": round(report["spam"]["precision"] * 100, 2),
        "spam_recall": round(report["spam"]["recall"] * 100, 2),
        "spam_f1": round(report["spam"]["f1-score"] * 100, 2),
        "test_samples": len(y_test)
    }

    joblib.dump(model, MODEL_PATH)

    with open(METRICS_PATH, "w") as f:
        import json
        json.dump(metrics, f, indent=4)

    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    main()
