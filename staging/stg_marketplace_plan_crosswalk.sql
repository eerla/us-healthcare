-- Staging: Marketplace Plan ID Crosswalk
-- One row per plan crosswalk between years
-- Source: CMS Marketplace Plan ID Crosswalk PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_plan_crosswalk AS
SELECT
    "State" AS state,
    "DentalPlan"::BOOLEAN AS dental_plan,
    "PlanID_2025" AS plan_id_2025,
    "IssuerID_2025" AS issuer_id_2025,
    "MultistatePlan_2025"::BOOLEAN AS multistate_plan_2025,
    "MetalLevel_2025" AS metal_level_2025,
    "ChildAdultOnly_2025" AS child_adult_only_2025,
    "FIPSCode" AS fips_code,
    "ZipCode" AS zip_code,
    "CrosswalkLevel" AS crosswalk_level,
    "ReasonForCrosswalk" AS reason_for_crosswalk,
    "PlanID_2026" AS plan_id_2026,
    "IssuerID_2026" AS issuer_id_2026,
    "MultistatePlan_2026" = 'X' AS multistate_plan_2026,
    "MetalLevel_2026" AS metal_level_2026,
    "ChildAdultOnly_2026" AS child_adult_only_2026,
    "AgeOffPlanID_2026" AS age_off_plan_id_2026,
    "IssuerID_AgeOff2026" AS issuer_id_age_off_2026,
    "MultistatePlan_AgeOff2026" = 'X' AS multistate_plan_age_off_2026,
    "MetalLevel_AgeOff2026" AS metal_level_age_off_2026,
    "ChildAdultOnly_AgeOff2026" AS child_adult_only_age_off_2026,
    "ReasonForBronzeToSilverCrosswalk" AS reason_for_bronze_to_silver_crosswalk,
    "SilverCSREligPlanID_2026" AS silver_csr_elig_plan_id_2026,
    "SilverCSREligIssuerID_2026" AS silver_csr_elig_issuer_id_2026,
    "CrosswalkLevel" AS crosswalk_level,
    "ReasonForCrosswalk" AS reason_for_crosswalk
FROM marketplace_raw.raw_plan_id_crosswalk
WHERE "PlanID_2026" IS NOT NULL
  AND "PlanID_2026" <> '';