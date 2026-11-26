"""Konfidensintervall och hypotesprövningar med SciPy och Statsmodels."""
import numpy as np
from scipy import stats
from statsmodels.stats.weightstats import DescrStatsW, CompareMeans
from statsmodels.stats.proportion import proportion_confint, proportions_ztest, confint_proportions_2indep

def _numeric(values):
    x=np.asarray(values,dtype=float)
    return x[np.isfinite(x)]

def ci_mean_normal(data, confidence=0.95):
    """Beräknar konfidensintervall för medelvärdet med normalapproximation."""

    # Omvandla data till en NumPy-array
    data = np.asarray(data, dtype=float)

    # Ta bort saknade värden
    data = data[np.isfinite(data)]

    # Beräkna stickprovsstorlek
    n = len(data)

    if n < 2:
        raise ValueError("Minst två värden krävs.")

    # Beräkna medelvärde och standardavvikelse
    mean = np.mean(data)
    s = np.std(data, ddof=1)

    # Beräkna standardfel
    SE = s / np.sqrt(n)

    # Kritiskt Z-värde
    z_critical = stats.norm.ppf((1 + confidence) / 2)

    # Beräkna felmarginal
    half_width = z_critical * SE

    # Beräkna konfidensintervallet
    lower = mean - half_width
    upper = mean + half_width

    return lower, upper, mean, s, SE, n

def ci_mean_bootstrap(data, B=10000, seed=42):

    # Omvandla data till en NumPy-array
    data = np.asarray(data, dtype=float)

    # Ta bort saknade värden
    data = data[~np.isnan(data)]

    # Antal observationer
    n = len(data)
    if n < 2:
        raise ValueError("Minst två värden krävs.")
    
    # Skapa slumpgenerator
    rng = np.random.default_rng(seed)

    # Lagra bootstrap-medelvärden
    boot_means = np.empty(B)

    # Skapa bootstrap-stickprov
    for b in range(B):

        boot_sample = rng.choice(
            data,
            size=n,
            replace=True
        )

        boot_means[b] = np.mean(boot_sample)

    ci_boot_lower, ci_boot_upper = np.percentile(boot_means, [2.5, 97.5])
    return boot_means,ci_boot_lower, ci_boot_upper



def test_two_means(a, b, alternative="greater", confidence=0.95):
    """Welch t-test, konfidensintervall och Cohen's d."""

    a = _numeric(a)
    b = _numeric(b)

    if min(len(a), len(b)) < 2:
        raise ValueError("Minst två observationer per grupp.")

    # Gruppstatistik
    n_a, n_b = len(a), len(b)
    mean_a, mean_b = np.mean(a), np.mean(b)
    s_a, s_b = np.std(a, ddof=1), np.std(b, ddof=1)
    
    # Observerad skillnad
    observed_skillnad = mean_a - mean_b

    # Welch's t-test 
    test_result = stats.ttest_ind(
        a,
        b,
        equal_var=False,
        alternative=alternative
    )
    
    # ----------------------------------
    # 95 % konfidensintervall med Statsmodels
    # ----------------------------------
    
    stats_a = DescrStatsW(a)
    stats_b = DescrStatsW(b)
    
    comparison = CompareMeans(stats_a, stats_b)
    
     # Tvåsidigt konfidensintervall
    ci_lower, ci_upper = comparison.tconfint_diff(
        alpha=1-confidence,
        usevar="unequal"
    )

    
    # Ensidig nedre 95 % konfidensgräns
    ci_one_lower, ci_one_upper = comparison.tconfint_diff(
        alpha=1-confidence, usevar="unequal", alternative="larger"
    )
    
    
    # Cohen's d – standardiserad skillnad i medelvärde
    pooled_sd = np.sqrt(
        ((n_a - 1) * s_a**2 + (n_b - 1) * s_b**2)
        / (n_a + n_b - 2)
    )

    cohens_d = observed_skillnad / pooled_sd

    return {
        "mean_a": float(mean_a),
        "mean_b": float(mean_b),
        "observed_skillnad": float(observed_skillnad),
        "statistic": float(test_result.statistic),
        "pvalue": float(test_result.pvalue),
        "lower": float(ci_lower),
        "upper": float(ci_upper),
        "ci_one_lower": float(ci_one_lower),
        "ci_one_upper": float(ci_one_upper),
        "cohens_d": float(cohens_d),
        "n_a": n_a,
        "n_b": n_b
    }

def test_two_proportions(a, b, confidence=0.95):
    """
    Jämför två proportioner med z-test,
    konfidensintervall samt absolut och relativ lift.

    a: Referensgrupp (icke-rökare)
    b: Jämförelsegrupp (rökare)
    """

    # Rensa data
    a = _numeric(a)
    b = _numeric(b)

    if (
        min(len(a), len(b)) == 0
        or not np.isin(a, [0, 1]).all()
        or not np.isin(b, [0, 1]).all()
    ):
        raise ValueError("Två icke-tomma binära grupper krävs.")

    alpha = 1 - confidence

    # Antal observationer
    n_A = len(a)
    n_B = len(b)

    # Antal sjukdomsfall
    x_A = int(a.sum())
    x_B = int(b.sum())

    # Sjukdomsandel per grupp
    p_A = x_A / n_A
    p_B = x_B / n_B

    # Skillnad i sjukdomsandel
    diff = p_B - p_A

    # Absolut lift i procentenheter
    absolute_pp = diff * 100

    # Relativ lift i procent
    relative_lift = (
        (p_B / p_A - 1) * 100
        if p_A > 0 else np.nan
    )

    # Wilson-konfidensintervall för varje grupp
    ci_A = proportion_confint(
        x_A,
        n_A,
        alpha=alpha,
        method="wilson"
    )

    ci_B = proportion_confint(
        x_B,
        n_B,
        alpha=alpha,
        method="wilson"
    )

    # Newcombe-konfidensintervall för skillnaden
    diff_ci_low, diff_ci_high = confint_proportions_2indep(
        count1=x_B,
        nobs1=n_B,
        count2=x_A,
        nobs2=n_A,
        alpha=alpha,
        compare="diff",
        method="newcomb"
    )

    # Ensidigt z-test: Grupp B > Grupp A
    z_stat, p_one_sided = proportions_ztest(
        count=[x_B, x_A],
        nobs=[n_B, n_A],
        alternative="larger"
    )

    # Tvåsidigt z-test
    _, p_two_sided = proportions_ztest(
        count=[x_B, x_A],
        nobs=[n_B, n_A],
        alternative="two-sided"
    )

    return {
        "n_A": n_A,
        "n_B": n_B,
        "x_A": x_A,
        "x_B": x_B,
        "p_A": p_A,
        "p_B": p_B,
        "difference": diff,
        "absolute_pp": absolute_pp,
        "relative_lift": relative_lift,
        "ci_A": ci_A,
        "ci_B": ci_B,
        "lower": diff_ci_low,
        "upper": diff_ci_high,
        "statistic": z_stat,
        "p_one_sided": p_one_sided,
        "p_two_sided": p_two_sided
    }