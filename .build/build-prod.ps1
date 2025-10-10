#!/usr/bin/env pwsh
# Production Build Script for AI Telegram Bot (Windows PowerShell)
# Usage: .\.build\build-prod.ps1 [-Tag <tag>] [-Push] [-Help]

param(
    [string]$Tag = "latest",
    [switch]$Push,
    [switch]$Help
)

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Show-Help {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor $InfoColor
    Write-Host "  AI Telegram Bot - Production Build Script" -ForegroundColor $InfoColor
    Write-Host "==================================================" -ForegroundColor $InfoColor
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor $InfoColor
    Write-Host "  .\.build\build-prod.ps1 [-Tag <tag>] [-Push] [-Help]"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor $InfoColor
    Write-Host "  -Tag <tag>    Docker image tag (default: latest)"
    Write-Host "  -Push         Push image to registry after build"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $InfoColor
    Write-Host "  .\.build\build-prod.ps1"
    Write-Host "  .\.build\build-prod.ps1 -Tag v1.0.0"
    Write-Host "  .\.build\build-prod.ps1 -Tag v1.0.0 -Push"
    Write-Host ""
    exit 0
}

if ($Help) {
    Show-Help
}

# Configuration
$ImageName = "ai-tg-bot"
$Registry = ""  # Оставь пустым для локальной сборки или укажи свой registry (например: "cr.yandex/crp1nepgdftqcnu309rn")
$DockerfilePath = ".build/Dockerfile"

# Формирование полного имени образа
if ($Registry) {
    $FullImageName = "$Registry/$ImageName"
} else {
    $FullImageName = $ImageName
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor $InfoColor
Write-Host "  Building Production Docker Image" -ForegroundColor $InfoColor
Write-Host "==================================================" -ForegroundColor $InfoColor
Write-Host ""

# Check if Docker is installed
Write-Host "[1/4] Checking Docker installation..." -ForegroundColor $InfoColor
try {
    $dockerVersion = docker --version
    Write-Host "  ✓ Docker found: $dockerVersion" -ForegroundColor $SuccessColor
} catch {
    Write-Host "  ✗ Docker is not installed or not in PATH" -ForegroundColor $ErrorColor
    Write-Host "  Please install Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor $ErrorColor
    exit 1
}

# Check if Dockerfile exists
Write-Host ""
Write-Host "[2/4] Checking Dockerfile..." -ForegroundColor $InfoColor
if (-not (Test-Path $DockerfilePath)) {
    Write-Host "  ✗ Dockerfile not found: $DockerfilePath" -ForegroundColor $ErrorColor
    exit 1
}
Write-Host "  ✓ Dockerfile found: $DockerfilePath" -ForegroundColor $SuccessColor

# Build Docker image
Write-Host ""
Write-Host "[3/4] Building Docker image..." -ForegroundColor $InfoColor
Write-Host "  Image: $FullImageName`:$Tag" -ForegroundColor $InfoColor
Write-Host "  Dockerfile: $DockerfilePath" -ForegroundColor $InfoColor
Write-Host ""

$buildArgs = @(
    "build",
    "-f", $DockerfilePath,
    "-t", "$FullImageName`:$Tag",
    "-t", "$FullImageName`:latest",
    "--build-arg", "BUILDTIME=$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')",
    "."
)

& docker $buildArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  ✗ Docker build failed" -ForegroundColor $ErrorColor
    exit 1
}

Write-Host ""
Write-Host "  ✓ Docker image built successfully" -ForegroundColor $SuccessColor

# Push to registry if requested
if ($Push) {
    Write-Host ""
    Write-Host "[4/4] Pushing image to registry..." -ForegroundColor $InfoColor
    
    docker push "$FullImageName`:$Tag"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Failed to push image" -ForegroundColor $ErrorColor
        exit 1
    }
    
    docker push "$FullImageName`:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Failed to push latest tag" -ForegroundColor $ErrorColor
        exit 1
    }
    
    Write-Host "  ✓ Image pushed successfully" -ForegroundColor $SuccessColor
} else {
    Write-Host ""
    Write-Host "[4/4] Skipping push (use -Push to push to registry)" -ForegroundColor $WarningColor
}

# Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor $SuccessColor
Write-Host "  Build Completed Successfully!" -ForegroundColor $SuccessColor
Write-Host "==================================================" -ForegroundColor $SuccessColor
Write-Host ""
Write-Host "Image tags created:" -ForegroundColor $InfoColor
Write-Host "  - $FullImageName`:$Tag"
Write-Host "  - $FullImageName`:latest"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor $InfoColor
Write-Host "  1. Configure environment variables in .build/docker-compose.prod.yml"
Write-Host "     (укажи TELEGRAM_TOKEN и OPENROUTER_API_KEY)"
Write-Host ""
Write-Host "  2. Run with docker-compose:"
Write-Host "     docker-compose -f .build/docker-compose.prod.yml up -d"
Write-Host ""
Write-Host "  3. Check logs:"
Write-Host "     docker-compose -f .build/docker-compose.prod.yml logs -f bot"
Write-Host ""

if (-not $Push) {
    Write-Host "  4. Push to registry (optional):"
    Write-Host "     .\.build\build-prod.ps1 -Tag $Tag -Push"
    Write-Host ""
}

