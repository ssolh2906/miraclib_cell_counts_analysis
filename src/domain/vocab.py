"""
Controlled vocabulary for the miraclib cell-count dataset.
"""

from enum import StrEnum


class Sex(StrEnum):
    M = "M"
    F = "F"


class Condition(StrEnum):
    MELANOMA = "melanoma"
    CARCINOMA = "carcinoma"
    HEALTHY = "healthy"


class Treatment(StrEnum):
    MIRACLIB = "miraclib"
    PHAUXIMAB = "phauximab"
    NONE = "none"


class Response(StrEnum):
    YES = "yes"
    NO = "no"


class SampleType(StrEnum):
    PBMC = "PBMC"
    WB = "WB"


class Population(StrEnum):
    B_CELL = "b_cell"
    CD8_T = "cd8_t_cell"
    CD4_T = "cd4_t_cell"
    NK = "nk_cell"
    MONOCYTE = "monocyte"


# time_from_treatment_start value marking the pre-treatment (predictive) sample.
BASELINE = 0

# The five count columns in the wide CSV, in canonical order.
# Used by the loader to melt wide -> long and to seed the populations table.
POPULATION_COLUMNS = [p.value for p in Population]

# Canonical color per population (dataviz palette slots 1-5, in POPULATION_COLUMNS order).
# Single source of truth for BOTH the pipeline plots (src/ui) and the dashboard.
_POPULATION_PALETTE = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#008300"]
POPULATION_COLORS = dict(zip(POPULATION_COLUMNS, _POPULATION_PALETTE))


def order_populations(values) -> list[str]:
    """Return the given populations in canonical order (unknown ones appended, stable)."""
    present = set(values)
    known = [p for p in POPULATION_COLUMNS if p in present]
    extra = [v for v in dict.fromkeys(values) if v not in POPULATION_COLUMNS]
    return known + extra
