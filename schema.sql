-- schema.sql — miraclib cell-count analysis (Part 1)
-- SQLite. Normalized 3NF, 5 tables:
--   projects (1) --< subjects (1) --< samples (1) --< cell_counts >-- (1) populations
--
-- Design decisions (rationale in README):
--   1. All IDs are TEXT — source values are 'prj1', 'sbj000', 'sample00000' (not integers).
--   2. cell_counts is LONG format — population is a row, not a column.
--      Adding a new population needs no schema change.
--   3. Raw counts only. Percentages (Part 2) are derived via the cell_frequencies VIEW
--      (single source of truth — never store computed frequencies).
--   4. response is nullable TEXT — 'yes'/'no'/NULL for healthy/none.
--   5. CHECK constraints enforce controlled vocabulary; population is enforced by FK.
--   6. Indexes on every FK column for scale (thousands of samples, hundreds of projects).

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- projects
-- ---------------------------------------------------------------------------
CREATE TABLE projects (
    project_id  TEXT PRIMARY KEY,           -- natural key: 'prj1'
    name        TEXT
);

-- ---------------------------------------------------------------------------
-- subjects (one biological subject / patient)
-- ---------------------------------------------------------------------------
CREATE TABLE subjects (
    subject_id  TEXT PRIMARY KEY,           -- 'sbj000'
    project_id  TEXT NOT NULL,
    condition   TEXT NOT NULL CHECK (condition IN ('melanoma', 'carcinoma', 'healthy')),
    age         INTEGER,
    sex         TEXT CHECK (sex IN ('M', 'F')),
    treatment   TEXT CHECK (treatment IN ('miraclib', 'phauximab', 'none')),
    response    TEXT CHECK (response IN ('yes', 'no')),   -- nullable: NULL for healthy / none
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
);

-- ---------------------------------------------------------------------------
-- samples (one biological sample; a subject has up to 3 timepoints)
-- ---------------------------------------------------------------------------
CREATE TABLE samples (
    sample_id                  TEXT PRIMARY KEY,   -- 'sample00000'
    subject_id                 TEXT NOT NULL,
    sample_type                TEXT CHECK (sample_type IN ('PBMC', 'WB')),
    time_from_treatment_start  INTEGER CHECK (time_from_treatment_start IN (0, 7, 14)),
    FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
);

-- ---------------------------------------------------------------------------
-- populations (controlled vocabulary of cell types)
-- ---------------------------------------------------------------------------
CREATE TABLE populations (
    population  TEXT PRIMARY KEY            -- 'b_cell', 'cd8_t_cell', ...
);

-- ---------------------------------------------------------------------------
-- cell_counts (LONG format; raw counts only)
-- ---------------------------------------------------------------------------
CREATE TABLE cell_counts (
    sample_id   TEXT NOT NULL,
    population  TEXT NOT NULL,
    cell_count  INTEGER NOT NULL CHECK (cell_count >= 0),
    PRIMARY KEY (sample_id, population),     -- composite PK
    FOREIGN KEY (sample_id)  REFERENCES samples (sample_id),
    FOREIGN KEY (population)  REFERENCES populations (population)
);

-- ---------------------------------------------------------------------------
-- Indexes on FK columns (scale)
-- ---------------------------------------------------------------------------
CREATE INDEX idx_subjects_project    ON subjects   (project_id);
CREATE INDEX idx_samples_subject     ON samples    (subject_id);
CREATE INDEX idx_cell_counts_sample  ON cell_counts (sample_id);
CREATE INDEX idx_cell_counts_pop     ON cell_counts (population);

-- ---------------------------------------------------------------------------
-- VIEW: cell_frequencies (Part 2) — relative frequency per sample.
-- Percentage = population count / total count of that sample * 100.
-- Derived, not stored: single source of truth.
-- ---------------------------------------------------------------------------
CREATE VIEW cell_frequencies AS
SELECT
    cc.sample_id,
    cc.population,
    cc.cell_count,
    tot.total_count,
    ROUND(100.0 * cc.cell_count / tot.total_count, 4) AS percentage
FROM cell_counts cc
JOIN (
    SELECT sample_id, SUM(cell_count) AS total_count
    FROM cell_counts
    GROUP BY sample_id
) tot ON cc.sample_id = tot.sample_id;
