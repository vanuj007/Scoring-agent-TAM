import pytest

from app.models import CompanyType, FundingStatus, Geography, RevenueBand, TamScoreRequest
from app.scoring import category_for_score, score_employee_count, score_tam


def test_core_tam_top_score():
    request = TamScoreRequest(
        company_type=CompanyType.startup,
        employee_count=500,
        funding_status=FundingStatus.vc_backed,
        revenue_band=RevenueBand.band_1m_100m,
        geography=Geography.global_remote,
    )
    result = score_tam(request)
    assert result.tam_score == 20 + 25 + 20 + 15 + 20
    assert result.tam_score == 100
    assert result.tam_decision == "Yes"
    assert result.tam_category == "Core TAM"
    assert len(result.reason_codes) == 5


def test_not_tam_low_score():
    request = TamScoreRequest(
        company_type=CompanyType.traditional_enterprise,
        employee_count=50000,
        funding_status=FundingStatus.unknown,
        revenue_band=RevenueBand.unknown,
        geography=Geography.other,
    )
    result = score_tam(request)
    assert result.tam_score == 5 + 5 + 8 + 8 + 12
    assert result.tam_decision == "No"
    assert result.tam_category == "Not TAM"


def test_missing_revenue_band_defaults_to_unknown():
    request = TamScoreRequest(
        company_type=CompanyType.scale_up,
        employee_count=200,
        funding_status=FundingStatus.vc_backed,
        geography=Geography.us,
    )
    result = score_tam(request)
    assert result.tam_score == 20 + 25 + 20 + 8 + 18


@pytest.mark.parametrize(
    "count,expected",
    [
        (0, 8),
        (9, 8),
        (10, 25),
        (1000, 25),
        (1001, 18),
        (3000, 18),
        (3001, 10),
        (10000, 10),
        (10001, 5),
    ],
)
def test_score_employee_count_boundaries(count, expected):
    assert score_employee_count(count) == expected


@pytest.mark.parametrize(
    "score,expected",
    [
        (100, "Core TAM"),
        (90, "Core TAM"),
        (89, "Qualified TAM"),
        (75, "Qualified TAM"),
        (74, "Peripheral TAM"),
        (60, "Peripheral TAM"),
        (59, "Not TAM"),
        (0, "Not TAM"),
    ],
)
def test_category_boundaries(score, expected):
    assert category_for_score(score) == expected


def test_decision_threshold():
    request = TamScoreRequest(
        company_type=CompanyType.public_tech,
        employee_count=15000,
        funding_status=FundingStatus.public,
        revenue_band=RevenueBand.over_100m,
        geography=Geography.other,
    )
    result = score_tam(request)
    assert result.tam_score == 10 + 5 + 10 + 10 + 12
    assert result.tam_score < 60
    assert result.tam_decision == "No"
