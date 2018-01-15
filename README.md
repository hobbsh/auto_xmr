# auto_monero
Trying to automate as much of the Vega XMR mining shenanigans as possible

### Powershell

Make sure you enable script execution in Group Policy (gp so the powershell scripts can run (and so it persists on reboots). Set it to "Allow local and remote signed scripts". If you are paranoid, you can also enable this for just the User.
```
Computer Configuration
-Administrative Templates
  -Windows Components
    -Windows PowerShell -> Turn on Script Execution > 
```
