"""
Configuration file for the Machine Learning pipeline.

All paths and constants are defined here.
"""

from pathlib import Path

# -------------------------------------------------------
# Project Root
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# -------------------------------------------------------
# Dataset
# -------------------------------------------------------

DATASET_DIR = PROJECT_ROOT / "datasets"

RAW_DATASET_DIR = DATASET_DIR / "raw"

PROCESSED_DATASET_DIR = DATASET_DIR / "processed"

HEART_DATASET = (
    RAW_DATASET_DIR
    / "heart_disease"
    / "processed.cleveland.data"
)

FINAL_DATASET = (
    PROCESSED_DATASET_DIR
    / "patient_health_dataset.csv"
)

# -------------------------------------------------------
# ML Models
# -------------------------------------------------------

MODEL_DIR = PROJECT_ROOT / "ml_model"

TRAINED_MODEL_DIR = MODEL_DIR / "trained"

ENCODER_DIR = MODEL_DIR / "encoders"

REPORT_DIR = MODEL_DIR / "reports"

# -------------------------------------------------------
# Saved Models
# -------------------------------------------------------

RANDOM_FOREST_MODEL = (
    TRAINED_MODEL_DIR / "random_forest.pkl"
)

XGBOOST_MODEL = (
    TRAINED_MODEL_DIR / "xgboost.pkl"
)

# -------------------------------------------------------
# Encoders
# -------------------------------------------------------

LABEL_ENCODER = (
    ENCODER_DIR / "label_encoder.pkl"
)

GENDER_ENCODER = (
    ENCODER_DIR / "gender_encoder.pkl"
)

FEATURE_COLUMNS = (
    ENCODER_DIR / "feature_columns.pkl"
)

# -------------------------------------------------------
# Reports
# -------------------------------------------------------

MODEL_COMPARISON = (
    REPORT_DIR / "model_comparison.csv"
)

EVALUATION_REPORT = (
    REPORT_DIR / "evaluation_report.json"
)

# -------------------------------------------------------
# Random State
# -------------------------------------------------------

RANDOM_STATE = 42

TEST_SIZE = 0.20
# -------------------------------------------------------
# Reports
# -------------------------------------------------------

FEATURE_IMPORTANCE = REPORT_DIR / "feature_importance.csv"

RANDOM_FOREST_REPORT = REPORT_DIR / "random_forest_metrics.json"

# -------------------------------------------------------
# XGBoost
# -------------------------------------------------------

XGBOOST_REPORT = REPORT_DIR / "xgboost_metrics.json"

BEST_MODEL_REPORT = REPORT_DIR / "best_model.json"

MODEL_COMPARISON_CSV = REPORT_DIR / "model_comparison.csv"

FINAL_EVALUATION_REPORT = REPORT_DIR / "evaluation_report.json"