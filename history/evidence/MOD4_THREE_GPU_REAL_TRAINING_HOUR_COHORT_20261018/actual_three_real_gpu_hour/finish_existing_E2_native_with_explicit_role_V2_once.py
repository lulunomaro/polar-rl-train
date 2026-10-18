"""Finish the already installed unused target; V1 wrapper rejected missing role before any child."""
import deploy_E2_210_new_fullstate_native_before_three_training_handoff_once as d
from pathlib import Path
import json,time,os,sys,traceback
def main():
 d.put('E2_NATIVE_V2_EXPLICIT_ROLE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,V1_missing_role_before_any_child=True,original_failure_retained=True));c=None
 try:
  c=d.a.t.connect();proof=d.a.code(c,d.a.t.PY,"from pathlib import Path;import json,psutil,os;B=Path("+repr(d.TARGET)+");assert not (B/'native_only_CONSOLE.log').exists() and not (B/'job0/native').exists();alive=[p.info for p in psutil.process_iter(['pid','cmdline']) if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or [])];assert not alive;print(json.dumps(dict(actual_no_parent_worker_native_GO=True,installed_target_reused_no_reupload=True)))",timeout=60);d.put('E2_NATIVE_V2_ACTUAL_UNUSED_INSTALLED_TARGET_PROOF.json',proof);prep=json.loads((d.R/'E2_SOURCE210_EXISTING_FULLSTATE_ONE_HOUR_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());cfg=dict(role='native_only',root=d.TARGET,GPU_UUID=d.d.S['E2']['GPU_UUID'],private_lock=d.d.S['E2']['actual_existing_private_lock'],python=d.a.t.PY,source_SHA=prep['source_SHA'],manifest_SHA=prep['manifest']['SHA']);from dispatch_new_fe778_frozen210_native120_after_E2_full_out_once import old
  parent=old.d.launch(d.a.code,c,d.a.t.PY,d.TARGET,'fullstate_native_only_finite_parent_v1.py',cfg);d.put('E2_SOURCE210_NEW_FULLSTATE_NATIVE144_V2_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=parent,root=d.TARGET,cfg=cfg,no_new_canonical_writer_GO_or_charge=True,H1_current_training_not_changed=True));print(json.dumps(dict(E2_native_actual_dispatched=True,parent=parent,H1_untouched=True)),flush=True)
 finally:
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:d.put('E2_NATIVE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_no_repeat=True));raise
