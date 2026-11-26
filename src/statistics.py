"""Beskrivande statistik och gruppjämförelser."""
import pandas as pd

def descriptive_statistics(df, numeric_columns):
    """Beräknar beskrivande statistik för numeriska variabler."""

    # Beskrivande statistik
    mean = df[numeric_columns].mean()
    median = df[numeric_columns].median()
    min = df[numeric_columns].min()
    max = df[numeric_columns].max()
    std = df[numeric_columns].std()
    count = df[numeric_columns].count()

    statistics = pd.DataFrame({
        "Mean": mean,
        "Median": median,
        "Min": min,
        "Max": max,
        "Standardavvikelse": std,
        "Antal": count
    })

    return statistics

def correlation_matrix(df):
    """Beräknar korrelation mellan numeriska hälsovariabler."""

    corr_columns = [
        "age",
        "height",
        "weight",
        "systolic_bp",
        "cholesterol",
        "bmi",
        "disease"
    ]

    return df[corr_columns].corr(numeric_only=True)

def disease_by_smoking(df):
    """Antal, sjukdomsfall och andel per rökgrupp."""

    # Filtrera giltiga värden
    out = df.loc[
        df["smoker"].isin(["Yes", "No"]) &
        df["disease"].isin([0, 1])
    ]

    # Beräkna sjukdomsandel per rökgrupp
    return out.groupby("smoker")["disease"].agg(
        observations="count",
        disease_cases="sum",
        disease_proportion="mean"
    )

def smoking_summary(df):
    """Beskrivande statistik för blodtryck efter rökstatus."""

    # Filtrera giltiga rökgrupper
    out = df.loc[df["smoker"].isin(["Yes", "No"])]

    # Beräkna beskrivande statistik
    return out.groupby("smoker")["systolic_bp"].agg(
        antal="count",
        medelvärde="mean",
        median="median",
        standardavvikelse="std"
    )