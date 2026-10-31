from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports';S=N/'source'
p=N/'run_ROOT230_candidate225_physical_regression_once.py'
original=p.read_text(encoding='utf8');D=N/'draft_before_use';D.mkdir(exist_ok=False)
(D/p.name).write_text(original,encoding='utf8')
assert 'e6291fc50e692b9921dfe8ddcbfcc678e9b5916441230c2fd7a4f2c2cc75a538' in original
s=original.replace('e6291fc50e692b9921dfe8ddcbfcc678e9b5916441230c2fd7a4f2c2cc75a538','17696bc47c494ba84a0bd872c4e9be9595410045e90f9abd1a1949d701e9cbaf')
s=s.replace(" task=read(S/'TASK230.json');pack=read(S/'PACKAGE230_SOURCE_AND_TASK.json')", " task=read(S/'TASK230.json');pack=read(S/'PACKAGE230_SOURCE_AND_TASK.json')\n copyproof=read(task['candidate_CPU_report']);assert copyproof['passed'] and copyproof['candidate']['SHA']==task['model_SHA'] and copyproof['candidate']['bytes']==task['model_bytes'] and copyproof['all17_steps_LR_preserved']")
s=s.replace('run_ROOT230_original_action_closure_metadata_once','run_ROOT230_candidate225_physical_regression_once')
ast.parse(s);p.write_text(s,encoding='utf8')
# Verify every selected remote Python file, contract, task and package before use.
for q in S.glob('*.py'):ast.parse(q.read_bytes(),filename=str(q))
task=json.loads((S/'TASK230.json').read_bytes())
ns={};exec(compile((S/'contract230.py').read_text(encoding='utf8'),'contract230','exec'),ns);assert ns['validate_task'](task)
rejected=0
for field,value in [('model_SHA','0'*64),('num_envs',1),('current_authority_binding',{'kind':'EXACT_ORIGINAL219_OWNER_GO'}),('training_reward_changed',True)]:
 bad=dict(task,**{field:value})
 try:ns['validate_task'](bad)
 except AssertionError:rejected+=1
assert rejected==4
report=dict(epoch=time.time(),passed=True,source_AST=True,typed_task=True,rejections=4,original_pre_use_caller_preserved=str(D/p.name),pre_use_issue='Broad phase-label substitution altered embedded old SHA; corrected exact new candidate identity before any caller execution/network. CIM basename now exact selected caller.',model_raw_SDK_remote_reads=0)
(R/'ROOT230_PRE_USE_SOURCE_IDENTITY_AND_Task_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
