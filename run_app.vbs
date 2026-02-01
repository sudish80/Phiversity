Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory of the script
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Run the batch file
strBatFile = objFSO.BuildPath(strScriptPath, "run_app.bat")

objShell.Run strBatFile, 1, False
