"""Figurer med svenska etiketter och återanvändbara layouter."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets

from IPython.display import display
from src.statistics import correlation_matrix


UNITS = {
    "age": "år",
    "height": "cm",
    "weight": "kg",
    "systolic_bp": "mmHg",
    "cholesterol": "mmol/L",
    "bmi": "kg/m²"
}

# Svenska variabelnamn
LABELS = {
    "age": "Ålder",
    "height": "Längd",
    "weight": "Vikt",
    "systolic_bp": "Systoliskt blodtryck",
    "cholesterol": "Kolesterol",
    "bmi": "BMI"
}

def plot_distribution(df, column, ax, bins=25):
    """Visualiserar fördelningen av en numerisk variabel."""

    ax.hist(df[column].dropna(), bins=bins, color="cornflowerblue", edgecolor="black", alpha=0.85)
    
    ax.set(title=f"Fördelning av {LABELS[column]}", 
           xlabel=f"{LABELS[column]} ({UNITS[column]})", 
           ylabel="Antal personer")
    ax.grid(axis="y", alpha=0.4)

def plot_group_comparison(df, column, group, ax):

    """Jämför en numerisk variabel mellan grupper."""

    sns.boxplot(
        data=df,
        x=group,
        y=column,
        color="coral",
        ax=ax
    )

    ax.set_title(f"Fördelning av {LABELS[column]} efter {group}")
    ax.set_xlabel(LABELS.get(group, group))
    ax.set_ylabel(f"{LABELS[column]} ({UNITS[column]})")
    ax.grid(axis="y", alpha=0.3)


def plot_smoking_distribution(df, ax):

    """Visualiserar fördelningen av rökstatus."""

    counts = df["smoker"].value_counts()
    total = counts.sum()
    
    sns.countplot(
        data=df,
        x="smoker",
        color="coral",
        edgecolor="black",
        width=0.6,
        ax=ax
    )
    # Visa antal och procent ovanför staplarna
    for bar, count in zip(ax.patches, counts):
        percent = count / total * 100

        ax.annotate(
            f"{count} ({percent:.1f} %)",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10
        )

    ax.set_title("Fördelning av rökstatus")
    ax.set_xlabel("Rökstatus")
    ax.set_ylabel("Antal personer")
    ax.tick_params(axis="x", rotation=0)
    ax.set_ylim(0, counts.max() * 1.15)
    ax.grid(axis="y", alpha=0.3)

def plot_correlation_matrix(correlation_matrix):

    """Visualiserar korrelationsmatrisen som en heatmap."""

    plt.figure(figsize=(16, 5))

    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap="coolwarm",
        center=0,
        fmt=".2f"
    )

    plt.title("Korrelationsmatris för numeriska variabler")
    plt.tight_layout()
    plt.show()

def plot_relationship(df, x, y, ax):
    """Visualiserar sambandet mellan två numeriska variabler."""

    sns.regplot(
        data=df,
        x=x,
        y=y,
        scatter_kws={"alpha": 0.4},
        line_kws={"color": "red", "linewidth": 2},
        ci=None,
        ax=ax
    )

    # Svenska etiketter och enheter
    x_label = LABELS.get(x, x)
    y_label = LABELS.get(y, y)

    x_unit = UNITS.get(x)
    y_unit = UNITS.get(y)

    ax.set_xlabel(f"{x_label} ({x_unit})" if x_unit else x_label)
    ax.set_ylabel(f"{y_label} ({y_unit})" if y_unit else y_label)

    ax.set_title(f"{y_label} efter {x_label.lower()}")
    ax.grid(alpha=0.3)

def plot_disease_boxplot(df, column, ax):
    """Jämför en hälsovariabel mellan personer med och utan sjukdom."""

    # Gruppera data efter sjukdomsstatus
    grouped = df.groupby("disease")[column]

    # Hämta värden för båda grupperna
    data = [
        grouped.get_group(0).dropna(),
        grouped.get_group(1).dropna()
    ]

    # Skapa boxplot
    ax.boxplot(
        data,
        tick_labels=["Ingen sjukdom", "Sjukdom"]
    )

    # Svenska variabelnamn och enheter
    y_label = LABELS.get(column, column)
    y_unit = UNITS.get(column)

    ax.set_title(f"{y_label} efter sjukdomsstatus")
    ax.set_xlabel("Sjukdomsstatus \n Disease (0 = No, 1 = Yes)")
    ax.set_ylabel(f"{y_label} ({y_unit})" if y_unit else y_label)

    ax.grid(axis="y", alpha=0.3)

def plot_smoking_disease(df, ax):
    """Visualiserar sjukdomsandel efter rökstatus."""

    # Beräkna sjukdomsandel inom varje rökgrupp
    smoking_disease = pd.crosstab(
        df["smoker"],
        df["disease"],
        normalize="index"
    )

    # Skapa staplat stapeldiagram
    smoking_disease.plot(
        kind="bar",
        stacked=True,
        ax=ax
    )

    # Svenska etiketter
    ax.set_title("Sjukdomsandel efter rökstatus")
    ax.set_xlabel("Rökstatus")
    ax.set_ylabel("Andel")
    ax.set_ylim(0, 1)

    ax.legend(
        title="Sjukdom",
        labels=["Ingen sjukdom", "Sjukdom"]
    )

    ax.tick_params(axis="x", rotation=0)
    ax.grid(axis="y", alpha=0.3)  

# ---------------------------------------
# Visualisering av sjukdomsfördelning och simulering
# ---------------------------------------

def plot_disease_simulation(df, simulation):

    """Visualiserar sjukdomsfördelning och verklig/simulerad sjukdomsandel."""

    # Beräkna sjukdomsfördelningen
    disease_counts = df["disease"].value_counts().reindex(
        [0, 1], fill_value=0
    )

    disease_percentages = (
        df["disease"].value_counts(normalize=True)
        .reindex([0, 1], fill_value=0) * 100
    )

    # Beräkna verklig och simulerad sjukdomsandel
    disease_percent = df["disease"].mean()
    simulated_percentage = np.mean(simulation)

    # Skapa två diagram
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # ---------------------------------------
    # Diagram 1: Sjukdomsfördelning
    # ---------------------------------------

    bars = axes[0].bar(
        ["Ingen sjukdom", "Sjukdom"],
        disease_counts.values,
        color=["steelblue", "orange"],
        edgecolor="black",
        width=0.5
    )

    # Visa antal och procent ovanför staplarna
    for i, bar in enumerate(bars):
        height = bar.get_height()

        axes[0].annotate(
            f"{int(height)} ({disease_percentages.iloc[i]:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12
        )

    axes[0].set(
        title="Sjukdomsfördelning i datasetet",
        xlabel="Sjukdomsstatus",
        ylabel="Antal personer"
    )

    axes[0].set_ylim(0, max(disease_counts.max() * 1.15, 1))
    axes[0].grid(axis="y", alpha=0.3)

    # ---------------------------------------
    # Diagram 2: Jämförelse av sjukdomsandelar
    # ---------------------------------------

    labels = ["Verklig andel", "Simulerad andel"]

    values = [
        disease_percent * 100,
        simulated_percentage * 100
    ]

    bars = axes[1].bar(
        labels,
        values,
        color=["steelblue", "orange"],
        edgecolor="black",
        width=0.5
    )

    # Visa procent ovanför staplarna
    for bar in bars:
        height = bar.get_height()

        axes[1].annotate(
            f"{height:.2f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12
        )

    axes[1].set(
        title="Verklig och simulerad sjukdomsandel",
        xlabel="Typ av sjukdomsandel",
        ylabel="Sjukdomsandel (%)"
    )

    axes[1].set_ylim(0, max(max(values) * 1.2, 1))
    axes[1].grid(axis="y", alpha=0.3)

   
    fig.suptitle(
        "Simulering av sjukdomsandel",
        fontsize=18,
        fontweight="bold"
    )

    fig.tight_layout()

    return fig

def plot_bootstrap_ci(normal, bootstrap, title, xlabel, unit):

    """Jämför normalapproximation och bootstrap-konfidensintervall."""
      
    lower, upper, mean, s, SE, n = normal

    boot_means, ci_boot_lower, ci_boot_upper = bootstrap

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    axes[0].errorbar(
        mean,
        1,
        xerr=[[mean - lower], [upper - mean]],
        fmt="o",
        capsize=10,
        label="Normalapproximation"
    )
    
    axes[0].errorbar(
        np.mean(boot_means),
        0,
        xerr=[[
            np.mean(boot_means) - ci_boot_lower
        ], [
            ci_boot_upper - np.mean(boot_means)
        ]],
        fmt="o",
        capsize=10,
        label="Bootstrap"
    )
    
    axes[0].axvline(
        mean,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"Stickprovsmedelvärde:{mean:.2f}"
    )
    
    axes[0].set_yticks([0, 1])
    axes[0].set_yticklabels(["Bootstrap", "Normal\napproximation"])
    axes[0].set_xlabel(xlabel)
    axes[0].set_title("Jämförelse av 95 % konfidensintervall")
    axes[0].legend()
    axes[0].grid(axis="x", alpha=0.3)
    
    
    
    # Visualisering av  Bootstrap Fördelning
    
    
    axes[1].hist(
        boot_means,
        bins=30,
        color="skyblue",
        edgecolor="black",
        alpha=0.8
    )
    
    axes[1].axvline(
        mean,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Stickprovsmedelvärde: {mean:.2f}"
    )
    
    axes[1].axvline(
        ci_boot_lower,
        color="purple",
        linestyle="--",
        linewidth= 1,
        label="95 % Bootstrap KI"
    )
    
    axes[1].axvline(
        ci_boot_upper,
        color="purple",
        linewidth= 1,
        linestyle="--"
    )
    
    axes[1].set_xlabel(xlabel)
    axes[1].set_ylabel("Antal bootstrap-stickprov")
    axes[1].set_title("Bootstrapfördelning")
    axes[1].legend()
    axes[1].grid(axis="y", alpha=0.3)

    fig.suptitle(title, fontsize=18, fontweight="bold")

    plt.tight_layout()
    plt.show()
    
def plot_smoking_bp(df, test):
    """Visualiserar blodtryck efter rökstatus och skillnad med 95 % KI."""

    # Dela upp grupperna
    non_smokers = df.loc[
        df["smoker"] == "No", "systolic_bp"
    ].dropna()

    smokers = df.loc[
        df["smoker"] == "Yes", "systolic_bp"
    ].dropna()

    # Beräkna medianer
    medians = [non_smokers.median(), smokers.median()]

    # Skapa två diagram
    fig, axes = plt.subplots(1, 2, figsize=(18, 4))

    # Diagram 1: Boxplot
    sns.boxplot(
        data=df,
        x="smoker",
        y="systolic_bp",
        order=["No", "Yes"],
        color="lightblue",
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "red",
            "markeredgecolor": "red",
            "markersize": 7
        },
        ax=axes[0]
    )

    # Visa medianvärden
    for i, median in enumerate(medians):
        axes[0].text(
            i,
            median + 2,
            f"Median = {median:.1f}",
            ha="center",
            va="bottom",
            fontsize=10
        )

    axes[0].set_xticks([0, 1])
    axes[0].set_xticklabels(["Icke-rökare", "Rökare"])
    axes[0].set_xlabel("Rökstatus")
    axes[0].set_ylabel("Systoliskt blodtryck (mmHg)")
    axes[0].set_title("Systoliskt Blodtryck hos rökare och icke-rökare")
    axes[0].grid(axis="y", alpha=0.3)

    # Diagram 2: Skillnad i medelvärde med KI
    observed_skillnad = test["observed_skillnad"]
    lower = test["lower"]
    upper = test["upper"]

    axes[1].errorbar(
        0,
        observed_skillnad,
        yerr=[
            [observed_skillnad- lower],
            [upper - observed_skillnad]
        ],
        fmt="o",
        color="blue",
        markersize=9,
        capsize=7,
        label="Observerad skillnad med 95 % KI"
    )

    # Referenslinje vid noll
    axes[1].axhline(
        0,
        color="red",
        linestyle="--",
        label="Ingen skillnad"
    )

    axes[1].set_xticks([0])
    axes[1].set_xticklabels(["Rökare − icke-rökare"])
    axes[1].set_ylabel("Skillnad i medelvärde (mmHg)")
    axes[1].set_title("Skillnad i systoliskt blodtryck mellan rökare och icke-rökare")
    axes[1].legend()
    axes[1].grid(axis="y", alpha=0.3)

    fig.tight_layout()

    return fig


def plot_power_curve(
    power_result,
    title,
    xlabel,
    target_power=0.80
):
    """Visualiserar statistisk power vid olika antagna effektstorlekar."""

    fig = plt.figure(figsize=(9, 5))

    plt.plot(
        list(power_result.keys()),
        list(power_result.values()),
        marker="o",
        color="steelblue",
        linewidth=2,
        markersize=8
    )

    # Referenslinje för önskad power
    plt.axhline(
        y=target_power,
        color="red",
        linestyle="--",
        label=f"Referensnivå: {target_power:.0%}"
    )

    # Visa power i procent vid varje punkt
    for effect, power in power_result.items():
        plt.annotate(
            f"{power:.1%}",
            (effect, power),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center"
        )

    # Diagraminställningar
    plt.ylim(0, 1.10)
    plt.ylabel("Uppskattad statistisk power")
    plt.xlabel(xlabel)
    plt.title(title)
    plt.xticks(rotation=15)
    plt.legend()
    plt.tight_layout()

    return fig



def plot_simple_regression(linreg):
    """
    Visualiserar regressionslinjen och residualerna
    för enkel linjär regression.
    """

    linreg_model = linreg["model"]

    # Sortera åldersvärden
    X_line = linreg["X_train"].sort_values("age")

    # Beräkna regressionslinjen
    y_line = linreg_model.predict(X_line)

    fig, axes = plt.subplots(1, 2, figsize=(18, 5))

    # Regressionslinje
    axes[0].scatter(
        linreg["X_train"]["age"],
        linreg["y_train"],
        alpha=0.4,
        label="Observationer"
    )

    axes[0].plot(
        X_line["age"],
        y_line,
        color="red",
        linewidth=2,
        label="Regressionslinje"
    )

    axes[0].set_title("Enkel linjär regression – Ålder och blodtryck")
    axes[0].set_xlabel("Ålder (år)")
    axes[0].set_ylabel("Systoliskt blodtryck (mmHg)")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Residualdiagram
    axes[1].scatter(
        linreg["y_pred"],
        linreg["residuals"],
        alpha=0.5
    )

    axes[1].axhline(
        0,
        color="red",
        linestyle="--"
    )

    axes[1].set_title("Residualdiagram – Enkel linjär regression")
    axes[1].set_xlabel("Förutsagt blodtryck (mmHg)")
    axes[1].set_ylabel("Residualer (mmHg)")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

def plot_multiple_regression(multiple):
    """
    Visualiserar prediktioner och residualer
    för multipel linjär regression.
    """

    y_test = multiple["y_test"]
    y_pred = multiple["y_pred"]
    residuals = multiple["residuals"]

    fig, axes = plt.subplots(1, 2, figsize=(18, 5))

    # Observerade och förutsagda värden
    axes[0].scatter(
        y_test,
        y_pred,
        alpha=0.5,
        label="Observationer"
    )

    lower = min(y_test.min(), y_pred.min())
    upper = max(y_test.max(), y_pred.max())

    # Referenslinje för perfekt prediktion
    axes[0].plot(
        [lower, upper],
        [lower, upper],
        color="red",
        linestyle="--",
        label="Perfekt prediktion"
    )

    axes[0].set_title("Observerat och förutsagt blodtryck")
    axes[0].set_xlabel("Observerat blodtryck (mmHg)")
    axes[0].set_ylabel("Förutsagt blodtryck (mmHg)")
    axes[0].set_xlim(lower, upper)
    axes[0].set_ylim(lower, upper)
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Residualdiagram
    axes[1].scatter(
        y_pred,
        residuals,
        alpha=0.5
    )

    axes[1].axhline(
        0,
        color="red",
        linestyle="--"
    )

    axes[1].set_title("Residualdiagram – Multipel linjär regression")
    axes[1].set_xlabel("Förutsagt blodtryck (mmHg)")
    axes[1].set_ylabel("Residualer (mmHg)")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

def plot_interactive_simple(result):
    """
    Interaktiv prognos av systoliskt blodtryck
    utifrån ålder.
    """

    model = result["model"]
    X_train = result["X_train"]
    y_train = result["y_train"]

    # Beräkna regressionslinjen
    X_line = X_train.sort_values("age")
    y_line = model.predict(X_line)

    @widgets.interact(
        age=widgets.IntSlider(
            min=int(X_train["age"].min()),
            max=int(X_train["age"].max()),
            value=int(X_train["age"].median()),
            step=1,
            description="Ålder:",
            continuous_update=False
        )
    )
    def interactive_regression(age):

        # Skapa ny observation
        X_new = pd.DataFrame({
            "age": [age]
        })

        # Beräkna prognos
        prediction = model.predict(X_new)[0]

        plt.figure(figsize=(18, 4.5))

        # Observerade värden
        plt.scatter(
            X_train["age"],
            y_train,
            alpha=0.3,
            label="Observationer"
        )

        # Regressionslinje
        plt.plot(
            X_line["age"],
            y_line,
            color="blue",
            label="Regressionslinje"
        )

        # Markera prognosen
        plt.scatter(
            age,
            prediction,
            color="red",
            s=100,
            zorder=5,
            label=f"Prognos: {prediction:.1f} mmHg"
        )

        # Referenslinjer
        plt.axvline(
            age,
            linestyle="--",
            color="gray"
        )

        plt.axhline(
            prediction,
            linestyle="--",
            color="gray"
        )

        plt.title("Interaktiv prognos av systoliskt blodtryck")
        plt.xlabel("Ålder (år)")
        plt.ylabel("Systoliskt blodtryck (mmHg)")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

def plot_interactive_multiple(result):
    """
    Interaktiv prognos av systoliskt blodtryck
    utifrån ålder, vikt, kolesterol och rökstatus.
    """

    model = result["model"]
    X_train = result["X_train"]

    # Skapa sliders utifrån träningsdata
    @widgets.interact(
        age=widgets.IntSlider(
            min=int(X_train["age"].min()),
            max=int(X_train["age"].max()),
            value=int(X_train["age"].median()),
            step=1,
            description="Ålder:",
            continuous_update=False
        ),

        weight=widgets.FloatSlider(
            min=X_train["weight"].min(),
            max=X_train["weight"].max(),
            value=X_train["weight"].median(),
            step=0.5,
            description="Vikt:",
            continuous_update=False
        ),

        cholesterol=widgets.FloatSlider(
            min=X_train["cholesterol"].min(),
            max=X_train["cholesterol"].max(),
            value=X_train["cholesterol"].median(),
            step=0.1,
            description="Kolesterol:",
            continuous_update=False
        ),

        smoker=widgets.Dropdown(
            options=[
                ("Icke-rökare", 0),
                ("Rökare", 1)
            ],
            description="Rökstatus:"
        )
    )
    def interactive_multiple_regression(
        age, weight, cholesterol, smoker
    ):

        # Skapa ny observation
        X_new = pd.DataFrame({
            "age": [age],
            "weight": [weight],
            "cholesterol": [cholesterol],
            "smoker_numeric": [smoker]
        })

        # Säkerställ samma kolumnordning som träningsdata
        X_new = X_new[result["features"]]

        # Beräkna prognos
        prediction = model.predict(X_new)[0]

        # Kompakt visualisering
        fig, ax = plt.subplots(figsize=(18, 1.3))

        ax.barh(
            0,
            prediction,
            height=0.5,
            color="steelblue"
        )

        ax.set_title(
            f"Förutsagt systoliskt blodtryck: {prediction:.1f} mmHg",
            fontsize=11,
            pad=3
        )

        ax.set_xlim(
            min(0, prediction),
            max(200, prediction + 20)
        )

        ax.set_ylim(-0.3, 0.3)
        ax.set_yticks([])

        ax.set_xlabel(
            "Systoliskt blodtryck (mmHg)",
            fontsize=9,
            labelpad=2
        )

        ax.tick_params(axis="x", labelsize=8)

        # Ta bort onödiga kanter
        ax.spines[["top", "right", "left"]].set_visible(False)

        ax.grid(axis="x", alpha=0.2)
        ax.set_axisbelow(True)

        plt.tight_layout(pad=0.2)
        plt.show()    

def plot_disease_proportion_ci(
    test,
    confidence=0.95
):
    """Visualiserar sjukdomsandel och skillnad med konfidensintervall."""

    p_A = test["p_A"]
    p_B = test["p_B"]

    ci_A = test["ci_A"]
    ci_B = test["ci_B"]

    diff = test["difference"]
    diff_ci_low = test["lower"]
    diff_ci_high = test["upper"]

    ci_percent = confidence * 100

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Sjukdomsandel per grupp
    proportions = np.array([p_A, p_B]) * 100

    errors = [
        [(p_A - ci_A[0])*100, (p_B - ci_B[0])*100],
        [(ci_A[1] - p_A)*100, (ci_B[1] - p_B)*100]
    ]

    axes[0].bar(
        ["Icke-rökare", "Rökare"],
        proportions,
        yerr=errors,
        capsize=7
    )

    axes[0].set_ylabel("Sjukdomsandel (%)")
    axes[0].set_title(f"Sjukdomsandel med {ci_percent:g} % KI")
    axes[0].grid(axis="y", alpha=0.3)

    # Skillnad mellan grupper
    axes[1].errorbar(
        [0],
        [diff * 100],
        yerr=[
            [(diff - diff_ci_low) * 100],
            [(diff_ci_high - diff) * 100]
        ],
        fmt="o",
        capsize=7
    )

    # Referenslinje vid noll
    axes[1].axhline( 0, color="red", linestyle="--", label="Ingen skillnad")

    axes[1].set_xticks([0])
    axes[1].set_xticklabels(["Rökare - icke-rökare"])
    axes[1].set_ylabel("Skillnad (procentenheter)")
    axes[1].set_title(f"Skillnad i sjukdomsandel med {ci_percent:g} % KI")
    axes[1].grid(axis="y", alpha=0.3)
    axes[1].legend()

    plt.tight_layout()

    return fig

def plot_power_proportions(
    power_results,
    title,
    xlabel,
    target_power=0.80
):
    """Visualiserar simulerad power vid olika skillnader i andelar."""


    # Omvandla till procentenheter och procent
    differences = [
        r["effekt"] * 100 for r in power_results
    ]

    powers = [
        r["power"] * 100 for r in power_results
    ]

    fig = plt.figure(figsize=(9, 5))

    plt.plot(
        differences,
        powers,
        marker="o",
        linewidth=2,
        color="steelblue"
    )

    # Referenslinje för önskad power
    plt.axhline(
        target_power * 100,
        color="red",
        linestyle="--",
        label=f"{target_power:.0%} power"
    )

    # Visa power vid varje punkt
    for effect, power in zip(differences, powers):

        plt.annotate(
            f"{power:.1f} %",
            (effect, power),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center"
        )

    plt.xlabel(xlabel)
    plt.ylabel("Simulerad power (%)")
    plt.title(title)
    plt.ylim(0, 110)

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    return fig