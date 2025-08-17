#run as admin

$nssm = "$PSScriptRoot\nssm.exe"
$python = (Get-Command python).Source
$agent = "C:\syshealth-agent\agent.py"
New-Item -ItemType Directory -Path "C:\syshealth-agent" -Force | Out-Null
Copy-Item "$PSScriptRoot\..\..\agent.py" "C:\syshealth-agent\agent.py" -Force
Copy-Item "$PSScriptRoot\..\..\config.json" "C:\syshealth-agent\config.json" -Force
& $nssm install SysHealthAgent $python "C:\syshealth-agent\agent.py"
& $nssm set SysHealthAgent AppDirectory "C:\syshealth-agent"
& $nssm set SysHealthAgent AppEnvironmentExtra "SYSHEALTH_CONFIG=C:\syshealth-agent\config.json"
& $nssm set SysHealthAgent Start SERVICE_AUTO_START
& $nssm start SysHealthAgent