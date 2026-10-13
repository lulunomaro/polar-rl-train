from pathlib import Path
import json,time,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
def main():
 p='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/env/lib/site-packages/isaacsim/kit/data/Kit/Isaac-Sim/5.1/f4adcb23-b55a-4b8c-8f14-528aa60e1b06.dmp'
 code="[Console]::OutputEncoding=[Text.Encoding]::UTF8; $f=Get-Item -LiteralPath '"+p+"';[pscustomobject]@{path=$f.FullName;bytes=$f.Length;sha256=(Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLower();original_retained=$true}|ConvertTo-Json -Compress"
 x=json.loads(powershell(connect(),code,60));report=D/'reports'/('NATIVE2048_ORIGINAL_DUMP_INDEX_'+str(time.time_ns())+'.json');report.write_text(json.dumps(x,indent=2),encoding='utf8');print(json.dumps(x))
if __name__=='__main__':main()
