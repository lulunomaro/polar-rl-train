"""New namespace only: correct Warp read-only capture and reaped-child observer."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,tarfile,time
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
OLD=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_20261027'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=L/'native87R5_frozen_step_acceptance_preparation_v2_own_pid_only'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 R.mkdir(exist_ok=True);code=S/'code';code.mkdir()
 own=json.loads((OLD/'reports/MISSING_ONLY_OWN_FIRST_CASE_ERROR_AND_ALLOUT_RETURNED_ACTUAL.json').read_bytes())
 assert own['canonical_None'] and own['own_pid_evidence']==[dict(pid=515220,actual_original_own_PID_out=True)]
 status=json.loads((OLD/'missing_actual72/seed_20260928/episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json').read_bytes())
 assert status['controls']==0 and status['physics_callbacks']==0
 q=json.loads((OLD/'BINDING.json').read_bytes());oldroot=q['eval_root'];newroot=oldroot.replace('fixed3_diagnostic_','fixed3_diagnostic_r2_')
 q['eval_root']=newroot;q['runtime_root']=newroot+'/runtime'
 olddriver=(P/'native87R5_frozen_acceptance_driver_v1.py').read_bytes()
 text=olddriver.decode('utf8');key="forces=t(e.h1_sensor.contact_view.get_net_contact_forces(dt=float(e.physics_dt))).reshape(1,31,3)"
 replacement="forces=__import__('h1_fullstate_environment_v1').tensor(e.h1_sensor.contact_view.get_net_contact_forces(dt=float(e.physics_dt))).reshape(1,31,3)"
 assert text.count(key)==1
 fixed=text.replace(key,replacement,1)
 # Strict existing DR tensor helper remains unmodified. Only this known Warp-returning sensor uses the original H1 adapter.
 for name in q['eval_code_pins']:
  raw=fixed.encode('utf8') if name=='native87R5_frozen_acceptance_driver_v1.py' else (P/name).read_bytes()
  with (code/name).open('xb') as f:f.write(raw)
  q['eval_code_pins'][name]=hashlib.sha256(raw).hexdigest()
 put(S/'BINDING.json',q)
 files=json.loads((OLD/'INPUT_TRANSFER_INDEX.json').read_bytes())['files']
 for row in files:
  if row['relative']=='BINDING.json':row.update(local=str(S/'BINDING.json'),bytes=(S/'BINDING.json').stat().st_size,SHA=H(S/'BINDING.json'))
  elif row['relative'].startswith('code/'):
   p=code/Path(row['relative']).name;row.update(local=str(p),bytes=p.stat().st_size,SHA=H(p))
 changed=[r for r in files if r['relative']=='BINDING.json' or r['relative'].startswith('code/')]
 with tarfile.open(S/'NEW_CODE_AND_BINDING_INPUTS.tar','x') as tar:
  for row in changed:tar.add(row['local'],arcname=row['relative'],recursive=False)
 archive=dict(path=str(S/'NEW_CODE_AND_BINDING_INPUTS.tar'),bytes=(S/'NEW_CODE_AND_BINDING_INPUTS.tar').stat().st_size,SHA=H(S/'NEW_CODE_AND_BINDING_INPUTS.tar'))
 put(S/'INPUT_TRANSFER_INDEX.json',dict(files=files,archive=archive,exact_old_eval_runtime_private_copy_source=oldroot,new_code_binding_only_upload=True))
 parent=(OLD/'run_native87R5_old700_three_fixed_frozen_diagnostics_once.py').read_text('utf8')
 spec=importlib.util.spec_from_file_location('old700_parent_definitions_no_main',OLD/'run_native87R5_old700_three_fixed_frozen_diagnostics_once.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 prep=m.PREP.replace("root.mkdir()", """root.mkdir()
source=Path('"""+oldroot+"""');assert source.is_dir()
try:
 p=psutil.Process(515220);assert p.create_time()>1793073523,'original first case still exists'
except psutil.NoSuchProcess:pass
for row in v['files']:
 rel=row['relative']
 if not rel.startswith(('runtime/','evidence/','qualified_model/')):continue
 original=(source/rel).resolve();target=(root/rel).resolve()
 assert original.is_relative_to(source.resolve()) and target.is_relative_to(root.resolve()) and original.is_file() and not original.is_symlink()
 assert original.stat().st_size==row['bytes'] and not target.exists()
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
""")
 run=m.RUN
 a=run.index('with tarfile.open(');z=run.index('# All current exact',a)
 block=run[a:z]
 newblock=block.replace("expected={", "expected={")
 newblock=newblock.replace("len(members)==len(expected) and {m.name for m in members}==set(expected)","{m.name for m in members}=={x for x in expected if x=='BINDING.json' or x.startswith('code/')}")
 run=run[:a]+newblock+run[z:]
 start="    p=psutil.Process(child.pid);assert p.create_time()==own['creation']\n"
 end="    time.sleep(.25)\n"
 a=run.index(start);z=run.index(end,a)
 original=run[a:z]
 corrected="    try:\n"+''.join(' '+line+'\n' for line in original.splitlines())+"    except (psutil.NoSuchProcess,psutil.ZombieProcess):\n     break\n"
 run=run[:a]+corrected+run[z:]
 ast.parse(prep);ast.parse(run)
 parent=parent.replace('PREP='+repr(m.PREP),'PREP='+repr(prep)) if False else parent
 # Replace only top-level constant spans using AST line boundaries, no quote heuristics.
 lines=parent.splitlines(keepends=True);tree=ast.parse(parent)
 for name,value in reversed([('PREP',prep),('RUN',run)]):
  n=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
  lines[n.lineno-1:n.end_lineno]=[name+'='+repr(value)+'\n']
 parent=''.join(lines).replace("dict(q=q),timeout=45","dict(q=q,files=index['files']),timeout=60")
 parent=parent.replace("pre=d.code(c,d.PY72,PREP,dict(q=q,files=index['files']),timeout=60)","pre=d.code(c,d.PY72,PREP,dict(q=q,files=index['files']),timeout=60)")
 ast.parse(parent)
 with (S/'run_native87R5_old700_r2_fixed_frozen_diagnostics_once.py').open('x',encoding='utf8') as f:f.write(parent)
 # New bounded source tests: actual adapter AST handles Warp via original source,
 # and the observer always reaches child.wait after a disappearance/zombie race.
 original_sensor=(T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1/job0/runtime/isaac/mod4/h1_fullstate_environment_v1.py').read_bytes()
 fn=next(n for n in ast.parse(original_sensor).body if isinstance(n,ast.FunctionDef) and n.name=='tensor')
 assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='to_torch' for n in ast.walk(fn))
 restored=fixed.replace(replacement,key,1);assert restored==text
 assert "except (psutil.NoSuchProcess,psutil.ZombieProcess)" in run and "rc=child.wait()" in run
 assert 'process_iter' not in run+prep
 put(R/'R1_ZERO_ACTION_SOURCE_ERROR_AND_R2_EXACT_FIX_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,source_scope_only=True,original_error_preserved=True,original_case_controls=0,original_case_physics_callbacks=0,no_original_actor_forward=True,exact_H1_Warp_adapter_source_SHA=hashlib.sha256(original_sensor).hexdigest(),strict_DR_tensor_helper_unchanged=True,only_driver_contact_conversion_changed=True,original_child_zombie_race_handled_then_waited=True,new_eval_namespace=newroot,no_runtime_or_model_opened_here=True,remaining_fixed_seeds_unchanged=q['seeds'],not400N_hardware_acceptance=True))
 print(json.dumps(dict(prepared=True,upload_bytes=archive['bytes'],runtime_model_private_copy_from_exact_R1=True,actor_not_run=True)))
if __name__=='__main__':main()
