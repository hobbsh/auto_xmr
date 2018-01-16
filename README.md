# auto_xmr
Trying to automate as much of the Vega XMR mining shenanigans as possible. All the config files (amd.txt, OverdriveNTool.ini) in this repo are based on a 4x Vega rig (3x Vega FE and 1x Vega 64).

This repo assumes you have everything else setup and working (i.e. drivers, device detection, etc).

If this helped you, consider donating. Thanks!

`XMR: 42TtmJxMEReSPiU39tUwFZ84KpFSpzdhuHstkzuTCipTdAuFqh7eMtk6b4zSLvfWZDA26aMKVTynYNVX19996DJx5uJugZm`

## Prerequisites
* xmr_stak
* OverdriveNTool
* Windows DK (for devcon.exe)
* Powershell
* git-scm
* I'm running Windows 10 Pro x64

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

* xmr_stak installation in C:\auto_monero\miner
* OverdrivenTool.exe in C:\auto_monero\overdriventool

### 4. Run mine.ps1

**Make sure you Run as Administrator!**

`mine.ps1` runs `mine.bat` which starts `xmr_stak.exe`. If you don't want it to start `xmr_stak.exe` and only do `devcon.exe` and `OverdriveNtool.exe`, remove that line in `mine.ps1`

## Footnotes
Additional configuration - may or may not be related to your setup

### Monitoring

monitoring/hashrate_poller.py - can be used to poll the xmr_stak web interface and ship data to Graphite. Only tested on Ubuntu 16.04.

### Dealing with Vega Frontier Edition enable/disable

This is what I had to do to get things setup (I followed Geek Mark's FE video on youtube with some changes):
* Make sure you have remote desktop or Chrome remote desktop enabled!
* Boot into safe mode and DDU every driver (including onboard) - at this point, it's ok to be plugged into one of the cards
* Unplug all cards except one FE and boot
* Install adrenaline driver only - run `ulps_crossfire.ps1` to disable Crossfire and Ulps
* Unplug your monitor and everything resembling one!
* Plug the other cards in
* Run `ulps_crossfire.ps1` again to disable Crossfire and Ulps and reboot
* Make sure settings stick on reboot
* Disable all cards in Device Manager except for one - I pick an FE usually
* Choose Update Driver and select the blockchain driver using "Have Disk"
* When it's done, they should all be enabled. Run `devcon.ps1`
* Run mine.ps1 to get rolling

## References
* vega.miningguides.com
* Geek Mark's Video: https://www.youtube.com/watch?v=wUrt7DgSiDM&t=3s 
* The rest of the beautiful internet

## Contributing

Open a PR!

## Authors
Wylie Hobbs
