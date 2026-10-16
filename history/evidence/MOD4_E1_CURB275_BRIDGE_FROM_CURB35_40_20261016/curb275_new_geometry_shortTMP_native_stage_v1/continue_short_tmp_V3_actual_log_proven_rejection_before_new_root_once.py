from pathlib import Path
import sys,json,time,traceback
P=Path(__file__).resolve().parent;R=P/'reports';sys.path.insert(0,str(P))
import deploy_bridge275_short_tmp_native_then_original_owner_handoff_v2_once as a
from deploy_bridge275_deferred_existing_owner_native_finite_once import CPU
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 m=json.loads((a.Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());cfg={k:v for k,v in m.items() if k!='files'};cfg.update(manifest_SHA=a.H(a.Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json'),python=a.t.PY,root=a.ROOT,previous_case=a.PREV);put('SHORT_TMP_V3_READER_SOURCE_LOG_INSTEAD_OF_TRACE_DISCLOSURE.json',dict(epoch=time.time(),original_V2_assertion_NVRTC_text_in_Python_exception_failed_before_new_root=True,actual_NVRTC_directory_message_in_preserved_worker_console=True,new_reader_only_checks_actual_console_and_original_error_no_GPU_or_physics_change=True,stdin_newline_explicit_chr10_not_literal_escape=True));put('SHORT_TMP_V3_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=__import__('os').getpid(),actual_alive_only_exclusive_transport=True));c=None
 try:
  c=a.t.connect();create=a.CREATE.replace("assert 'name of directory for temporary files is too long' in error['error']", "assert 'name of directory for temporary files is too long' in (A/'job0/native_WORKER.log').read_text(errors='replace') and 'NVRTC' in error['error']")
  put('SHORT_TMP_V3_ACTUAL_NEW_COPY_RESOURCES.json',a.code(c,a.t.PY,create,a.PREV,a.ROOT,cfg['GPU_UUID']));sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   sf.put(str(a.Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json'),a.ROOT+'/CONTINUATION_COMPLETE_MANIFEST_V2.json');missing=a.code(c,a.t.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());print(json.dumps(dict(missing=[r for r in m['files'] if not (B/r['relative']).is_file() or (B/r['relative']).stat().st_size!=r['bytes'] or hashlib.sha256((B/r['relative']).read_bytes()).hexdigest()!=r['SHA']])))",a.ROOT);put('SHORT_TMP_V3_MISSING_ONLY_UPLOAD.json',missing)
   for r in missing['missing']:
    folder=a.ROOT
    for piece in r['relative'].split('/')[:-1]:
     folder+='/'+piece
     try:sf.stat(folder)
     except FileNotFoundError:sf.mkdir(folder)
    sf.put(str(a.Q/r['relative']),a.ROOT+'/'+r['relative'])
  finally:sf.close()
  put('SHORT_TMP_V3_ALL_TARGET_SOURCE_CPU_ACTUAL.json',a.code(c,a.t.PY,CPU,a.ROOT,timeout=180));source="from pathlib import Path;import sys,json,subprocess;B=Path(sys.argv[1]);assert not (B/'PARENT_CONSOLE.log').exists();p=subprocess.run([sys.argv[2],'-u','-B',str(B/'bridge275_native_then_original_lock_handoff_parent_v2.py')],input=sys.argv[3]+chr(10),text=True,capture_output=True,cwd=B,timeout=30);assert p.returncode==0,p.stderr;print(p.stdout)";owner=a.code(c,a.t.PY,source,a.ROOT,a.t.PY,json.dumps(cfg));put('SHORT_TMP_V3_ACTUAL_NATIVE_TO_ORIGINAL_HANDOFF_DISPATCH.json',dict(epoch=time.time(),parent=owner,root=a.ROOT,source_SHA=cfg['source_SHA'],no_native_or_PPO_pass_inferred=True,no_second_global_cohort_or_other_experts_stopped=True));print(json.dumps(owner),flush=True)
 finally:a.t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('SHORT_TMP_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_replay=True));raise
