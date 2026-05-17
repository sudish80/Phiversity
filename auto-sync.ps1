<#
.SYNOPSIS
  Auto-sync Phiversity repo — watches for file changes and pushes to GitHub.
  Run this in the background (or via Task Scheduler) for continuous sync.
.DESCRIPTION
  Uses FileSystemWatcher to detect changes. After 60s of inactivity,
  automatically commits and pushes. Logs to auto-sync.log.
.PARAMETER WatchSeconds
  Debounce window — seconds of no changes before a commit triggers (default: 60).
.PARAMETER PollMinutes
  Fallback: force a sync check every N minutes even without file events (default: 15).
#>

param(
  [int]$WatchSeconds = 60,
  [int]$PollMinutes = 15
)

$script:Root = Split-Path -Parent $PSCommandPath
$script:LogFile = Join-Path $script:Root "auto-sync.log"
$script:DebounceTimer = $null
$script:WatchTimer = $null

function Write-Log {
  param([string]$Msg)
  $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Msg"
  Write-Host $line
  Add-Content -Path $script:LogFile -Value $line
}

function Invoke-Sync {
  try {
    Push-Location $script:Root

    # Fetch latest from remote
    git fetch origin 2>&1 | Out-Null

    # Check for local changes
    $status = git status --porcelain 2>&1
    if (-not $status) {
      Write-Log "Sync: no local changes"
      Pop-Location
      return
    }

    # Check if there's anything to commit
    $hasChanges = $status -ne ""
    if (-not $hasChanges) {
      Write-Log "Sync: no changes to commit"
      Pop-Location
      return
    }

    # Stage everything, commit, push
    git add -A 2>&1 | Out-Null
    $changeSummary = ($status | Select-Object -First 5) -join "; "
    git commit -m "Auto-sync: ${changeSummary}" 2>&1 | Out-Null
    git push origin main 2>&1 | Out-Null
    Write-Log "Sync: committed and pushed successfully"
    Pop-Location
  } catch {
    Write-Log "Sync: ERROR - $($_.Exception.Message)"
    try { Pop-Location } catch {}
  }
}

function On-Changed {
  # Reset the debounce timer on any file change
  if ($script:DebounceTimer) { $script:DebounceTimer.Dispose() }
  $script:DebounceTimer = [System.Timers.Timer]::new($WatchSeconds * 1000)
  $script:DebounceTimer.AutoReset = $false
  Register-ObjectEvent -InputObject $script:DebounceTimer -EventName Elapsed -Action {
    Invoke-Sync
  } | Out-Null
  $script:DebounceTimer.Start()
}

# ─── File Watcher ───
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $script:Root
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::DirectoryName
$watcher.EnableRaisingEvents = $true

# Exclude patterns (git-ignored directories)
$excludeDirs = @('\.git', '__pycache__', 'node_modules', '.venv', '.venv312', 'env', 'venv',
                 'media', 'voice_cache', 'web_jobs', 'dist', '.vscode', '.obsidian',
                 '__pycache__')

$shouldSkip = {
  param($path)
  foreach ($ex in $excludeDirs) {
    if ($path -match $ex) { return $true }
  }
  return $false
}

$action = {
  $path = $Event.SourceEventArgs.FullPath
  if (-not (& $shouldSkip $path)) {
    On-Changed
  }
}

Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action | Out-Null

Write-Log "Auto-sync started. Watching: $script:Root"
Write-Log "Debounce: ${WatchSeconds}s | Poll: every ${PollMinutes}min"
Write-Log "Logging to: $script:LogFile"

# ─── Periodic poll fallback ───
$script:PollTimer = New-Object System.Timers.Timer ($PollMinutes * 60 * 1000)
$script:PollTimer.AutoReset = $true
Register-ObjectEvent -InputObject $script:PollTimer -EventName Elapsed -Action {
  Invoke-Sync
} | Out-Null
$script:PollTimer.Start()

# ─── Keep alive ───
Write-Host "Press Ctrl+C to stop auto-sync." -ForegroundColor Green
while ($true) {
  Start-Sleep -Seconds 10
}
