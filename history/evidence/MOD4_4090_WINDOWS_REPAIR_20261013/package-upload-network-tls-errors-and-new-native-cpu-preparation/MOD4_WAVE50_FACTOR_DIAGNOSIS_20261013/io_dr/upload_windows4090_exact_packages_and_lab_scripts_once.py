from pathlib import Path
import sys,json,time,hashlib,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr';R=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/recovery4090_windows_CPU';sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
ROOT='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
files=[(R/'TESTED_ISAACLAB_EDITABLE_FOURPKG_SOURCE_20261013.zip','packages/TESTED_ISAACLAB_EDITABLE_FOURPKG_SOURCE_20261013.zip'),(R/'SOURCE459_FULL_TRAINING_ASSETS_D05C_20261013.zip','packages/SOURCE459_FULL_TRAINING_ASSETS_D05C_20261013.zip'),(R/'TESTED_WINDOWS_ABI_REFERENCE_20K_NO_CAP_CHANGE_20261013.zip','packages/TESTED_WINDOWS_ABI_REFERENCE_20K_NO_CAP_CHANGE_20261013.zip')]
files += [(F/n,n) for n in ('windows4090_exact_lab_install_cpu_v1.ps1','extract_three_exact_packages_cpu_v1.py','metadata_full_environment_cpu_admission_v1.py','tested_lab_dependencies_v1.txt')]
c=connect();p=F/('WINDOWS4090_THREE_PACKAGES_UPLOAD_ACTUAL_'+str(time.time_ns())+'.json');r=dict(epoch=time.time(),owner='io_dr',files=[],no_GPU_Kit_PPO_or_budgetwrite=True)
def save():p.write_text(json.dumps(r,indent=2),encoding='utf8')
try:
 r['directory_actual']=json.loads(powershell(c,r"""$ErrorActionPreference='Stop';$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$d=Join-Path $r 'packages';$existed=Test-Path -LiteralPath $d;if(!$existed){New-Item -ItemType Directory -Path $d|Out-Null};@{root=$r;packages_dir=$d;directory_preexisted=$existed;durable_free=(Get-Volume -DriveLetter C).SizeRemaining;no_installed_env_or_GPU_modified=$true}|ConvertTo-Json -Compress""",45));save()
 for source,relative in files:
  expected=hashlib.sha256(source.read_bytes()).hexdigest();remote=ROOT+'/'+relative
  code=r"""$p='__PATH__';if(Test-Path -LiteralPath $p){@{exists=$true;bytes=(Get-Item -LiteralPath $p).Length;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower()}|ConvertTo-Json -Compress}else{@{exists=$false}|ConvertTo-Json -Compress}""".replace('__PATH__',remote)
  before=json.loads(powershell(c,code,45))
  row=dict(source=str(source),remote=remote,bytes=source.stat().st_size,sha256=expected,before=before)
  r['files'].append(row);save()
  if not before['exists'] or before.get('sha256')!=expected:
   assert not before['exists'],'Unexpected partial/otherbyte ownedupload requires independent reviewed continuation'
   started=time.time();upload(str(source),remote,timeout=180);row['upload_wall_seconds']=time.time()-started;save()
  actual=json.loads(powershell(c,code,45));assert actual.get('bytes')==source.stat().st_size and actual.get('sha256')==expected
  row['remote_actual']=actual;row['path_size_SHA_exact']=True;save()
 r['all7_source_payloads_actual_byteSHA_passed']=True;r['not_unpacked_or_installed_or_GPU_admitted_yet']=True;save();print(json.dumps(dict(report=str(p),files=[dict(remote=x['remote'],bytes=x['bytes'],sha256=x['sha256']) for x in r['files']]),ensure_ascii=True))
except BaseException:r['error']=traceback.format_exc();r['unknownpartial_recheck_actual_SHA_before_retry']=True;save();raise
finally:c.close()
