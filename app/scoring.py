from app.models import CompanyType, FundingStatus, Geography, RevenueBand, TamScoreRequest, TamScoreResponse

COMPANY_TYPE_SCORES: dict[CompanyType, int] = {
    CompanyType.startup: 20,
    CompanyType.scale_up: 20,
    CompanyType.pe_backed_growth: 15,
    CompanyType.public_tech: 10,
    CompanyType.traditional_enterprise: 5,
}

FUNDING_STATUS_SCORES: dict[FundingStatus, int] = {
    FundingStatus.vc_backed: 20,
    FundingStatus.bootstrapped: 18,
    FundingStatus.pe_backed: 15,
    FundingStatus.public: 10,
    FundingStatus.unknown: 8,
}

REVENUE_BAND_SCORES: dict[RevenueBand, int] = {
    RevenueBand.band_1m_100m: 15,
    RevenueBand.under_1m: 12,
    RevenueBand.over_100m: 10,
    RevenueBand.unknown: 8,
}

GEOGRAPHY_SCORES: dict[Geography, int] = {
    Geography.global_remote: 20,
    Geography.us: 18,
    Geography.europe: 18,
    Geography.india: 18,
    Geography.sea_middle_east: 15,
    Geography.other: 12,
}

REASON_CODES = {
    "company_type": {
        CompanyType.startup: "Startup company type",
        CompanyType.scale_up: "Scale-up company type",
        CompanyType.pe_backed_growth: "PE-backed growth company",
        CompanyType.public_tech: "Public tech company",
        CompanyType.traditional_enterprise: "Traditional enterprise",
    },
    "funding_status": {
        FundingStatus.vc_backed: "VC-backed company",
        FundingStatus.bootstrapped: "Bootstrapped company",
        FundingStatus.pe_backed: "PE-backed company",
        FundingStatus.public: "Publicly traded company",
        FundingStatus.unknown: "Unknown funding status",
    },
    "revenue_band": {
        RevenueBand.band_1m_100m: "Revenue within $1M-$100M target band",
        RevenueBand.under_1m: "Revenue under $1M",
        RevenueBand.over_100m: "Revenue over $100M",
        RevenueBand.unknown: "Unknown revenue band",
    },
    "geography": {
        Geography.global_remote: "Operates globally / remote hiring",
        Geography.us: "Operates in US",
        Geography.europe: "Operates in Europe",
        Geography.india: "Operates in India",
        Geography.sea_middle_east: "Operates in SEA / Middle East",
        Geography.other: "Operates in other geography",
    },
}


def score_employee_count(employee_count: int) -> int:
    if employee_count < 10:
        return 8
    if employee_count <= 1000:
        return 25
    if employee_count <= 3000:
        return 18
    if employee_count <= 10000:
        return 10
    return 5


def _employee_reason(employee_count: int) -> str:
    if employee_count < 10:
        return "Employee count under 10"
    if employee_count <= 1000:
        return "Employee count within target range (10-1000)"
    if employee_count <= 3000:
        return "Employee count 1001-3000"
    if employee_count <= 10000:
        return "Employee count 3001-10000"
    return "Employee count over 10000"


def category_for_score(score: int) -> str:
    if score >= 90:
        return "Core TAM"
    if score >= 75:
        return "Qualified TAM"
    if score >= 60:
        return "Peripheral TAM"
    return "Not TAM"


def score_tam(request: TamScoreRequest) -> TamScoreResponse:
    revenue_band = request.revenue_band or RevenueBand.unknown

    company_type_score = COMPANY_TYPE_SCORES[request.company_type]
    employee_score = score_employee_count(request.employee_count)
    funding_score = FUNDING_STATUS_SCORES[request.funding_status]
    revenue_score = REVENUE_BAND_SCORES[revenue_band]
    geography_score = GEOGRAPHY_SCORES[request.geography]

    total = company_type_score + employee_score + funding_score + revenue_score + geography_score
    decision = "Yes" if total >= 60 else "No"
    category = category_for_score(total)

    reason_codes = [
        REASON_CODES["company_type"][request.company_type],
        _employee_reason(request.employee_count),
        REASON_CODES["funding_status"][request.funding_status],
        REASON_CODES["revenue_band"][revenue_band],
        REASON_CODES["geography"][request.geography],
    ]

    return TamScoreResponse(
        tam_score=total,
        tam_decision=decision,
        tam_category=category,
        reason_codes=reason_codes,
    )
