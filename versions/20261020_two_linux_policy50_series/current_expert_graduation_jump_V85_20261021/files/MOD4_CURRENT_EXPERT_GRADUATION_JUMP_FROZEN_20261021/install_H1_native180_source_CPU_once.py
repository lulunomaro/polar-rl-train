from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_51_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
REMOTE=r'''
from pathlib import Path
import ast,hashlib,json,time,zipfile,importlib.metadata as md
B=Path(v['root']);z=Path(v['zip']);assert not B.exists() and B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks')) and hashlib.sha256(z.read_bytes()).hexdigest()==v['zip_SHA'];B.mkdir()
with zipfile.ZipFile(z) as a:
 for n in a.namelist():assert (B/n).resolve().is_relative_to(B.resolve())
 a.extractall(B)
m=json.loads((B/'SOURCE_MANIFEST.json').read_bytes());assert m['source_SHA']==v['source_SHA']
for row in m['files']:
 p=B/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
import torch
torch.set_num_threads(1);state=torch.load(B/'job0/source.pt',map_location='cpu',weights_only=False);assert len(state['actor_state_dict'])==9 and len(state['critic_state_dict'])==8 and len(state['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in state['optimizer_state_dict']['state'].values()}=={674740};assert all(torch.isfinite(x).all() for x in list(state['actor_state_dict'].values())+list(state['critic_state_dict'].values())) and not torch.cuda.is_initialized()
out=dict(epoch=time.time(),root=str(B),all_manifest_files_exact=True,source_SHA=m['source_SHA'],source_Adam=674740,actor9_STD_critic8_17Adam_CPU=True,actual_packages={n:md.version(n) for n in ('torch','isaacsim','isaaclab','rsl-rl-lib')},CUDA_not_initialized=True,no_GPU_launch_or_optimizer_or_account_write=True,source_CPU_only_not_SDK_execution_pass=True);(B/'TARGET_SOURCE_CPU_INSTALLED_ACTUAL.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''
try:
 q=json.loads((R/'H1_CURRENT_CLOSED16_JUMP80_PACKAGE_CPU_PREPARED_ACTUAL.json').read_bytes());assert q['passed_source_AST'];root='/home/lc01/Zonglin Li/zonglin2/tasks/GraduationH1_2110v85_native180_v1';remote_zip=root+'.zip';secret=memory.recover();c=d.connect72(secret);secret=None
 try:
  sf=c.open_sftp()
  try:
   try:sf.stat(remote_zip)
   except FileNotFoundError:pass
   else:raise FileExistsError(remote_zip)
   sf.put(q['package']['path'],remote_zip)
  finally:sf.close()
  out=d.code(c,d.PY72,REMOTE,dict(root=root,zip=remote_zip,zip_SHA=q['package']['SHA'],source_SHA=q['source_SHA']),timeout=90)
 finally:c.close()
 (R/'H1_NATIVE180_TARGET_SOURCE_CPU_INSTALLED_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(out,indent=2));print(json.dumps(out))
except BaseException:
 (R/'H1_NATIVE180_INSTALL_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),indent=2));raise
