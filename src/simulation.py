"""Reproducerbara binomial- och powersimuleringar."""
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest
from statsmodels.stats.power import NormalIndPower


def simulate_disease(df,n=1000,seed=42):

    # Simulering av 1000 personer

    # Beräkna den verkliga sjukdomsandelen
    disease_percent = df["disease"].mean()

    np.random.seed(seed)

    # Simulera 1000 personer med samma sjukdomssannolikhet
    simulation = np.random.binomial(
        n=1,
        p=disease_percent,
        size=n
    )
 
    # Beräkna den simulerade sjukdomsandelen
    simulated_percentage = simulation.mean()

    # Beräkna skillnaden mellan verklig och simulerad andel
    difference = abs(disease_percent - simulated_percentage)

    return simulation, disease_percent, simulated_percentage, difference

def simulated_power(
    smokers,
    non_smokers,
    vald_effekt,
    n_simulations=5000,
    alpha=0.05,
    seed=42
):
    """
    Simulerar statistisk power för ett ensidigt Welch's t-test.

    Parametrar:
    smokers: Blodtryck för rökare
    non_smokers: Blodtryck för icke-rökare
    vald_effekt: Antagen skillnad i medelblodtryck (mmHg)
    n_simulations: Antal upprepade simuleringar
    alpha: Signifikansnivå
    seed: Slumpfrö för reproducerbara resultat

    Returnerar:
    Uppskattad statistisk power
    """

    # Obeserverad group Statistiks
    n_smokers = len(smokers)
    n_non_smokers = len(non_smokers)

    sd_smokers = smokers.std(ddof=1)
    sd_non_smokers = non_smokers.std(ddof=1)

    mean_non_smokers = non_smokers.mean()
    mean_smokers = smokers.mean()

    
    rng = np.random.default_rng(seed)

    significant_results = 0

    # Upprepa simuleringen
    for i in range(n_simulations):

        # Simulera blodtryck för rökare med vald effekt
        simulated_smokers = rng.normal(
            loc=mean_non_smokers + vald_effekt,
            scale=sd_smokers,
            size=n_smokers
        )

        # Simulera blodtryck för icke-rökare
        simulated_non_smokers = rng.normal(
            loc=mean_non_smokers,
            scale=sd_non_smokers,
            size=n_non_smokers
        )

        # Genomför ensidigt Welch's t-test
        result = stats.ttest_ind(
            simulated_smokers,
            simulated_non_smokers,
            equal_var=False,
            alternative="greater"
        )

        # Räkna signifikanta resultat
        if result.pvalue < alpha:
            significant_results += 1

            
    power = significant_results / n_simulations


    return power


def analytical_power_proportions(
    p_A,
    p_B,
    n_A,
    n_B,
    alpha=0.05
):
    """Beräknar Cohen's h och analytisk power för två proportioner."""

    # Effektstorlek för två proportioner
    effect_size = proportion_effectsize(p_B, p_A)

    # Skapa power-modell
    power_model = NormalIndPower()

    # Beräkna power med befintliga gruppstorlekar
    power = power_model.power(
        effect_size=effect_size,
        nobs1=n_B,
        alpha=alpha,
        ratio=n_A / n_B,
        alternative="larger"
    )

    return {
        "effect_size": effect_size,
        "power": power,
        "alpha": alpha
    }

def simulated_power_proportions(
    p_A,
    p_B,
    n_A,
    n_B,
    n_simulations=5000,
    alpha=0.05,
    seed=42
):
    """
    Simulerar power för ett ensidigt z-test
    av två sjukdomsandelar.
    """
    rng = np.random.default_rng(seed)
    significant = 0

    for _ in range(n_simulations):

        # Simulera antal sjuka i varje grupp
        x_A = rng.binomial(n_A, p_A)
        x_B = rng.binomial(n_B, p_B)
        
        # Ensidigt z-test
        _, p_value = proportions_ztest(
            count=[x_B, x_A],
            nobs=[n_B, n_A],
            alternative="larger"
        )

        # Räkna signifikanta resultat
        if np.isfinite(p_value) and p_value < alpha:
            significant += 1

    return significant / n_simulations

def simulated_power_curve(
    p_A,
    n_A,
    n_B,
    assumed_proportions,
    n_simulations=5000,
    alpha=0.05,
    seed=42
):
    """Simulerar power vid olika antagna sjukdomsandelar."""

    power_results = []

    for assumed_p in assumed_proportions:

        # Simulera power för vald sjukdomsandel
        power = simulated_power_proportions(
            p_A=p_A,
            p_B=assumed_p,
            n_A=n_A,
            n_B=n_B,
            n_simulations=n_simulations,
            alpha=alpha,
            seed=seed
        )

        # Spara resultat
        power_results.append({
            "proportion": assumed_p,
            "effekt": assumed_p - p_A,
            "power": power
        })

    return power_results