from prisma.quality.mmat import (
    QualityLevel,
    Score,
    assess_text,
    quality_level,
    score_to_num,
)

HIGH_QUALITY_TEXT = """
Abstract. The aim of this study is to forecast retail sales using Google
Trends. We collected weekly data from 2010 to 2022 (n = 624 observations).
This study employs an ARIMA-X regression with train/test split. Independent
variables include search volume; dependent variable is sales. Results
section shows that the coefficient on search volume is statistically
significant (p < 0.001), R² = 0.84. Our findings suggest that digital
signals improve forecast accuracy. Limitations: small geographic scope.
"""


LOW_QUALITY_TEXT = "A short note. No data, no method, no results."


def test_score_helpers():
    assert score_to_num(Score.YES) == 1.0
    assert score_to_num(Score.CANT_TELL) == 0.5
    assert score_to_num(Score.NO) == 0.0
    assert quality_level(5.0) == QualityLevel.HIGH
    assert quality_level(3.5) == QualityLevel.MEDIUM
    assert quality_level(1.0) == QualityLevel.LOW


def test_assess_high_quality():
    a = assess_text("doc-1", HIGH_QUALITY_TEXT)
    assert a.total >= 4.0
    assert a.level in {QualityLevel.HIGH, QualityLevel.MEDIUM}
    assert all(code in a.scores for code in ("Q1", "Q2", "Q3", "Q4", "Q5"))


def test_assess_low_quality():
    a = assess_text("doc-2", LOW_QUALITY_TEXT)
    assert a.total <= 2.5
    assert a.level == QualityLevel.LOW
