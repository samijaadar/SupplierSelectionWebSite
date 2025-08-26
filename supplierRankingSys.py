import json
import random
import time

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.neural_network import MLPRegressor
import streamlit as st

import pdfGenerator
from mailSender import send_email
from genAi import generate_perturbation
from rankingUtils import compare_supplier_rankings, calculate_fr


class SupplierRankingSystem:
    def __init__(self, beneficial_criteria, non_beneficial_criteria, weights, models=None):
        self.beneficial_criteria = set(beneficial_criteria)
        self.non_beneficial_criteria = set(non_beneficial_criteria)
        self.weights = weights
        self.scaler = StandardScaler()
        self.models = models or {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'xgboost': XGBRegressor(random_state=42),
            #'neural_net': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=10000, random_state=42)
        }

    def prepare_data(self, df):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X_scaled = self.scaler.fit_transform(df[numeric_cols])
        return pd.DataFrame(X_scaled, columns=numeric_cols), numeric_cols

    def train_models(self, X, y):
        predictions = [model.fit(X, y).predict(X) for model in self.models.values()]
        return np.mean(predictions, axis=0)

    def generate_rankings(self, df):
        X_scaled, numeric_cols = self.prepare_data(df)
        results = pd.DataFrame({'Supplier': df['Fournisseur'].unique()})

        for col in numeric_cols:
            if col not in self.beneficial_criteria and col not in self.non_beneficial_criteria:
                continue  # Skip unclassified columns

            X = X_scaled.drop(columns=[col])
            y = df[col]
            preds = self.train_models(X, y)

            ascending = col in self.non_beneficial_criteria
            ranks = pd.Series(preds).rank(method='min', ascending=ascending)
            results[col] = ranks.astype(int)

        valid_weights = {k: v for k, v in self.weights.items() if k in results.columns}
        total_weight = sum(valid_weights.values())
        if total_weight == 0:
            st.error("Weights sum to zero. Please assign weights.")
            return pd.DataFrame()
        normalized_weights = {k: v / total_weight for k, v in valid_weights.items()}

        results['Score'] = sum(results[col] * weight for col, weight in normalized_weights.items())

        return results.sort_values('Score').reset_index(drop=True)

    def analyze_individual_supplier_perturbations(self, original_df, original_rankings, perturbation_data):
        all_comparisons = []

        # Pre-cast once for efficiency
        numeric_columns = list(perturbation_data.keys())
        original_df[numeric_columns] = original_df[numeric_columns].astype(float)

        i=0
        for supplier in original_df['Fournisseur'].unique():
            df_perturbed = original_df.copy()
            supplier_mask = df_perturbed['Fournisseur'] == supplier
            i += 1
            print(i)
            for column, factor in perturbation_data.items():
                if column in self.beneficial_criteria:
                    df_perturbed.loc[supplier_mask, column] *= (1 - factor)
                elif column in self.non_beneficial_criteria:
                    df_perturbed.loc[supplier_mask, column] *= (1 + factor)

            perturbed_rankings = self.generate_rankings(df_perturbed)
            comparison = compare_supplier_rankings(original_rankings, perturbed_rankings)
            all_comparisons.append(comparison[comparison['Supplier'] == supplier])

        return pd.concat(all_comparisons, ignore_index=True).sort_values('Rank_Change', ascending=False)

    def rank(self, df, company, mail):
        time.sleep(20)
        try:
                report_file = f'report_{company}.pdf'
                pdfGenerator.generate_report(df, "resp" , df, report_file)
                perturbation_results_file = f'perturbation_results_{company}.csv'
                initial_ranking_results_file = f'initial_ranking_results_{company}.csv'
                df.to_csv(perturbation_results_file, index=False)
                df.to_csv(initial_ranking_results_file, index=False)
                send_email(mail, [perturbation_results_file, initial_ranking_results_file,report_file])
                return df, "test" , df
        except Exception as e:
            print(f"Error during processing: {e}")
