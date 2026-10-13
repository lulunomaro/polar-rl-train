"""One batched SSH metadata read; import only authorized native transport functions."""
from pathlib import Path
import sys, json, time, traceback, base64, hashlib
W=Path('C:/Users/lulu/Desktop/claude/mjcf')
F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
D=W/'MOD4_4090_WINDOWS_REPAIR_20261013'
sys.path.insert(0,str(D))
from windows4090_native_transport import connect,powershell

py=r'''
import sys,json,importlib.metadata as md,importlib.util
out={'executable':sys.executable,'python':sys.version,'packages':{},'top_level_module_specs':{},'no_Isaac_or_Torch_or_CUDA_import':True}
for name in ['torch','isaacsim','isaaclab','isaaclab-rl','isaaclab_rl','rsl-rl-lib','rsl-rl','tensordict','warp-lang','numpy','scipy','gymnasium']:
 try:
  d=md.distribution(name);out['packages'][name]={'version':d.version,'location':str(d.locate_file(''))}
 except md.PackageNotFoundError:out['packages'][name]=None
 except Exception as e:out['packages'][name]={'metadata_error':type(e).__name__+': '+str(e)}
for name in ['torch','isaacsim','isaaclab','isaaclab_rl','rsl_rl','tensordict','warp']:
 try:
  s=importlib.util.find_spec(name);out['top_level_module_specs'][name]=None if s is None else {'origin':s.origin,'search_locations':list(s.submodule_search_locations or [])}
 except Exception as e:out['top_level_module_specs'][name]={'metadata_error':type(e).__name__+': '+str(e)}
print(json.dumps(out))
'''
encoded=base64.b64encode(py.encode()).decode()
code=r'''
$OutputEncoding=[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new()
$env:CUDA_VISIBLE_DEVICES=''
$roots=@('D:\anaconda\envs','C:\Users\Win10\.local\share\ov\pkg','D:\BRUH','D:\cq')
$inventory=[ordered]@{}
$pythonPaths=New-Object System.Collections.Generic.List[string]
foreach($p in @('D:\anaconda\python.exe')){if(Test-Path -LiteralPath $p){$pythonPaths.Add($p)}}
foreach($root in $roots){
 if(Test-Path -LiteralPath $root){
  $top=@(Get-ChildItem -LiteralPath $root -Force -ErrorAction SilentlyContinue | Select-Object -First 80 Name,FullName,Mode)
  $markers=@(Get-ChildItem -LiteralPath $root -Directory -Depth 2 -Force -ErrorAction SilentlyContinue | Where-Object {$_.Name -match 'isaac|omniverse|venv|env|python'} | Select-Object -First 120 Name,FullName)
  $inventory[$root]=[ordered]@{exists=$true;top=$top;SDK_or_environment_directory_markers=$markers}
  if($root -eq 'D:\anaconda\envs'){
   foreach($e in @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue | Select-Object -First 12)){
    $p=Join-Path $e.FullName 'python.exe';if(Test-Path -LiteralPath $p){$pythonPaths.Add($p)}
   }
  } else {
   foreach($e in $markers){
    foreach($relative in @('python.exe','Scripts\python.exe','kit\python\python.exe')){
     $p=Join-Path $e.FullName $relative;if(Test-Path -LiteralPath $p){$pythonPaths.Add($p)}
    }
   }
  }
 }else{$inventory[$root]=[ordered]@{exists=$false}}
}
foreach($e in @(Get-ChildItem -LiteralPath 'C:\Users\Win10\AppData\Local\Programs\Python' -Directory -ErrorAction SilentlyContinue | Select-Object -First 4)){
 $p=Join-Path $e.FullName 'python.exe';if(Test-Path -LiteralPath $p){$pythonPaths.Add($p)}
}
$pycode=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('__PY_B64__'))
$rows=New-Object System.Collections.Generic.List[object]
foreach($p in @($pythonPaths | Select-Object -Unique | Select-Object -First 16)){
 try{
  $text=(& $p -c $pycode 2>&1 | Out-String).Trim();$exit=$LASTEXITCODE
  try{$data=$text | ConvertFrom-Json}catch{$data=$null}
  $rows.Add([ordered]@{python_path=$p;exit_code=$exit;metadata=$data;raw_metadata_output=$text})
 }catch{$rows.Add([ordered]@{python_path=$p;error=$_.Exception.Message})}
}
[ordered]@{timestamp=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();hostname=$env:COMPUTERNAME;root_inventory=$inventory;python_metadata=$rows;read_only=$true;no_Isaac_or_Torch_or_CUDA_import=$true;no_GPU_or_install_or_OS_mutation=$true} | ConvertTo-Json -Depth 12 -Compress
'''.replace('__PY_B64__',encoded)

attempts=[]
stamp=str(time.time_ns())
report=F/('WINDOWS4090_SDK_READONLY_INVENTORY_ACTUAL_'+stamp+'.json')
receipt=F/('WINDOWS4090_SDK_READONLY_CONNECT_ATTEMPTS_'+stamp+'.json')
session=None
try:
    session=connect()
    for i in range(6):
        try:
            raw=powershell(session,code,120)
            attempts.append(dict(attempt=i+1,epoch=time.time(),passed=True))
            data=json.loads(raw)
            data['native_transport_import_only_no_source_or_key_bytes_read']=True
            data['local_script_source_index']=dict(path=__file__,sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
            data['Git_archive_pending_root_unified_stage']=True
            report.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
            print(json.dumps(dict(passed_readonly=True,report=str(report),interpreters=[dict(path=x['python_path'],exit=x.get('exit_code'),packages=(x.get('metadata') or {}).get('packages')) for x in data['python_metadata']]),ensure_ascii=False))
            break
        except RuntimeError as e:
            attempts.append(dict(attempt=i+1,epoch=time.time(),passed=False,error=str(e)))
            if not any(s in str(e) for s in ('kex_exchange','banner exchange','MaxStartups')):raise
            if i==5:raise RuntimeError('Six bounded metadata SSH prehandshake rejections')
            time.sleep(5)
except BaseException:
    (F/('WINDOWS4090_SDK_READONLY_READER_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_Isaac_or_Torch_or_CUDA_import=True,no_GPU_or_install_or_OS_mutation=True,report_pending=True),indent=2),encoding='utf8')
    raise
finally:
    receipt.write_text(json.dumps(dict(epoch=time.time(),attempts=attempts,one_batched_read_only_inventory=True,max_prehandshake_retries=6,no_periodic_monitor=True,actual_inventory_report=str(report) if report.exists() else None),indent=2),encoding='utf8')
    if session is not None:session.close()
