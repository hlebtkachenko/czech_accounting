"""Czech statutory tax depreciation (daňové odpisy) — Act 586/1992 Sb.

§ 31 rovnoměrné (linear, year-1 rate differs from year-2+) and § 32 zrychlené (accelerated,
k1/k2 coefficients). Rates and coefficients are from Annex 1 + § 31/§ 32 as in force for 2026.
These amounts are what the CZ-Daňové odpisy Finance Book must post; they differ from účetní
(accounting) depreciation and from ERPNext's straight-line default. Technické zhodnocení (TI)
and přerušení (suspension) are not modelled yet — the first depreciation of an un-improved asset.

Pure functions, no Frappe dependency, so they are unit-testable in isolation.
"""
import math

# Minimum depreciation period (years) per odpisová skupina (Annex 1, § 30).
MIN_PERIOD_YEARS = {1: 3, 2: 5, 3: 10, 4: 20, 5: 30, 6: 50}

# § 31 rovnoměrné: (year-1 rate %, year-2+ rate %). Rates sum to 100% over the min period.
LINEAR_RATES = {
    1: (20.0, 40.0),
    2: (11.0, 22.25),
    3: (5.5, 10.5),
    4: (2.15, 5.15),
    5: (1.4, 3.4),
    6: (1.02, 2.02),
}

# § 32 zrychlené: (k1 year-1 coefficient, k2 year-2+ coefficient).
ACCELERATED_COEFFICIENTS = {
    1: (3, 4),
    2: (5, 6),
    3: (10, 11),
    4: (20, 21),
    5: (30, 31),
    6: (50, 51),
}

LINEAR = "linear"
ACCELERATED = "accelerated"


def _round_up(amount):
    """§ 31 odst. 1 / § 32: tax depreciation is rounded up to whole crowns."""
    return float(math.ceil(round(amount, 6)))


def _cap_to_cost(amounts, cost):
    """Rounding up can overshoot in the last year; clip so the schedule sums to exactly the cost."""
    total = 0.0
    capped = []
    for amount in amounts:
        amount = min(amount, cost - total)
        capped.append(amount)
        total += amount
    return capped


def linear_schedule(cost, group):
    """§ 31 rovnoměrné annual amounts: year 1 at the lower rate, years 2+ at the higher rate."""
    rate1, rate2 = LINEAR_RATES[group]
    years = MIN_PERIOD_YEARS[group]
    amounts = [_round_up(cost * rate1 / 100)]
    amounts += [_round_up(cost * rate2 / 100) for _ in range(years - 1)]
    return _cap_to_cost(amounts, cost)


def accelerated_schedule(cost, group):
    """§ 32 zrychlené annual amounts: year 1 = cost / k1; year n = 2 * ZC / (k2 - (n - 1))."""
    k1, k2 = ACCELERATED_COEFFICIENTS[group]
    years = MIN_PERIOD_YEARS[group]
    first = _round_up(cost / k1)
    amounts = [first]
    residual = cost - first
    for n in range(2, years + 1):
        amount = _round_up(2 * residual / (k2 - (n - 1)))
        amounts.append(amount)
        residual -= amount
    return _cap_to_cost(amounts, cost)


def tax_depreciation_schedule(cost, group, method):
    """Annual daňové odpisy amounts for one asset. method is LINEAR (§ 31) or ACCELERATED (§ 32)."""
    if group not in MIN_PERIOD_YEARS:
        raise ValueError(f"unknown depreciation group: {group!r}")
    if method == LINEAR:
        return linear_schedule(cost, group)
    if method == ACCELERATED:
        return accelerated_schedule(cost, group)
    raise ValueError(f"unknown tax depreciation method: {method!r} (use {LINEAR!r} or {ACCELERATED!r})")
