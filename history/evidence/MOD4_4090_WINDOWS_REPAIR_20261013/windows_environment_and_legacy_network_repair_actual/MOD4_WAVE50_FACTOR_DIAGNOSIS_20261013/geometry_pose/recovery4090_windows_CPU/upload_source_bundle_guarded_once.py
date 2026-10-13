"""Authorized native-SCP CPU source upload with immutable targets and SHA guards.

Transport owns transient authentication. This script never reads/prints key bytes.
"""
from pathlib import Path
import json,time,sys,argparse,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parents[2]
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import windows4090_native_transport as transport
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--receipt',required=True);p.add_argument('--remote',required=True);args=p.parse_args()
M=Path(args.manifest);R=Path(args.receipt);assert not R.exists();m=json.loads(M.read_bytes());source=Path(m['zip']['path']);expected=m['zip']
assert source.stat().st_size==expected['bytes'] and hashlib.sha256(source.read_bytes()).hexdigest()==expected['sha256']
remote=args.remote.replace('\\','/');assert remote.startswith('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/') and remote.endswith('.zip')
esc=lambda s:"'"+s.replace("'","''")+"'"
def remote_actual():
 code="$ErrorActionPreference='Stop';$p="+esc(remote)+";if(Test-Path -LiteralPath $p -PathType Leaf){$f=Get-Item -LiteralPath $p;[ordered]@{exists=$true;path=$p;bytes=$f.Length;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}|ConvertTo-Json -Compress}else{[ordered]@{exists=$false;path=$p}|ConvertTo-Json -Compress}"
 return json.loads(transport.powershell(session,code,timeout=60))
receipt=dict(epoch=time.time(),source=expected,manifest=str(M),remote_path=remote,CPU_source_only=True,no_GPU_training_budget_or_OS_setup=True,transport_owns_auth_private_bytes_not_read=True)
def save(path,value):
 assert not path.exists();path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
session=transport.connect()
try:
 prior=remote_actual();receipt['remote_before']=prior
 if prior['exists']:
  assert prior['bytes']==expected['bytes'] and prior['sha256']==expected['sha256'],'Existing immutable remote path differs; preserve and do not overwrite/reupload'
  receipt['already_exact_no_upload_replayed']=True
 else:
  parent=remote.rsplit('/',1)[0]
  transport.powershell(session,"$ErrorActionPreference='Stop';$p="+esc(parent)+";if(-not(Test-Path -LiteralPath $p)){New-Item -ItemType Directory -Path $p|Out-Null};[ordered]@{new_source_directory=$p;exists=(Test-Path -LiteralPath $p)}|ConvertTo-Json -Compress",timeout=60)
  save(R.with_name(R.stem+'_INTENT.json'),dict(epoch=time.time(),source=expected,remote_path=remote,actual_before=prior,upload_attempt_consumed_now=True,no_overwrite=True))
  try:
   transport.upload(source,remote,timeout=300);receipt['native_SCP_returned_success']=True
  except BaseException:
   receipt['native_SCP_original_error']=traceback.format_exc();receipt['outcome_unknown_before_actual_SHA_read']=True
  current=remote_actual();receipt['remote_after']=current
  assert current['exists'] and current['bytes']==expected['bytes'] and current['sha256']==expected['sha256'],'Remote source incomplete or unknown; preserve original target and do not blindly resend'
 receipt['actual_remote_bytes_SHA_exact']=True;receipt['completed_epoch']=time.time();save(R,receipt)
 print(json.dumps(dict(receipt=str(R),remote=remote,bytes=expected['bytes'],sha256=expected['sha256'],actual_remote_SHA_exact=True),ensure_ascii=False),flush=True)
except BaseException:
 receipt['error']=traceback.format_exc();receipt['original_target_retained_no_reupload']=True
 E=R.with_name(R.stem+'_ORIGINAL_ERROR.json');save(E,receipt);print(json.dumps(dict(error_report=str(E),source_only_no_GPU=True)),flush=True);raise
finally:session.close()
