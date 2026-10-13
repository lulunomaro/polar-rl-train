"""Continue the same readonly inventory with compact Windows command encoding."""
from pathlib import Path
import sys,json,time,base64,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf')
F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
py="""import sys,json,importlib.metadata as m,importlib.util as u
r={'python':sys.version,'path':sys.executable,'packages':{},'specs':{}}
for n in ['torch','isaacsim','isaaclab','isaaclab-rl','isaaclab_rl','rsl-rl-lib','tensordict','warp-lang','numpy','scipy']:
 try:
  d=m.distribution(n);r['packages'][n]=[d.version,str(d.locate_file(''))]
 except m.PackageNotFoundError:r['packages'][n]=None
for n in ['torch','isaacsim','isaaclab','isaaclab_rl','rsl_rl','tensordict','warp']:
 try:
  s=u.find_spec(n);r['specs'][n]=None if s is None else [s.origin,list(s.submodule_search_locations or [])]
 except Exception as e:r['specs'][n]=str(e)
print(json.dumps(r))
"""
code=r"""
$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$env:CUDA_VISIBLE_DEVICES='';$inv=@{};$pys=@('D:\anaconda\python.exe');
foreach($r in @('D:\anaconda\envs','C:\Users\Win10\.local\share\ov\pkg','D:\BRUH','D:\cq')){
 if(Test-Path -LiteralPath $r){$inv[$r]=@(Get-ChildItem -LiteralPath $r -Force|Select-Object -First 80 Name,FullName,Mode);$ds=@(Get-ChildItem -LiteralPath $r -Directory -Depth 2 -ErrorAction SilentlyContinue|Select-Object -First 100);foreach($d in $ds){foreach($s in @('python.exe','Scripts\python.exe')){$p=Join-Path $d.FullName $s;if(Test-Path -LiteralPath $p){$pys+=$p}}}}else{$inv[$r]=$false}}
foreach($d in @(Get-ChildItem 'C:\Users\Win10\AppData\Local\Programs\Python' -Directory -ErrorAction SilentlyContinue)){$pys+=(Join-Path $d.FullName 'python.exe')}
$pc=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('__PY__'));$rows=@();foreach($p in @($pys|Select-Object -Unique -First 16)){if(Test-Path -LiteralPath $p){$t=(& $p -c $pc 2>&1|Out-String).Trim();try{$m=$t|ConvertFrom-Json}catch{$m=$null};$rows+=@{path=$p;exit=$LASTEXITCODE;metadata=$m;raw=$t}}}
@{hostname=$env:COMPUTERNAME;epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();roots=$inv;python=$rows;readonly=$true;no_Torch_Isaac_or_CUDA_import=$true;no_install_GPU_OS_mutation=$true}|ConvertTo-Json -Depth 12 -Compress
""".replace('__PY__',base64.b64encode(py.encode()).decode())
assert len(code.encode('utf-16le'))*4//3 < 7600, 'keep Windows encoded command bounded'
stamp=str(time.time_ns());a=[];c=connect();out=F/('WINDOWS4090_SDK_COMPACT_READONLY_ACTUAL_'+stamp+'.json')
try:
 for i in range(4):
  try:
   raw=powershell(c,code,120);a.append(dict(attempt=i+1,passed=True,epoch=time.time()));r=json.loads(raw)
   r.update(prior_original_connectionclosed_attempt1=True,prior_compact_command_required_return1_attempt2=True,total_nativeSSH_invocation_cap=6,original_errors_preserved=True,transport_functions_only_imported_no_transport_or_key_source_bytes_read=True,Git_archive_pending_root=True)
   out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
   print(json.dumps(dict(report=str(out),python=r['python']),ensure_ascii=False));break
  except RuntimeError as e:
   a.append(dict(attempt=i+1,passed=False,epoch=time.time(),error=str(e)))
   if not any(s in str(e) for s in ('kex_exchange','banner exchange','MaxStartups','Connection closed by 10.24.4.210 port 22')):raise
   if i==3:raise RuntimeError('Six total native SSH invocations exhausted')
   time.sleep(5)
except BaseException:
 (F/('WINDOWS4090_SDK_COMPACT_READONLY_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_SDK_install_OS_mutation=True),indent=2),encoding='utf8');raise
finally:
 (F/('WINDOWS4090_SDK_COMPACT_CONNECT_RECEIPT_'+stamp+'.json')).write_text(json.dumps(dict(attempts=a,prior_failed_invocations=2,total_call_cap6=True,one_batched_inventory_continuation=True,command_encoded_UTF16_estimated_bytes=len(code.encode('utf-16le'))*4//3,report=str(out) if out.exists() else None),indent=2),encoding='utf8');c.close()
