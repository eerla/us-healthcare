-- Staging: Marketplace Rate
-- One row per plan per rating area per age per tobacco status
-- Source: CMS Marketplace Rate PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_rate AS
SELECT
    "BusinessYear"::INTEGER AS business_year,
    "StateCode" AS state_code,
    "IssuerId"::VARCHAR AS issuer_id,
    "PlanId" AS plan_id,
    "RatingAreaId" AS rating_area_id,
    "Tobacco" = 'Tobacco User' AS tobacco,
    CASE 
    WHEN "Age" IN ('0-14', '64 and over', 'Family Option') THEN NULL
    ELSE "Age"::INTEGER
END AS age,
    "IndividualRate"::DECIMAL AS individual_rate,
    "IndividualTobaccoRate"::DECIMAL AS individual_tobacco_rate,
    "Couple"::DECIMAL AS couple_rate,
    "PrimarySubscriberAndOneDependent"::DECIMAL AS primary_subscriber_one_dep,
    "PrimarySubscriberAndTwoDependents"::DECIMAL AS primary_subscriber_two_dep,
    "PrimarySubscriberAndThreeOrMoreDependents"::DECIMAL AS primary_subscriber_three_plus_dep,
    "CoupleAndOneDependent"::DECIMAL AS couple_one_dep,
    "CoupleAndTwoDependents"::DECIMAL AS couple_two_dep,
    "CoupleAndThreeOrMoreDependents"::DECIMAL AS couple_three_plus_dep,
    "RateEffectiveDate"::DATE AS rate_effective_date,
    "RateExpirationDate"::DATE AS rate_expiration_date,
    "SourceName" AS source_name,
    "ImportDate"::DATE AS import_date,
    EXTRACT(YEAR FROM "RateEffectiveDate"::DATE) AS rate_year,
FROM marketplace_raw.raw_rate
WHERE "PlanId" IS NOT NULL
  AND "PlanId" <> ''
  AND "RatingAreaId" IS NOT NULL
  AND "RatingAreaId" <> '';