# auto_monero
Trying to automate as much of the Vega XMR mining shenanigans as possible

If this helped you, consider donating. Thanks!

`XMR: 42TtmJxMEReSPiU39tUwFZ84KpFSpzdhuHstkzuTCipTdAuFqh7eMtk6b4zSLvfWZDA26aMKVTynYNVX19996DJx5uJugZm`

## Prerequisites
* xmr_stak
* OverdriveNTool
* Windows DK (for devcon.exe)
* Powershell 

### 1. Clone this repo to C:\
I recommend https://git-scm.com 

### 2. Allow Powershell script execution

Make sure you enable script execution in Group Policy (gp so the powershell scripts can run (and so it persists on reboots). Set it to "Allow local and remote signed scripts". If you are paranoid, you can also enable this for just the User.
```
Computer Configuration
-Administrative Templates
  -Windows Components
    -Windows PowerShell -> Turn on Script Execution > 
```

### 3. Make sure your binaries are in place

Look at mine.ps1 and devcon.ps1 for where everything should be.

* xmr_stak installation in C:\auto_monero_\miner
* OverdrivenTool.exe in C:\auto_monero\overdriventool

### 4. Run mine.ps1

`mine.ps1` runs `mine.bat` which starts `xmr_stak.exe`. If you don't want it to start `xmr_stak.exe` and only do `devcon.exe` and `OverdriveNtool.exe`, remove that line in `mine.ps1`

## Contributing

Open a PR!

## Authors
Wylie Hobbs
