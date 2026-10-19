"""Read only known MOD4 paths and volume metadata; never mount or copy the ledger."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('WINDOWS_KNOWN_CANONICAL_PATH_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_training_transport=True))
 s=importlib.util.spec_from_file_location('known_strict_windows_transport',W/'MOD4_4090_WINDOWS_REPAIR_20261013/windows4090_native_transport.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 code=r'''
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$paths=@('D:\rl_candidates\MOD4_native_floor_continue10h_20260930\TRAINING_BUDGET_10H.json','D:\home\egde\rl_candidates\MOD4_native_floor_continue10h_20260930\TRAINING_BUDGET_10H.json','C:\Users\Win10\rl_candidates\MOD4_native_floor_continue10h_20260930\TRAINING_BUDGET_10H.json')
$rows=@(foreach($p in $paths){if(Test-Path -LiteralPath $p -PathType Leaf){$i=Get-Item -LiteralPath $p;[ordered]@{path=$p;exists=$true;bytes=$i.Length;last_write=$i.LastWriteTimeUtc.ToString('o');text=[IO.File]::ReadAllText($p)}}else{[ordered]@{path=$p;exists=$false}}})
[ordered]@{computer=$env:COMPUTERNAME;known_paths=$rows;volumes=@(Get-Volume | Select-Object DriveLetter,FileSystemType,FileSystemLabel,Path,Size,SizeRemaining);partitions=@(Get-Partition | Select-Object DiskNumber,PartitionNumber,DriveLetter,GptType,Size,AccessPaths);no_mount_or_ledger_write=$true} | ConvertTo-Json -Depth 7
'''
 out=m.powershell(None,code,timeout=60);v=json.loads(out);put('WINDOWS_KNOWN_CANONICAL_PATHS_AND_VOLUMES_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True,actual=v,no_mount_copy_canonical_or_training_or_budget_write=True));print(json.dumps(dict(known_paths=[dict(path=x['path'],exists=x['exists']) for x in v['known_paths']],actual_finite_transport_returned=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('WINDOWS_KNOWN_CANONICAL_PATH_READER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
