"""Enkel och multipel regression med gemensam testmängd och OLS."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    root_mean_squared_error
)


def regression_analysis(
    df,
    features,
    target="systolic_bp",
    test_size=0.2,
    seed=42
):
    """
    Tränar och utvärderar enkel eller multipel
    linjär regression.
    """

    data = df.copy()

    if "smoker_numeric" in features:
        data["smoker_numeric"] = data["smoker"].map({
            "Yes": 1,
            "No": 0
        })

    # Ta bort saknade värden
    data = data[features + [target]].dropna()

    # Förklarande variabler och responsvariabel
    X = data[features]
    y = data[target]

    # Dela upp data i träning och test
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=seed
    )

    # Skapa och träna modellen
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Beräkna prediktioner och residualer
    y_pred = model.predict(X_test)
    residuals = y_test - y_pred

    # Beräkna utvärderingsmått
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)

    return {
        "model": model,
        "features": features,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "y_pred": y_pred,
        "residuals": residuals,
        "r2": r2,
        "mae": mae,
        "rmse": rmse
    }