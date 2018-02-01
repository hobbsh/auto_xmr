$ErrorActionPreference = "Stop"

# Get the ID and security principal of the current user account
$myWindowsID=[System.Security.Principal.WindowsIdentity]::GetCurrent()
$myWindowsPrincipal=new-object System.Security.Principal.WindowsPrincipal($myWindowsID)
 
# Get the security principal for the Administrator role
$adminRole=[System.Security.Principal.WindowsBuiltInRole]::Administrator
 
# Check to see if we are currently running "as Administrator"
if ($myWindowsPrincipal.IsInRole($adminRole)){
   # We are running "as Administrator" - so change the title and background color to indicate this
   $Host.UI.RawUI.WindowTitle = $myInvocation.MyCommand.Definition + "(Elevated)"
   $Host.UI.RawUI.BackgroundColor = "DarkBlue"
   clear-host
}
else {
   # We are not running "as Administrator" - so relaunch as administrator
   
   # Create a new process object that starts PowerShell
   $newProcess = new-object System.Diagnostics.ProcessStartInfo "PowerShell";
   
   # Specify the current script path and name as a parameter
   $newProcess.Arguments = $myInvocation.MyCommand.Definition;
   
   # Indicate that the process should be elevated
   $newProcess.Verb = "runas";
   
   # Start the new process
   [System.Diagnostics.Process]::Start($newProcess);
   
   # Exit from the current, unelevated, process
   exit
}
 
C:\auto_monero\scripts\devcon.ps1
C:\auto_monero\overdriventool\OverdriveNTool.exe -p1"vega_fe" -p2"vega64" -p3"vega_fe" -p4"vega_fe" -p5"vega_fe"

set GPU_FORCE_64BIT_PTR=1
set GPU_MAX_HEAP_SIZE=99
set GPU_MAX_ALLOC_PERCENT=99
set GPU_SINGLE_ALLOC_PERCENT=99

C:\auto_monero\miner\xmr-stak.exe --noCPU -c C:\auto_monero\miner\config.txt --amd C:\auto_monero\miner\amd.txt --noNVIDIA