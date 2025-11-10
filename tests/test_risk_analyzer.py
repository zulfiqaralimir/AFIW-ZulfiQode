"""
Test suite for RiskAnalyzer
Run with: pytest tests/test_risk_analyzer.py -v
"""
from app.agents.risk_analyzer import RiskAnalyzer


def test_risk_analyzer_basic():
    """Test basic RiskAnalyzer functionality"""
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

    # Assertions
    assert 0 <= risk["risk_score"] <= 1
    assert "category" in risk
    assert isinstance(compare["bias"], float)


def test_risk_analyzer_ratios():
    """Test ratio calculations"""
    ra = RiskAnalyzer()
    
    ratios = ra.compute_ratios({
        "total_debt": 1000,
        "total_equity": 2000,
        "current_assets": 1500,
        "current_liabilities": 1000,
        "stock_prices": [100, 105, 110, 108, 112]
    })
    
    assert "debt_equity" in ratios
    assert "current_ratio" in ratios
    assert "volatility" in ratios
    assert ratios["debt_equity"] == 0.5
    assert ratios["current_ratio"] == 1.5


def test_risk_analyzer_risk_categories():
    """Test risk score categories"""
    ra = RiskAnalyzer()
    
    # High risk scenario
    high_risk_ratios = {"debt_equity": 2.0, "current_ratio": 0.5, "volatility": 0.5}
    high_risk = ra.compute_risk_score(high_risk_ratios, ethical_bias=0.5)
    assert high_risk["risk_score"] > 0.7 or "High Risk" in high_risk["category"]
    
    # Low risk scenario
    low_risk_ratios = {"debt_equity": 0.2, "current_ratio": 2.0, "volatility": 0.1}
    low_risk = ra.compute_risk_score(low_risk_ratios, ethical_bias=0.0)
    assert low_risk["risk_score"] < 0.4 or "Low Risk" in low_risk["category"]


def test_risk_analyzer_model_comparison():
    """Test LLM vs econometric model comparison"""
    ra = RiskAnalyzer()
    
    ratios = {"debt_equity": 1.0, "current_ratio": 1.0, "volatility": 0.2}
    llm_score = 0.6
    econ_score = 0.5
    
    compare = ra.compare_models(llm_score, econ_score)
    
    assert "llm_score" in compare
    assert "econ_score" in compare
    assert "bias" in compare
    assert "variance" in compare
    assert "hallucination_flag" in compare
    assert isinstance(compare["hallucination_flag"], bool)


def test_risk_analyzer_econometric_baseline():
    """Test econometric baseline calculation"""
    ra = RiskAnalyzer()
    
    ratios = {"debt_equity": 1.5, "current_ratio": 1.2, "volatility": 0.3}
    econ_score = ra.econometric_baseline(ratios)
    
    assert isinstance(econ_score, float)
    assert 0 <= econ_score <= 2  # Reasonable range for econometric score

