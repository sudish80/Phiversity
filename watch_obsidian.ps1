$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "$PSScriptRoot\scripts"
$watcher.Filter = "*.py"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $change = $Event.SourceEventArgs.ChangeType
    Write-Host "[watch] $change : $path"

    # Debounce: wait 500ms then regenerate
    Start-Sleep -Milliseconds 500
    & "$Event.Source\..\.venv\Scripts\python.exe" "$Event.Source\..\scripts\generate_obsidian_moc.py"
}

Register-ObjectEvent $watcher "Created" -Action $action | Out-Null
Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
Register-ObjectEvent $watcher "Deleted" -Action $action | Out-Null
Register-ObjectEvent $watcher "Renamed" -Action $action | Out-Null

Write-Host "Watching scripts/ for changes... (Ctrl+C to stop)"
Write-Host "Phiversity_Obsidian.md will auto-regenerate whenever you add/remove/rename Python files."
while ($true) { Start-Sleep -Seconds 2 }
