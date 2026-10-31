"""New narrow closure/source metadata purpose; preserve228 wrapped-source false."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;O=T/'E0_ACTUAL_ACTION_OPTIMIZER_BINDING_METADATA_V228_20261101'
N=T/'E0_ORIGINAL_ACTION_CLOSURE_METADATA_V229_20261101';assert N.is_dir();S=N/'source';assert S.is_dir();R=N/'reports';assert R.is_dir()
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
def source(p,s):ast.parse(s);p.write_text(s,encoding='utf8')
old=json.loads((O/'reports/ROOT228V2_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json').read_bytes());assert old['passed_execution']
prior=old['original_parent']['result']['proof'];assert not prior['actual_original_action_term_verified']
assert json.loads((S/'PRIOR228_ACTUAL_OPTIMIZER_IDENTITY.json').read_bytes())['proof']==prior
s=(O/'source_V2_FLOAT_FIRST/evaluate228_action_optimizer_metadata_UNUSED_once.py').read_text('utf8')
prefix=s[:s.index(' method=legs.process_actions;')].replace('228','229')
worker=prefix+''' method=legs.process_actions;cells=dict(zip(method.__func__.__code__.co_freevars,[c.cell_contents for c in method.__func__.__closure__]))
 original=cells['original_process'];assert original.__self__ is legs
 assert original.__func__ is type(legs).process_actions
 p=Path(inspect.getsourcefile(original));raw=p.read_bytes();text=raw.decode('utf8')
 guard='torch.maximum(pa[:, 0], pa[:, 1] + self.diff_min'in text and 'torch.minimum(pa[:, 0], pa[:, 1] + self.diff_max'in text
 old=json.loads((P/'PRIOR228_ACTUAL_OPTIMIZER_IDENTITY.json').read_bytes())['proof']
 assert old['policy_order']==order and old['leg_scales']==scales and old['leg_default_offsets']==offsets and old['diff_min']==diff_min and old['diff_max']==diff_max
 proof=dict(old,actual_original_action_term_verified=bool(guard),actual_SDK_source_SHA=hashlib.sha256(raw).hexdigest(),
  original_process_receiver_verified=True,original_process_qualname=original.__qualname__,wrapper_qualname=method.__qualname__,
  prior_actual_optimizer_binding_preserved=True,NN_constructors_in_this_purpose=0,model_reads_in_this_purpose=0)
 assert proof['actual_original_action_term_verified']
 result=dict(passed=True,kind=KIND,proof=proof,actual_original_action_source=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=text,byte_reads=1),
  model_byte_reads=0,model_decodes=0,NN_constructors=0,neural_forwards=0,optimizer_steps=0,account_writes=0,controls=0,
  previous228_false_not_overwritten=True,output_repair_applied=False)
 put('CAPTURE229_ACTUAL_RESULT.json',result);print(json.dumps(dict(passed=True,actual_original_action_term_verified=True)),flush=True)
except BaseException:
 put('ORIGINAL229_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV229_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV229_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:
  put('APP229_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_not_required_or_fabricated=True));ns['app'].close()
  put('APP229_CLOSE_RETURNED_IF_REACHED.json',dict(returned=True))
'''
source(S/'evaluate229_action_optimizer_metadata_UNUSED_once.py',worker)
for oldname in ('contract228.py','target228_single_N1_parent_UNUSED.py','zonglin2_app_launcher.py'):
 p=O/'source_V2_FLOAT_FIRST'/oldname
 source(S/oldname.replace('228','229'),p.read_text('utf8').replace('228','229'))
t=json.loads((O/'source_V2_FLOAT_FIRST/TASK228.json').read_bytes());t.update(kind=t['kind'].replace('228','229'),epoch=time.time(),necessity='New original_process closure receiver and class-method source proof;reuse prior actual optimizer-ID metadata,not new NN.',worker_SHA=hashlib.sha256((S/'evaluate229_action_optimizer_metadata_UNUSED_once.py').read_bytes()).hexdigest(),reader_adapter='NEW229_ORIGINAL_CLOSURE')
put(S/'TASK229.json',t)
caller=(O/'run_ROOT228V2_action_optimizer_metadata_once.py').read_text('utf8')
caller=caller.replace("S=N/'source_V2_FLOAT_FIRST'","S=N/'source'").replace('228V2','229').replace('228','229')
caller=caller.replace("read(T/'W35_FULL_RM70_CLOSED_SKILL_SOURCE_V222_20261101/reports/ROOT222_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')", "read(T/'E0_ACTUAL_ACTION_OPTIMIZER_BINDING_METADATA_V228_20261101/reports/ROOT228V2_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')")
caller=caller.replace('NN_constructors_for_optimizer_identity=2','NN_constructors_for_optimizer_identity=0')
source(N/'run_ROOT229_original_action_closure_metadata_once.py',caller.replace('run_ROOT229_action_optimizer_metadata_once','run_ROOT229_original_action_closure_metadata_once'))
rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(S.iterdir())if p.is_file()]
put(S/'PACKAGE229_SOURCE_AND_TASK.json',dict(epoch=time.time(),files=rows,model_asset_copies=0))
put(R/'SOURCE229_NECESSARY_CLOSURE_METADATA_FROZEN.json',dict(epoch=time.time(),original228V2_execution_passed=True,original228V2_guard_flag_false_preserved=True,
 necessity='Installed D4 action process is a wrapper invoking captured original_process;look up exact closure receiver and original class method,not assert guard text in wrapper file.',
 target_source_file_reads=1,prior_small_metadata_reads=1,target_models_NN_forward_optimizer_steps=0,source_preparation_model_or_SDK_calls=0))
print(json.dumps(dict(passed=True,source_files=len(rows),source_root=str(N),models_read=0)))
