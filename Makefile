.PHONY: help setup validate-sources ingest-nppes ingest-cms ingest-census ingest-marketplace ingest-utilization transform analyze dashboard clean

help:
	@echo "US Healthcare Data Pipeline"
	@echo ""
	@echo "Available targets:"
	@echo "  setup              - Create directory structure"
	@echo "  validate-sources   - Check all source URLs are reachable"
	@echo "  ingest-nppes       - Download and ingest NPPES data"
	@echo "  ingest-census      - Download and ingest Census ACS + TIGER/Line"
	@echo "  ingest-cms         - Download and ingest CMS clinicians/facilities/hospitals"
	@echo "  ingest-marketplace - Download and ingest Marketplace Exchange PUFs"
	@echo "  ingest-utilization - Download and ingest Medicare utilization data"
	@echo "  transform          - Run dbt-style SQL transformations (staging -> core -> mart)"
	@echo "  analyze            - Run all 15 analyses and write outputs"
	@echo "  dashboard          - Launch Streamlit CT dashboard"
	@echo "  clean              - Remove generated databases and outputs"

setup:
	@echo "Creating directory structure..."
	@mkdir -p raw/nppes raw/cms raw/census raw/marketplace db staging core mart sql tests notebooks dashboards docs manifests outputs/tables outputs/charts outputs/maps
	@echo "Directory structure created."

validate-sources:
	@echo "Validating source URLs..."
	@python -c "import yaml, requests; sources = yaml.safe_load(open('config/sources.yml')); [print(f'{k}: {v[\"url\"]}') for k, v in sources['sources'].items()]"
	@echo "Source registry validated."

ingest-nppes:
	@echo "Ingesting NPPES V2 data..."
	@python ingestion/nppes/download.py
	@python ingestion/nppes/ingest.py
	@echo "NPPES ingestion complete."

ingest-census:
	@echo "Ingesting Census ACS and TIGER/Line..."
	@python ingestion/census/download.py
	@python ingestion/census/ingest.py
	@echo "Census ingestion complete."

ingest-cms:
	@echo "Ingesting CMS clinicians, facilities, and hospitals..."
	@python ingestion/cms/download.py
	@python ingestion/cms/ingest.py
	@echo "CMS ingestion complete."

ingest-marketplace:
	@echo "Ingesting Marketplace Exchange PUFs..."
	@python ingestion/marketplace/download.py
	@python ingestion/marketplace/ingest.py
	@echo "Marketplace ingestion complete."

ingest-utilization:
	@echo "Ingesting Medicare utilization data..."
	@python ingestion/cms/download_utilization.py
	@python ingestion/cms/ingest_utilization.py
	@echo "Utilization ingestion complete."

transform:
	@echo "Running transformations..."
	@python scripts/run_transform.py
	@echo "Transform complete."

analyze:
	@echo "Running analyses..."
	@python scripts/run_analyses.py
	@echo "Analyses complete."

dashboard:
	@echo "Launching Streamlit dashboard..."
	@streamlit run dashboards/ct_dashboard.py

clean:
	@echo "Cleaning generated databases and outputs..."
	@rm -f db/*.duckdb
	@rm -rf outputs/tables/*.csv outputs/charts/*.png outputs/maps/*.png
	@echo "Clean complete."