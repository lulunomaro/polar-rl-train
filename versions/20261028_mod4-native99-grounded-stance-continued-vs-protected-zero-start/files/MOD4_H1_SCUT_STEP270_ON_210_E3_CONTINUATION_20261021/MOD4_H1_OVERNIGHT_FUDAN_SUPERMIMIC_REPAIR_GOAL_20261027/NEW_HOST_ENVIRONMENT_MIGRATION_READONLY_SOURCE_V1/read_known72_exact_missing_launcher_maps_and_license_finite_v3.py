"""One <=120s known72 read-only environment inventory. No GPU, PT or ledger."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,socket,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
PIN='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
CODE="\nfrom pathlib import Path\nimport hashlib,json,os,shutil,subprocess,sys,time\nSTART=time.monotonic();ROOT=Path('/home/lc01/Zonglin Li/zonglin2');ENV=ROOT/'envs/mod4';SITE=ENV/'lib/python3.12/site-packages';assert sys.flags.no_site\ndef text(p):\n assert p.resolve().is_relative_to(ROOT)\n with p.open('rb') as f:raw=f.read(262145)\n assert len(raw)<=262144\n return dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'))\nfiles=[ROOT/'run-python-compat.sh',ROOT/'compat/glibc240/copyright']\nfor name in ['__editable___isaaclab_6_1_14_finder','__editable___isaaclab_assets_0_3_4_finder','__editable___isaaclab_rl_0_5_5_finder','__editable___isaaclab_tasks_1_10_9_finder','__editable___isaaclab_visualizers_0_1_0_finder','_cuda_bindings_redirector','cmeel_pth']:files.append(SITE/(name+'.py'))\nfor name in ['isaaclab-6.1.14','isaaclab_assets-0.3.4','isaaclab_rl-0.5.5','isaaclab_tasks-1.10.9','isaaclab_visualizers-0.1.0']:files.append(SITE/(name+'.dist-info')/'direct_url.json')\nrows=[]\nfor p in files:\n if p.is_file():rows.append(text(p))\n else:rows.append(dict(path=str(p),missing_exact_path=True,no_alternative_path_guess=True))\nargv=['/usr/bin/readelf','-l',str(ENV/'bin/python3.12')];r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12)\ntools={x:shutil.which(x) for x in ['tar','gzip','pigz','zstd','conda-pack']}\nprint(json.dumps(dict(epoch=time.time(),scope='missing only exact launcher/registration/loader/license/tool paths; no repeated footprint',rows=rows,source_python_ELF_interpreter=dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),packaging_tool_paths=tools,source_root_available_bytes=shutil.disk_usage(ROOT).free,no_Torch_SDK_GPU_model_raw_ledger_or_source_write=True,elapsed_seconds=time.monotonic()-START,env_inventory=dict(logical_bytes=None,partial_time_bound='not_rescanned'),compat_inventory=dict(logical_bytes=None,partial_time_bound='not_rescanned'))))\n"
def put(n,v):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 put('READONLY_KNOWN72_ENV_PORTABILITY_V3_MISSING_TEXT_ENTRY_ENTERED_ACTUAL.json',dict(epoch=time.time(),PID=os.getpid(),script=str(Path(__file__).resolve()),maximum_remote_seconds=45,no_GPU_or_budget=True))
 wrapper=module('same_compressed_for_runtime_readonly_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();secret=None;t=None
 try:
  sec=module('same_password_in_memory_only_for_runtime_readonly',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  sock=socket.create_connection(('10.24.0.72',22),timeout=15);t=paramiko.Transport(sock);t.banner_timeout=15;t.auth_timeout=15;t.start_client(timeout=15);actual=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert actual==PIN,'PIN_MISMATCH_BEFORE_AUTH';t.auth_password('lc01',secret,fallback=False);secret=None
  print(json.dumps(dict(stage='PINNED_READONLY72_RUNTIME_METADATA',epoch=time.time())),flush=True)
  ch=t.open_session(timeout=15);ch.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -S -c '+shlex.quote(CODE));ch.settimeout(45);out=ch.makefile('rb').read();err=ch.makefile_stderr('rb').read();rc=ch.recv_exit_status();put('KNOWN72_ENV_PORTABILITY_V3_MISSING_TEXT_ORIGINAL_REMOTE_RESULT_ACTUAL.json',dict(returncode=rc,stdout=out.decode(),stderr=err.decode()));assert rc==0,'read-only environment metadata failed'
  v=json.loads(out);put('KNOWN72_ENV_PORTABILITY_V3_MISSING_TEXT_FOOTPRINT_ABI_ACTUAL.json',v);print(json.dumps(dict(actual_returned=True,returncode=rc,elapsed_seconds=v['elapsed_seconds'],env_logical_bytes=v['env_inventory']['logical_bytes'],compat_logical_bytes=v['compat_inventory']['logical_bytes'],env_partial=v['env_inventory']['partial_time_bound'],compat_partial=v['compat_inventory']['partial_time_bound'],no_GPU_model_or_source_writes=True)))
 finally:
  secret=None
  if t:t.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('KNOWN72_ENV_PORTABILITY_V3_MISSING_TEXT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
