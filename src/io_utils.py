"""Inläsning och datakvalitet."""
from pathlib import Path
import pandas as pd
import numpy as np

REQUIRED = ['age','sex','weight','height','systolic_bp','cholesterol','smoker','disease']

NUMERIC_COLUMNS = [
    "age",
    "weight",
    "height",
    "systolic_bp",
    "cholesterol"
]
def load_data(path):
    """Läs CSV och säkerställ att de nödvändiga kolumnerna finns."""
    path=Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset saknas: {path}. Lägg originalfilen i data/.")
    df=pd.read_csv(path)
    missing=set(REQUIRED)-set(df.columns)
    if missing: raise ValueError(f"Kolumner saknas: {sorted(missing)}")
    return df

def validate_data(df):
    """Sammanställ kvalitetsproblem utan att ändra originaldata."""
    invalid={col:int((pd.to_numeric(df[col],errors='coerce')<=0).sum()) for col in  NUMERIC_COLUMNS}
    invalid['disease (ej 0/1)']=int((~df['disease'].isin([0,1])).sum())
    invalid['smoker (ej Yes/No)']=int((~df['smoker'].isin(['Yes','No'])).sum())
    return {
        "antal_rader": len(df),
        "antal_kolumner": len(df.columns),
        "saknade": df.isna().sum(),
        "dubbletter": int(df.duplicated().sum()),
        "ogiltiga": pd.Series(invalid)
    }

def add_bmi(df):
    """Beräkna BMI från vikt i kg och längd i meter; originalet påverkas inte."""
    result=df.copy()
    height=pd.to_numeric(result['height'],errors='coerce')
    # Datasetet använder meter eller centimeter; välj utifrån observerad skala.
    height_m=height.where(height<=3,height/100)
    result['bmi']=pd.to_numeric(result['weight'],errors='coerce')/height_m.where(height_m>0)**2
    return result