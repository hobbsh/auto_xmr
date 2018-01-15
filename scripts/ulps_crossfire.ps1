

Function Test-RegistryValue {
    param(
        [Alias("PSPath")]
        [Parameter(Position = 0, Mandatory = $true, ValueFromPipeline = $true, ValueFromPipelineByPropertyName = $true)]
        [String]$Path
        ,
        [Parameter(Position = 1, Mandatory = $true)]
        [String]$Name
        ,
        [Switch]$PassThru
    ) 

    process {
        if (Test-Path $Path) {
            $Key = Get-Item -LiteralPath $Path
            if ($Key.GetValue($Name, $null) -ne $null) {
                if ($PassThru) {
                    Get-ItemProperty $Path $Name
                } else {
                    $true
                }
            } else {
                $false
            }
        } else {
            $false
        }
    }
}


$registry_path_root = 'HKLM:\SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}'
$keys = ("EnableUlps", "EnableCrossfireAutoLink")
$cards = ("0000", "0001", "0002", "0003")
$value = "0"
foreach ($card in $cards) {
  foreach ($key in $keys) {
    $path = $registry_path_root + "\" + $card
    $key_path = $path + "\" + $key
    IF(Test-RegistryValue -Path $path -Name $key) {
      Write-Host "Setting $key for card $card to $value"
      Set-ItemProperty -Path $path -Name $key -Value $value
    }
  }
}