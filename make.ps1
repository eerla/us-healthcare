#!/usr/bin/env pwsh
param(
    [Parameter(Position=0)]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"

$Directories = @(
    "raw\nppes",
    "raw\cms",
    "raw\census",
    "raw\marketplace",
    "db",
    "staging",
    "core",
    "mart",
    "sql",
    "tests",
    "notebooks",
    "dashboards",
    "docs",
    "manifests",
    "outputs\tables",
    "outputs\charts",
    "outputs\maps"
)

$Sources = @(
    @{ key="nppes"; url="https://download.cms.gov/nppes/NPI_Files.html" },
    @{ key="cms_clinicians"; url="https://data.cms.gov/provider-data/dataset/mj5m-pzi6" },
    @{ key="cms_affiliation"; url="https://data.cms.gov/provider-data/dataset/27ea-46a8" },
    @{ key="cms_hospital"; url="https://data.cms.gov/provider-data/dataset/xubh-q36u" },
    @{ key="census_acs"; url="https://www.census.gov/data/developers/data-sets/acs-5year.html" },
    @{ key="census_tiger"; url="https://www.census.gov/geographies/mapping-files.html" }
)

function Write-Header($text) {
    Write-Host ""
    Write-Host $text -ForegroundColor Cyan
}

function Invoke-Setup {
    Write-Header "Creating directory structure..."
    foreach ($dir in $Directories) {
        $path = Join-Path $PSScriptRoot $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
            Write-Host "  Created: $dir"
        } else {
            Write-Host "  Exists: $dir"
        }
    }
    Write-Host "Directory structure created."
}

function Invoke-ValidateSources {
    Write-Header "Validating source URLs..."
    foreach ($src in $Sources) {
        try {
            $response = Invoke-WebRequest -Uri $src.url -Method Head -UseBasicParsing -TimeoutSec 15
            Write-Host "  [OK] $($src.key): $($src.url) ($($response.StatusCode))"
        } catch {
            Write-Host "  [WARN] $($src.key): $($src.url) - $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    Write-Host "Source validation complete."
}

function Invoke-Clean {
    Write-Header "Cleaning generated databases and outputs..."
    $pathsToClean = @(
        "db\*.duckdb",
        "outputs\tables\*.csv",
        "outputs\charts\*.png",
        "outputs\maps\*.png"
    )
    foreach ($pattern in $pathsToClean) {
        $fullPattern = Join-Path $PSScriptRoot $pattern
        Remove-Item -Path $fullPattern -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Clean complete."
}

function Show-Help {
    Write-Host ""
    Write-Host "US Healthcare Data Pipeline - Build Tool" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\make.ps1 <target>"
    Write-Host ""
    Write-Host "Targets:"
    Write-Host "  setup            Create directory structure"
    Write-Host "  validate-sources Check all source URLs are reachable"
    Write-Host "  clean            Remove generated databases and outputs"
    Write-Host "  help             Show this help message"
    Write-Host ""
    Write-Host "Note: Ingestion and transformation targets require Python scripts to be implemented."
    Write-Host "      Use Git Bash or WSL for Makefile targets, or run Python commands directly."
    Write-Host ""
}

switch ($Target.ToLower()) {
    "setup" { Invoke-Setup }
    "validate-sources" { Invoke-ValidateSources }
    "clean" { Invoke-Clean }
    "help" { Show-Help }
    default {
        Write-Host "Unknown target: $Target" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
