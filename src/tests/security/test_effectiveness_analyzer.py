import pytest
import asyncio
from src.security.response.effectiveness_analyzer import EffectivenessAnalyzer

@pytest.mark.asyncio
async def test_effectiveness_analyzer_analyze_effectiveness():
    analyzer = EffectivenessAnalyzer()
    response = {
        "id": "response1",
        "type": "login_attempt",
        "steps": [
            {"id": "step1", "metrics": {}},
            {"id": "step2", "metrics": {}}
        ]
    }

    result = await analyzer.analyzeEffectiveness(response)

    assert "overallEffectiveness" in result
    assert "stepEffectiveness" in result
    assert "timelinessMetrics" in result
    assert "resourceEfficiency" in result
    assert "impactAssessment" in result

@pytest.mark.asyncio
async def test_effectiveness_analyzer_analyze_effectiveness_wrong_data():
    analyzer = EffectivenessAnalyzer()
    response = "wrong data"
    with pytest.raises(AttributeError):
        await analyzer.analyzeEffectiveness(response)