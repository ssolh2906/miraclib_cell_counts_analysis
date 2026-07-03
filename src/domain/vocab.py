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
    NAN = "NaN"


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
