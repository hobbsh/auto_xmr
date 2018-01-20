$ErrorActionPreference = "Stop"

C:\auto_monero\scripts\devcon.ps1
C:\auto_monero\overdriventool\OverdriveNTool.exe -p0"vega_fe" -p1"vega_fe" -p2"vega_fe" -p3"vega_fe" -p4"vega_fe"

set GPU_FORCE_64BIT_PTR=1
set GPU_MAX_HEAP_SIZE=99
set GPU_MAX_ALLOC_PERCENT=99
set GPU_SINGLE_ALLOC_PERCENT=99

C:\auto_monero\miner\xmr-stak.exe --noCPU -c C:\auto_monero\miner\config.txt --amd C:\auto_monero\miner\amd.txt --noNVIDIA