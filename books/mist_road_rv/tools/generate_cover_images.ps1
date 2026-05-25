param(
    [string]$EnvFile = "books/mist_road_rv/secrets/cover_image.env",
    [string]$PromptFile = "books/mist_road_rv/tmp/cover_action_chase_jobs.jsonl",
    [string]$OutDir = "books/mist_road_rv/assets/covers",
    [string]$Model = "gpt-image-2",
    [int]$Concurrency = 3
)

$ErrorActionPreference = "Stop"

function Read-EnvFile {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing env file: $Path. Copy books/mist_road_rv/secrets/cover_image.env.example to $Path and fill it in."
    }

    $values = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        $parts = $trimmed.Split("=", 2)
        if ($parts.Count -ne 2) {
            continue
        }
        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        $values[$name] = $value
    }
    return $values
}

$envValues = Read-EnvFile -Path $EnvFile

if (-not $envValues.ContainsKey("OPENAI_API_KEY") -or -not $envValues["OPENAI_API_KEY"] -or $envValues["OPENAI_API_KEY"] -eq "replace_with_your_key") {
    throw "OPENAI_API_KEY is missing or still a placeholder in $EnvFile."
}

if (-not $envValues.ContainsKey("OPENAI_BASE_URL") -or -not $envValues["OPENAI_BASE_URL"]) {
    throw "OPENAI_BASE_URL is missing in $EnvFile."
}

$env:OPENAI_API_KEY = $envValues["OPENAI_API_KEY"]
$env:OPENAI_BASE_URL = $envValues["OPENAI_BASE_URL"]

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

python C:\Users\HYMOD\.codex\skills\.system\imagegen\scripts\image_gen.py generate-batch `
    --input $PromptFile `
    --out-dir $OutDir `
    --concurrency $Concurrency `
    --model $Model `
    --force
