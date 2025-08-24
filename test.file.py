import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.neural_network import MLPRegressor
import time

import pdfGenerator
from suppSelectionRankModule.supplierRankingSys import SupplierRankingSystem

pd.set_option('display.max_columns', None)
# Constants
# BENEFICIAL_CRITERIA (Higher is better)

BENEFICIAL_CRITERIA = [
    'Annual Revenue (USD)',
    'Quality',
    'Production Capacity',
    'Reliability',
]

# NON_BENEFICIAL_CRITERIA (Lower is better)
NON_BENEFICIAL_CRITERIA = [
    'Debt-to-Equity Ratio',
    'Cost',
    'Delivery Time',
    'Track Record in Labor Relations',
]

# Weights (0.1 for each criterion)
weights = {
    'Annual Revenue (USD)' : 10,
    'Quality' : 10,
    'Production Capacity' : 10,
    'Reliability' : 10,
    'Debt-to-Equity Ratio' : 10,
    'Cost' : 10,
    'Delivery Time' : 10,
    'Track Record in Labor Relations' : 10,
}

def main():
    """Main execution function."""
    start_time = time.time()
    # Load sample data
    df = pd.read_csv("suppliers_data.csv")
    df.rename(columns={"Supplier": "Fournisseur"}, inplace=True)
    # Create ranking system and generate rankings

    system = SupplierRankingSystem(BENEFICIAL_CRITERIA, NON_BENEFICIAL_CRITERIA, weights)
    rankings_df = system.generate_rankings(df)

    pdfGenerator.generate_report(rankings_df,None,None)

if __name__ == "__main__":
    main()