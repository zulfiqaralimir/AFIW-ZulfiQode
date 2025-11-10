"""
Quick test for RiskAnalyzer
Run with: python test_risk_analyzer.py
"""
from app.agents.risk_analyzer import RiskAnalyzer

ra = RiskAnalyzer()

ratios = ra.compute_ratios({
    "total_debt": 500,
    "total_equity": 1000,
    "current_assets": 800,
    "current_liabilities": 600,
    "stock_prices": [95, 98, 100, 102, 105, 104, 107, 106]
})

risk = ra.compute_risk_score(ratios, ethical_bias=0.1)
econ = ra.econometric_baseline(ratios)
compare = ra.compare_models(risk["risk_score"], econ)

print("=" * 50)
print("Risk Analyzer Test Results")
print("=" * 50)
print("\n📊 Financial Ratios:")
print(ratios)
print("\n⚠️ Risk Score:")
print(risk)
print("\n📈 Econometric Baseline:")
print(f"Econometric Risk: {econ}")
print("\n🔍 Model Comparison:")
print(compare)
print("=" * 50)

