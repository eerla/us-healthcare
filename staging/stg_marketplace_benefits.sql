-- Staging: Marketplace Benefits & Cost Sharing
-- One row per plan per benefit
-- Source: CMS Marketplace Benefits & Cost Sharing PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_benefits AS
SELECT
    "BusinessYear"::INTEGER AS business_year,
    "StateCode" AS state_code,
    "IssuerId"::VARCHAR AS issuer_id,
    "StandardComponentId" AS standard_component_id,
    "PlanId" AS plan_id,
    "BenefitName" AS benefit_name,
    CASE 
        WHEN "CopayInnTier1" IN ('Not Applicable', 'No Charge') THEN NULL
        WHEN "CopayInnTier1" ~ '^[\d\.,$]+$' THEN REPLACE(REPLACE("CopayInnTier1", '$', ''), ',', '')::DECIMAL
        ELSE NULL
    END AS copay_inn_tier1,
    CASE 
        WHEN "CopayInnTier2" IN ('Not Applicable', 'No Charge') THEN NULL
        WHEN "CopayInnTier2" ~ '^[\d\.,$]+$' THEN REPLACE(REPLACE("CopayInnTier2", '$', ''), ',', '')::DECIMAL
        ELSE NULL
    END AS copay_inn_tier2,
    CASE 
        WHEN "CopayOutofNet" IN ('Not Applicable', 'No Charge') THEN NULL
        WHEN "CopayOutofNet" ~ '^[\d\.,$]+$' THEN REPLACE(REPLACE("CopayOutofNet", '$', ''), ',', '')::DECIMAL
        ELSE NULL
    END AS copay_out_of_net,
    CASE 
        WHEN "CoinsInnTier1" IN ('Not Applicable', 'No Charge') THEN NULL
        WHEN "CoinsInnTier1" ~ '^[\d\.,$]+$' THEN REPLACE(REPLACE("CoinsInnTier1", '$', ''), ',', '')::DECIMAL
        ELSE NULL
    END AS coins_inn_tier1,
    CASE 
        WHEN "CoinsInnTier2" IN ('Not Applicable', 'No Charge') THEN NULL
        WHEN "CoinsInnTier2" ~ '^[\d\.,$]+$' THEN REPLACE(REPLACE("CoinsInnTier2", '$', ''), ',', '')::DECIMAL
        ELSE NULL
    END AS coins_inn_tier2,
    CASE 
        WHEN "CoinsOutofNet" IN ('Not Applicable', 'No Charge') THEN NULL
        WHEN "CoinsOutofNet" ~ '^[\d\.,$]+$' THEN REPLACE(REPLACE("CoinsOutofNet", '$', ''), ',', '')::DECIMAL
        ELSE NULL
    END AS coins_out_of_net,
    "IsEHB" = 'Yes' AS is_ehb,
    "IsCovered" = 'Covered' AS is_covered,
    "QuantLimitOnSvc"::BOOLEAN AS quant_limit_on_svc,
    "LimitQty"::INTEGER AS limit_qty,
    "LimitUnit" AS limit_unit,
    "Exclusions" AS exclusions,
    "Explanation" AS explanation,
    "EHBVarReason" AS ehb_var_reason,
    "IsExclFromInnMOOP"::BOOLEAN AS is_excl_from_inn_moop,
    "IsExclFromOonMOOP"::BOOLEAN AS is_excl_from_oon_moop,
    "SourceName" AS source_name,
    "ImportDate"::DATE AS import_date
FROM marketplace_raw.raw_benefits_cost_sharing
WHERE "StandardComponentId" IS NOT NULL
  AND "StandardComponentId" <> '';