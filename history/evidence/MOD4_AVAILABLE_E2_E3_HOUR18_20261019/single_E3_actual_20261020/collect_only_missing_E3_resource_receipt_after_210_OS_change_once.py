"""Collect only the E3 receipt missing from the failed two-host preflight."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
import check_two_available_resources_and_original_owner_finite_once as pre
d=pre.d;B=d.B;R=d.R
def main():
 assert not (R/'MISSING_E3_RESOURCE_READER_STARTED_ACTUAL.json').exists();assert (R/'AVAILABLE_TWO_RESOURCE_PREFLIGHT_ORIGINAL_ERROR.json').exists();v=json.loads((R/'TWO_AVAILABLE_SOURCE_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());d.put('MISSING_E3_RESOURCE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_finite_alive_only_exclusive_all_transport=True,only_missing_E3_receipt_no_210_retry=True));pw=getpass.getpass('72 missing E3 resource receipt only (hidden): ');c=None
 try:c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);out=d.a.code(c,d.a.PY,pre.READ,json.dumps(v),'recovery',timeout=60)
 finally:
  pw=None
  if c:c.close()
 out['actual_finite_transport_returned']=True;d.put('AVAILABLE_E3_RESOURCE_AFTER_210_OS_CHANGE_ACTUAL.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:d.put('MISSING_E3_RESOURCE_READER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_210_key_bypass_or_GPU_account_write=True));raise
