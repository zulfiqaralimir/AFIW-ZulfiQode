# app/agents/risk_analyzer.py
import pandas as pd
import numpy as np
from typing import Dict


class RiskAnalyzer:
    """
    Computes financial and ethical risk indicators using quantitative ratios.
    This bridges LLM qualitative judgments with numeric risk analysis.
    """

    def __init__(self):
        # Weight constants — can be tuned later
        self.alpha = 0.4   # credit risk weight
        self.beta = 0.35   # liquidity risk weight
        self.gamma = 0.25  # volatility weight

    # -----------------------------
    # ---- Ratio Calculations -----
    # -----------------------------
    def compute_ratios(self, data: Dict) -> Dict:
        """
        Compute key ratios given a financial data dictionary.
        Expected keys: total_debt, total_equity, current_assets,
                       current_liabilities, stock_prices (list)
        """

        debt = data.get("total_debt", 0)
        equity = data.get("total_equity", 1)  # avoid div/0
        assets = data.get("current_assets", 1)
        liabilities = data.get("current_liabilities", 1)
        prices = data.get("stock_prices", [])

        # Credit ratio
        debt_equity = round(debt / equity, 2)

        # Liquidity ratio
        current_ratio = round(assets / liabilities, 2)

        # Volatility (std. dev. of price changes)
        volatility = round(np.std(prices[-30:]) if len(prices) > 1 else 0, 3)

        return {
            "debt_equity": debt_equity,
            "current_ratio": current_ratio,
            "volatility": volatility,
        }

    # --------------------------------------
    # ---- Composite Risk Score ------------
    # --------------------------------------
    def compute_risk_score(self, ratios: Dict, ethical_bias: float = 0.0) -> Dict:
        """
        Combine ratios and ethical bias into overall risk index.
        Range: 0 (low risk) → 1 (high risk)
        """

        risk_index = (
            self.alpha * ratios["debt_equity"]
            - self.beta * ratios["current_ratio"]
            + self.gamma * ratios["volatility"]
            + (ethical_bias * 0.1)
        )

        risk_score = min(max(round(risk_index, 3), 0), 1)
        label = (
            "⚠️ High Risk"
            if risk_score > 0.7
            else "🟡 Moderate Risk"
            if risk_score > 0.4
            else "🟢 Low Risk"
        )

        return {
            "credit_risk": ratios["debt_equity"],
            "liquidity_ratio": ratios["current_ratio"],
            "volatility": ratios["volatility"],
            "ethical_bias": ethical_bias,
            "risk_score": risk_score,
            "category": label,
        }

    # --------------------------------------
    # ---- Econometric Model Mock ----------
    # --------------------------------------
    def econometric_baseline(self, ratios: Dict) -> float:
        """
        Simulate an econometric model baseline for comparison (e.g., GARCH, ARIMA output).
        """
        econ_risk = (
            0.5 * ratios["debt_equity"]
            - 0.3 * ratios["current_ratio"]
            + 0.2 * ratios["volatility"]
        )
        return round(econ_risk, 3)

    # --------------------------------------
    # ---- LLM vs Econometric Comparison ---
    # --------------------------------------
    def compare_models(self, llm_score: float, econ_score: float) -> Dict:
        """
        Produce bias, variance, and hallucination stats between models.
        """
        diff = llm_score - econ_score
        bias = round(diff, 3)
        variance = round(diff ** 2, 3)
        hallucination_prob = abs(diff) > 0.2

        return {
            "llm_score": llm_score,
            "econ_score": econ_score,
            "bias": bias,
            "variance": variance,
            "hallucination_flag": hallucination_prob,
        }

