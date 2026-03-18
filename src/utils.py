"""
Shared utilities for data loading, cleaning, and constants.

The survey was exported from Qualtrics as two CSV files:
  - Wave 2 (modified instrument, n=237): primary analytic sample
  - Wave 1 (original instrument, n=151): qualitative responses only

Qualtrics CSV structure:
  Row 0: Question text
  Row 1: Import IDs
  Row 2+: Response data

Model prefix mapping in column names:
  1_ = ChatGPT, 2_ = Claude, 3_ = Gemini, 4_ = Llama,
  5_ = Grok, 6_ = DeepSeek, 7_ = Mistral
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ---------- paths ----------
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WAVE2_PATH = DATA_DIR / "wave2_cleaned.csv"
WAVE1_PATH = DATA_DIR / "wave1_cleaned.csv"
FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# ---------- constants ----------
LIKERT_MAP = {
    "Extremely dissatisfied": 1,
    "Somewhat dissatisfied": 2,
    "Neither satisfied nor dissatisfied": 3,
    "Somewhat satisfied": 4,
    "Extremely satisfied": 5,
}

MODEL_IDS = {1: "ChatGPT", 2: "Claude", 3: "Gemini", 4: "Llama",
             5: "Grok", 6: "DeepSeek", 7: "Mistral"}

MODEL_COLORS = {
    "ChatGPT": "#2c7bb6", "Claude": "#d7191c", "Gemini": "#1a9641",
    "DeepSeek": "#fdae61", "Grok": "#7b3294", "Mistral": "#c2a5cf",
    "Llama": "#a6611a",
}

DRIVER_LABELS = [
    "Value", "Quality", "Multimodal", "UI/UX", "Speed",
    "Work Fit", "WoM", "Discount", "Censorship",
]

USE_CASE_LABELS = [
    "Content Creation", "Communication", "Learning & Research",
    "Technical", "Productivity", "Business",
]

MODEL_COLS = [f"QID5_{i}" for i in range(1, 8)]


# ---------- data loading ----------
def load_wave2(path=None):
    """Load wave 2 data (primary analytic sample), skipping Qualtrics header rows."""
    p = path or WAVE2_PATH
    df_raw = pd.read_csv(p, low_memory=False)
    data = df_raw.iloc[2:].reset_index(drop=True)
    return data, df_raw


def load_wave1(path=None):
    """Load wave 1 data (qualitative supplement)."""
    p = path or WAVE1_PATH
    df_raw = pd.read_csv(p, low_memory=False)
    data = df_raw.iloc[2:].reset_index(drop=True)
    return data, df_raw


def get_satisfaction(data, model_id):
    """Return numeric satisfaction series for a given model."""
    col = f"{model_id}_QID14_1"
    return data[col].map(LIKERT_MAP).dropna()


def get_drivers(data, model_id):
    """Return DataFrame of 9 adoption driver scores for a model."""
    cols = [f"{model_id}_QID22_{i}" for i in range(1, 10)]
    df = data[cols].apply(pd.to_numeric, errors="coerce")
    df.columns = DRIVER_LABELS
    return df.dropna(how="all")


def get_use_cases(data, model_id):
    """Return DataFrame of 6 use case scores for a model."""
    cols = [f"{model_id}_QID25_{i}" for i in range(1, 7)]
    df = data[cols].apply(pd.to_numeric, errors="coerce")
    df.columns = USE_CASE_LABELS
    return df.dropna(how="all")


def platform_count(data):
    """Return Series of how many platforms each respondent uses."""
    return data[MODEL_COLS].notna().sum(axis=1)


def complete_mask(data):
    """Return boolean mask for respondents with occupation AND at least 1 model."""
    has_occ = data["QID2"].notna()
    has_model = data[MODEL_COLS].notna().any(axis=1)
    return has_occ & has_model
