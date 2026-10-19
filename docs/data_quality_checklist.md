# Data Quality Checklist

This document defines the data quality checks that must pass for every dataset.

## NPPES

- [ ] NPI is exactly 10 characters
- [ ] NPI contains only digits
- [ ] Entity type code is '1' or '2'
- [ ] No duplicate NPIs in dim_provider
- [ ] ZIP5 is exactly 5 characters (where present)
- [ ] Source row count matches expected file row count (± header offset)
- [ ] Checksum matches downloaded file

## CMS Doctors & Clinicians

- [ ] NPI format valid (10 digits, or blank/null allowed)
- [ ] No unexpected many-to-many explosion on NPI join to dim_provider
- [ ] Clinician rows per NPI is documented and reasonable
- [ ] Specialty codes map to dim_specialty
- [ ] Source row count matches expected file row count
- [ ] Checksum matches downloaded file

## CMS Facility Affiliation

- [ ] NPI format valid
- [ ] Facility identifiers (CCN) are preserved where present
- [ ] Inferred facility matches have documented method and confidence
- [ ] Source row count matches expected file row count
- [ ] Checksum matches downloaded file

## CMS Hospital General Information

- [ ] CCN is unique in dim_facility
- [ ] State codes are valid
- [ ] Facility types are documented
- [ ] Source row count matches expected file row count
- [ ] Checksum matches downloaded file

## Medicare Utilization

- [ ] NPI join to dim_provider has no many-to-many explosion
- [ ] Year is populated and consistent
- [ ] Services > 0 where beneficiaries > 0
- [ ] Payment <= submitted_charges (sanity check)
- [ ] Source row count matches expected file row count
- [ ] Checksum matches downloaded file

## Census ACS

- [ ] Population > 0 for all reported geographies
- [ ] Geography IDs match expected format (ZCTA, county FIPS)
- [ ] Year is populated and consistent
- [ ] Source row count matches expected file row count
- [ ] Checksum matches downloaded file

## Marketplace PUFs

- [ ] Plan IDs are unique within plan_year
- [ ] State codes are valid
- [ ] Service area keys join cleanly to geography
- [ ] Network URLs are valid URLs where present
- [ ] Source row count matches expected file row count
- [ ] Checksum matches downloaded file

## Cross-Cutting Checks

- [ ] Every analysis records source years/snapshot dates
- [ ] Raw rows = accepted + rejected; rejected rows have a reason
- [ ] No silent year mixing
- [ ] No invented fields or identifiers
- [ ] No patient-level PHI
