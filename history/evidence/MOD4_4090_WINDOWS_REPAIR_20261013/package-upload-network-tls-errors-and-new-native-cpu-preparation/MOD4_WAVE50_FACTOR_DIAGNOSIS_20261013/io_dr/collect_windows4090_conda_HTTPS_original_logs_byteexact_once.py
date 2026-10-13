from pathlib import Path
import sys,json,time,base64,hashlib,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
code=r"""$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$a=@();foreach($n in @('01B_NEW_PYTHON311_CONDA_OFFICIAL_HTTPS.stdout.log','01B_NEW_PYTHON311_CONDA_OFFICIAL_HTTPS.stderr.log')){$p=Join-Path $r ('install_logs\'+$n);$b=[IO.File]::ReadAllBytes($p);$a+=@{path=$p;name=$n;bytes=$b.Length;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower();base64=[Convert]::ToBase64String($b)}};$prefix=Join-Path $r 'env';@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();logs=$a;prefix_exists=(Test-Path -LiteralPath $prefix);prefix_top=@(Get-ChildItem -LiteralPath $prefix -Force -ErrorAction SilentlyContinue|Select-Object Name,Length,Mode);readonly=$true}|ConvertTo-Json -Depth 6 -Compress"""
c=connect();stamp=str(time.time_ns());p=F/('WINDOWS4090_CONDA_HTTPS_ORIGINAL_BYTE_LOG_COLLECTION_'+stamp+'.json')
try:
 raw=powershell(c,code,45);r=json.loads(raw)
 for row in r['logs']:
  b=base64.b64decode(row.pop('base64'));assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
  q=F/('ORIGINAL_REMOTE_CONDA_'+stamp+'_'+row['name']);assert not q.exists();q.write_bytes(b);row['local_byteexact_path']=str(q)
  row['utf8_display']=b.decode('utf8','replace')
 r['no_GPU_task_or_install_or_budget_mutation']=True;p.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),actual=r),ensure_ascii=True))
except BaseException:p.with_name(p.stem+'_READER_ERROR.json').write_text(json.dumps(dict(error=traceback.format_exc(),no_mutation=True),indent=2),encoding='utf8');raise
finally:c.close()
