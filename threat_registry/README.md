# Threat Subject Registry

Consolidated, person-level registry built from four source lists:

| Source code | File | Records | Demographics? |
|---|---|---|---|
| `ALL_INC` | ALL_INC.csv | Incident reports | No race/gender |
| `ALL_INV` | ALL_INV.csv | Investigations | Race/Gender/Age |
| `THREAT_LIST` | THREAT_LIST.csv | Threat list | R/G/A code |
| `ALL_BOLO` | ALL_BOLO.csv | BOLOs | No race/gender |

## Design (Option A — person-level)

- **One row per person.** Names that were packed into multi-line cells in the
  source have been split out so each individual is a discrete record.
- **Vehicles are NOT positionally guessed onto people.** A vehicle is attached
  to a person row **only** when that source record contains exactly one person
  AND exactly one vehicle (an unambiguous 1:1). All other vehicles live in the
  `vehicles.csv` table, linked by `Record_ID`, so nothing falsely asserts that
  a given person owned a given car.
- **Demographics**: the `R/G/A` code (e.g. `WMA` = White / Male / Adult) from
  `THREAT_LIST`, and the Race/Gender/Age columns from `ALL_INV`, are parsed into
  discrete `Race`, `Gender`, `Age` columns. `ALL_INC` and `ALL_BOLO` carry no
  race/gender, so those cells are intentionally blank for those rows.

## Files

| File | What it is |
|---|---|
| `registry_people.csv` | Person-level registry (the main table) |
| `vehicles.csv` | Every vehicle from every source, linked by `Record_ID` |
| `people_*.csv` | Per-source person extracts (audit trail) |
| `.github/workflows/build-threat-registry.yml` | Builds `THREAT_REGISTRY.xlsx` on GitHub's servers |

## Getting the Excel workbook (no local setup)

1. Go to the repo's **Actions** tab.
2. Open the **Build Threat Registry** workflow run (it runs automatically on
   push to the `threat-registry` branch, or trigger it manually with **Run
   workflow**).
3. Download the **THREAT_REGISTRY** artifact (a zip containing
   `THREAT_REGISTRY.xlsx`).

The workbook has four tabs: `Threat_Registry`, `Vehicles`, `Subject_Summary`,
`Pivot`.

## Column reference (`registry_people.csv`)

`Subject_ID, First, Middle, Last, Full_Name, DOB, Race, Gender, Age, Location,
Record_Date, Incident_Type, Case_Number, Source, Source_Ref, Vehicle_Make,
Vehicle_Model, Vehicle_Color, Vehicle_Year, Plate, Plate_State, VIN`

`DOB` is normalized to `YYYY-MM-DD` where a parseable date existed in the
source; otherwise left blank.
