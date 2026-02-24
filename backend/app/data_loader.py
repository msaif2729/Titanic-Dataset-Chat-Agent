import pandas as pd
from pathlib import Path

#Global DF variable (cached)
_df = None

def load_data():
    global _df

    if _df is not None:
        return _df
    
    #Get Dataset Path
    data_path = Path(__file__).resolve().parent.parent / "titanic.csv"

    df = pd.read_csv(data_path)

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Handle missing values

    # Age → fill with median
    if "Age" in df.columns:
        df["Age"] = df["Age"].fillna(df["Age"].median())

    # Fare → fill with median
    if "Fare" in df.columns:
        df["Fare"] = df["Fare"].fillna(df["Fare"].median())

    # Embarked → fill with mode
    if "Embarked" in df.columns:
        df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Cabin → too many missing values → fill with "Unknown"
    if "Cabin" in df.columns:
        df["Cabin"] = df["Cabin"].fillna("Unknown")

    # Convert categorical columns to string
    categorical_cols = ["Sex", "Embarked", "Cabin", "Ticket", "Name"]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Ensure numeric columns are numeric
    numeric_cols = ["Age", "Fare", "SibSp", "Parch", "Pclass", "Survived"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    _df = df
    return _df


def get_dataframe():
    return load_data()
