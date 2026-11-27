"""Analysklass som samordnar datakvalitet, statistik och regression."""
from .io_utils import load_data, validate_data, add_bmi, NUMERIC_COLUMNS
from .statistics import descriptive_statistics, correlation_matrix, disease_by_smoking, smoking_summary
from .statistical_tests import ci_mean_normal,ci_mean_bootstrap,test_two_means,test_two_proportions
from .regression import regression_analysis

class HealthAnalyzer:

    """Samlar dataset och återanvändbara analysmetoder."""
    
    def __init__(self,path):
        """Läser in hälsodata och beräknar BMI."""
        self.df=add_bmi(load_data(path))

    def quality(self):
        """Kontrollerar datasetets kvalitet."""
        return validate_data(self.df)

    def describe(self):
        """Visar beskrivande statistik för numeriska hälsovariabler."""
        return descriptive_statistics(self.df, NUMERIC_COLUMNS)
    
    def correlation(self):
        """Beräknar korrelationsmatrisen."""
        return correlation_matrix(self.df)
    
    def smoking_summary(self):
        """Beskrivande statistik för blodtryck efter rökstatus."""
        return smoking_summary(self.df)

    def disease_groups(self):
        """Beräkna sjukdomsandel per rökgrupp."""
        return disease_by_smoking(self.df)

    def bp_confidence_intervals(self,B=2000,seed=42):
        """Beräknar konfidensintervall med normalapproximation och bootstrap."""
        bp=self.df['systolic_bp'].dropna()
        return ci_mean_normal(bp),ci_mean_bootstrap(bp,B=B,seed=seed)
    
    def smoking_bp_test(self):
           return test_two_means(
           self.df.loc[self.df["smoker"] == "Yes", "systolic_bp"],
           self.df.loc[self.df["smoker"] == "No", "systolic_bp"],
           alternative="greater"
       )
    
    def smoking_disease_test(self, confidence=0.95):
        """Jämför sjukdomsandel mellan rökare och icke-rökare."""

        non_smokers = self.df.loc[self.df["smoker"] == "No", "disease"]
        smokers = self.df.loc[self.df["smoker"] == "Yes", "disease"]

        return test_two_proportions(
            non_smokers,
            smokers,
            confidence=confidence
        )
   
    def regression(self,features,target="systolic_bp",test_size=0.2,seed=42):
        
        """Utför enkel eller multipel linjär regression."""

        return regression_analysis(
            self.df,
            features=features,
            target=target,
            test_size=test_size,
            seed=seed
        )