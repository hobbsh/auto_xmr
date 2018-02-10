Function Toggle-Device {
  param(
    [Parameter(Position = 0, Mandatory = $true)]
    [String]$Device
    ,
    [Parameter(Position = 1, Mandatory = $true)]
    [String]$ToggleTo
  )

  process{
    $device_exists = .\devcon.exe find @$Device | Out-String
    IF($device_exists -like "*matching device(s) found*"){
      IF($ToggleTo -eq 'disable'){
        $disabled = .\devcon.exe disable @$Device | Out-String
        IF($disabled -like "*Disable failed*"){
          Write-Host "Disable failed for $Device - Exiting"
          Exit
        }
        Start-Sleep -s 5
      }
      ELSEIF($ToggleTo -eq 'enable'){
        $enabled = .\devcon.exe enable @$Device | Out-String
        IF($enabled -like "*Enable failed*"){
          Write-Host "Enable failed for $Device - Exiting"
          Exit
        }
      }
      ELSE {
        Write-Host "Invalid parameter $ToggleTo supplied for ToggleTo"
        return False
      }
    }
    ELSE{
      Write-Host "Device not found - $Device \n Exiting."
      Exit
    }
  }
}

cd "C:\Program Files (x86)\Windows Kits\10\Tools\x64"
$devcon_out = .\devcon.exe listclass display | Out-String
$devcon_split = $devcon_out.Split("`n`r")
$devices = $devcon_split[1..($devcon_split.length)]

foreach ($device in $devices) {
  $device_data = $device.Split(":")
  $devcon_string = $device_data[0]
  $device_name = $device_data[1] -replace "`t|`n|`r"""
  IF($device_name -like "*Vega*"){
    Write-Host "Disabling $device_name"
    Toggle-Device -Device "`"$devcon_string`"" -ToggleTo "disable"

    Write-Host "Enabling $device_name"
    Toggle-Device -Device "`"$devcon_string`"" -ToggleTo "enable"

    Write-Host "Running ulps_crossfire.ps1"
    C:\auto_monero\scripts\ulps_crossfire.ps1
  }
}