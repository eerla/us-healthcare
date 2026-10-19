-- Staging: Marketplace Plan Attributes
-- One row per plan from Plan Attributes PUF
-- Source: CMS Marketplace Plan Attributes PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_plan AS
SELECT
    "BusinessYear"::INTEGER AS business_year,
    "StateCode" AS state_code,
    "IssuerId"::VARCHAR AS issuer_id,
    "IssuerMarketPlaceMarketingName" AS issuer_name,
    "StandardComponentId" AS standard_component_id,
    "PlanMarketingName" AS plan_marketing_name,
    "HIOSProductId" AS hios_product_id,
    "NetworkId" AS network_id,
    "ServiceAreaId" AS service_area_id,
    "FormularyId" AS formulary_id,
    "IsNewPlan" = 'New' AS is_new_plan,
    "PlanType" AS plan_type,
    "MetalLevel" AS metal_level,
    "DesignType" AS design_type,
    "UniquePlanDesign" = 'Yes' AS unique_plan_design,
    "QHPNonQHPTypeId" AS qhp_non_qhp_type_id,
    "IsNoticeRequiredForPregnancy" = 'Yes' AS is_notice_required_for_pregnancy,
    "IsReferralRequiredForSpecialist" = 'Yes' AS is_referral_required_for_specialist,
    "SpecialistRequiringReferral" AS specialist_requiring_referral,
    "PlanLevelExclusions" AS plan_level_exclusions,
    REPLACE(REPLACE("IndianPlanVariationEstimatedAdvancedPaymentAmountPerEnrollee", '$', ''), ',', '')::DECIMAL AS indian_plan_variation_adv_payment,
    "CompositeRatingOffered" = 'Yes' AS composite_rating_offered,
    "ChildOnlyOffering" = 'Yes' AS child_only_offering,
    "ChildOnlyPlanId" AS child_only_plan_id,
    "WellnessProgramOffered" = 'Yes' AS wellness_program_offered,
    "DiseaseManagementProgramsOffered" = 'Yes' AS disease_management_programs_offered,
    "MarketCoverage" AS market_coverage,
    "DentalOnlyPlan" = 'Yes' AS dental_only_plan,
    "SourceName" AS source_name,
    CASE 
    WHEN "ImportDate" ~ '^\d{2}/\d{2}/\d{4}$' THEN 
        make_date(
            substring("ImportDate" from 7 for 4)::INTEGER,  -- year
            substring("ImportDate" from 1 for 2)::INTEGER,  -- month
            substring("ImportDate" from 4 for 2)::INTEGER   -- day
        )
    ELSE NULL 
END AS import_date,
    "BusinessYear" AS plan_year
FROM marketplace_raw.raw_plan_attributes
WHERE "StandardComponentId" IS NOT NULL
  AND "StandardComponentId" <> '';