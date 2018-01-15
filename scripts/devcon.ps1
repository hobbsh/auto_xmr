cd "C:\Program Files (x86)\Windows Kits\10\Tools\x64"
$devcon_out = .\devcon.exe listclass display | Out-String
$devcon_split = $devcon.Split("`n`r")
$devices = $devcon_split[1..($devcon_split.length)]

foreach ($device in $devices) {
  $device_data = $device.Split(":")
  $devcon_string = $device_data[0]
  $device_name = $device_data[1] -replace "`t|`n|`r"""

  IF($device_name -ne ""){
    Write-Host "Disabling $device_name - $devcon_string"
    .\devcon.exe disable "@$devcon_string"
    Start-Sleep -s 20
    Write-Host "Enabling $device_name - $devcon_string"
    .\devcon.exe enable "@$devcon_string"

    C:\auto_monero\scripts\ulps_crossfire.ps1
  }
}