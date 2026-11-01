"""Prepare unused independent probes and validate the observed close-classifier fix.

No network, SDK, checkpoint decoding, physics, optimizer, GO or account writes.
"""
from pathlib import Path
import ast, hashlib, importlib.util, json, math, re, shutil, tempfile, time

N=Path(__file__).resolve().parent; T=N.parent
S=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V310_20261102'
E=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102'
D=T/'FINAL_REPORT_CLASSIFICATION_REPAIR_V312_20261102'
def put(path, value):
    with path.open('x',encoding='utf8') as f: json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def write(path,text):
    ast.parse(text)
    with path.open('x',encoding='utf8',newline='\n') as f:f.write(text)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

assert not E.exists() and not D.exists()
E.mkdir();(E/'reports').mkdir();shutil.copytree(S/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(S/'reference305.npz',E/'reference305.npz')
source=(S/'source/evaluate310.py').read_text('utf8').replace('310','311')
source=source.replace("source_model_byte_read_admission=1","source_model_byte_read_admission=0")
source=source.replace('ACTUAL309_ZERO_MODEL_READS','ACTUAL311_ZERO_MODEL_READS')
needle=" real.reset();obs=vec.get_observations();active=torch.ones(80,dtype=torch.bool,device=real.device)"
replacement=needle+"\n initial=goal_state();initial_label=reference.labels(torch.zeros(80,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),real.target305)['state']\n put('ACTUAL311_INITIAL_STATE_BEFORE_CONTROL.json',dict(groups=['defaultzero0to39','referencefullstate40to79'],root_position=initial[0].cpu().tolist(),rotation=initial[1].cpu().tolist(),joint_q=initial[4].cpu().tolist(),joint_dq=initial[5].cpu().tolist(),reference_state=initial_label.cpu().tolist(),original_reset_then_reference_state_write=True,reset_queue_and_PD_memory='original reset only; no inferred exact fullstate restore',comparison_scope='two40env groups from same DR distribution; not matched identical DR draws'))"
assert source.count(needle)==1
source=source.replace(needle,replacement)
# This is a new, unused source; the rejected310 bundle remains byte-for-byte.
(E/'source/evaluate310.py').unlink()
write(E/'source/evaluate311.py',source)
for where in(E,E/'source'):
    old=where/'contract310.py'
    if old.exists():old.unlink()
    write(where/'contract311.py',(S/'contract310.py').read_text('utf8').replace('310','311'))
runner=(S/'run310_probe_once.py').read_text('utf8').replace('310','311')
runner=runner.replace('model_decodes_max=1','model_decodes_max=0').replace('NN_actor_only=True','NN_actor_only=False')
runner=runner.replace("patterns='","patterns='run311_probe|",1)
write(E/'run311_probe_once.py',runner)
task=json.loads((S/'TASK310_FROZEN.json').read_bytes())
task.update(kind='REFERENCE_INITIAL_STATE_PHYSICS_PROBE311',worker_SHA=sha(E/'source/evaluate311.py'))
put(E/'TASK311_FROZEN.json',task)
put(E/'reports/SOURCE311_UNUSED_READY.json',dict(epoch=time.time(),status='UNUSED_PENDING_SHARED_VALIDATION_RELEASE',previous310='shared EX lock rejected; SDK/physics/model/GO zero; consumed once not replayed',worker_SHA=task['worker_SHA'],controls_max=64,physics_max=512,groups='40 originalreset vs40 fullplannedreference0 reset; sameplanned q/dq targets; separate DR draws',model_reads=0,optimizer_steps=0,canonical_writes=0,new_GO=False,physical_changes=False))

D.mkdir();(D/'source').mkdir();(D/'reports').mkdir()
classifier='''"""Distinguish the exact successful305 WM diagnostic from error records."""
from pathlib import Path
import json, math
DIAGNOSTIC='ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json'
METRICS=('H32_position_RMSE_m','H32_Rzz_MAE','one_step_position_RMSE_m','one_step_Rzz_MAE','loss')
def classify_error_reports(directory):
    fatal=[];diagnostic=[]
    for path in sorted(Path(directory).glob('*ERROR*.json')):
        try:
            row=json.loads(path.read_bytes())
            admitted=(path.name==DIAGNOSTIC and row.get('passed') is True
                and 'error' not in row and 'traceback' not in row
                and row.get('source')=='actual own contiguous transitions, fixed startobservedanchor; mask before episode reset'
                and row.get('prediction_uses_no_future_real_depth') is True
                and isinstance(row.get('sample_count'),int) and row['sample_count']>0
                and all(isinstance(row.get(k),(int,float)) and math.isfinite(row[k]) and row[k]>=0 for k in METRICS))
        except (OSError,ValueError,TypeError):admitted=False
        (diagnostic if admitted else fatal).append(str(path))
    return fatal,diagnostic
'''
write(D/'source/report_classification312.py',classifier)
base=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101'
node=(base/'control305/model2050_240_fullstate_slot_node.py').read_text('utf8')
node=node.replace('import three_slot_common_v1 as b','from report_classification312 import classify_error_reports\nimport three_slot_common_v1 as b')
old='errors=[str(f) for f in out.glob("*ERROR*.json")]'
assert node.count(old)==1
node=node.replace(old,'errors,diagnostic_reports=classify_error_reports(out)')
write(D/'source/model2050_240_fullstate_slot_node_UNUSED312.py',node)
collector=(base/'normal305/collect305_tracking_formal_cost_normal900_UNUSED_once.py').read_text('utf8')
collector=collector.replace("B=Path(v['spec']['job_root']);C=B/'control305';end=time.time()+180", "B=Path(v['spec']['job_root']);C=B/'control305';end=time.time()+180\nimport sys;sys.path.insert(0,str(C));from report_classification312 import classify_error_reports")
old="errors=[str(p) for p in (B/'production').glob('*ERROR*.json')]"
assert collector.count(old)==1
collector=collector.replace(old,"errors,diagnostic_reports=classify_error_reports(B/'production')")
write(D/'source/collect_tracking_formal_cost_normal900_UNUSED312.py',collector)
worker=(base/'source/worker305.py').read_text('utf8')
old='ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json'
assert worker.count(old)==1
write(D/'source/worker_tracking_UNUSED312.py',worker.replace(old,'ACTUAL312_H32_PAIRED_REAL_WM_METRICS_BEFORE_PI.json'))

spec=importlib.util.spec_from_file_location('classification312',D/'source/report_classification312.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
receipt=json.loads((base/'reports/ROOT305_NORMAL900_JUMP_FULL_UTF8_AND_FORMAL_ACTUAL.json').read_bytes())
with tempfile.TemporaryDirectory(prefix='mod4_classifier312_') as tmp:
    root=Path(tmp)
    diagnostic=next(r for r in receipt['full_UTF8'] if Path(r['path']).name==old)
    (root/old).write_text(diagnostic['UTF8'],encoding='utf8')
    fatal,metrics=module.classify_error_reports(root)
    assert not fatal and len(metrics)==1 and len(receipt['errors'])==1
    put(root/'ORIGINAL_ERROR.json',dict(error='fixture: real error remains fatal'))
    fatal2,_=module.classify_error_reports(root);assert len(fatal2)==1
    put(root/'UNKNOWN_ERROR.json',dict(passed=True));fatal3,_=module.classify_error_reports(root);assert len(fatal3)==2
    (root/old).write_text('{malformed',encoding='utf8')
    fatal4,_=module.classify_error_reports(root);assert len(fatal4)==3
put(D/'reports/ACTUAL312_ORIGINAL305_REPORT_CLASSIFICATION_VALIDATION.json',dict(epoch=time.time(),passed=True,source_receipt=str(base/'reports/ROOT305_NORMAL900_JUMP_FULL_UTF8_AND_FORMAL_ACTUAL.json'),original_qualified_formal=receipt['qualified_formal'],original_false_preserved=True,actual_worker_RC=receipt['original_node_terminal']['row']['returncode'],actual_final_passed=receipt['final']['passed'],original_error_files=receipt['errors'],new_classification_actual_fatal=0,new_classification_actual_diagnostic=1,real_error_unknown_error_and_malformed_remain_fatal=True,models_read=0,network=0,physical_changes=False,deployed=False,purpose='unused repair assets for future independently frozen training; original305 artifacts unchanged'))
print(json.dumps(dict(passed=True,unused_probe=str(E),classification_repair=str(D),model_reads=0,network=0)))
