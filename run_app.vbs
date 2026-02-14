Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory of the script
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strScriptPath

' Display starting message
MsgBox "Starting Phiversity..." & vbCrLf & vbCrLf & "Checking dependencies...", vbInformation, "Phiversity"

' Check if Python is installed
Set objExec = objShell.Exec("python --version")
If objExec.Status = 0 Then
    strPythonVersion = objExec.StdOut.ReadAll()
    strPythonVersion = Trim(strPythonVersion)
Else
    MsgBox "ERROR: Python is not installed or not in PATH!" & vbCrLf & vbCrLf & "Please install Python 3.9+ from python.org", vbCritical, "Phiversity - Error"
    WScript.Quit(1)
End If

' Check if virtual environment exists
strVenvPath = objFSO.BuildPath(strScriptPath, ".venv")
strVenv312Path = objFSO.BuildPath(strScriptPath, ".venv312")

If objFSO.FolderExists(strVenvPath) Then
    strVenvDir = ".venv"
ElseIf objFSO.FolderExists(strVenv312Path) Then
    strVenvDir = ".venv312"
Else
    MsgBox "ERROR: Virtual environment not found!" & vbCrLf & vbCrLf & "Please run: python -m venv .venv", vbCritical, "Phiversity - Error"
    WScript.Quit(1)
End If

' Check if required files exist
strRequiredFiles = Array("scripts/server/app.py", "pyproject.toml", "web/index.html")
For Each strFile In strRequiredFiles
    strFilePath = objFSO.BuildPath(strScriptPath, strFile)
    If Not objFSO.FileExists(strFilePath) Then
        MsgBox "ERROR: Required file not found: " & strFile & vbCrLf & vbCrLf & "Please ensure you have the complete Phiversity installation.", vbCritical, "Phiversity - Error"
        WScript.Quit(1)
    End If
Next

' Get pip executable path
strPipPath = objFSO.BuildPath(strScriptPath, strVenvDir & "\Scripts\pip.exe")

If Not objFSO.FileExists(strPipPath) Then
    MsgBox "ERROR: pip executable not found!" & vbCrLf & vbCrLf & "Virtual environment may be corrupted.", vbCritical, "Phiversity - Error"
    WScript.Quit(1)
End If

' Install dependencies
MsgBox "Installing dependencies..." & vbCrLf & vbCrLf & "This may take a minute...", vbInformation, "Phiversity"

Set objExec = objShell.Exec("""" & strPipPath & """ install -q -e . 2>nul")
objExec.WaitForProcessToFinish()

If objExec.Status <> 0 Then
    MsgBox "WARNING: Dependency installation may have issues." & vbCrLf & vbCrLf & "The app will attempt to start anyway.", vbExclamation, "Phiversity"
End If

' All checks passed
MsgBox "All checks passed!" & vbCrLf & vbCrLf & "Starting server..." & vbCrLf & "Opening browser at http://127.0.0.1:8000", vbInformation, "Phiversity"

' Run the batch file
strBatFile = objFSO.BuildPath(strScriptPath, "run_app.bat")
objShell.Run strBatFile, 1, False

