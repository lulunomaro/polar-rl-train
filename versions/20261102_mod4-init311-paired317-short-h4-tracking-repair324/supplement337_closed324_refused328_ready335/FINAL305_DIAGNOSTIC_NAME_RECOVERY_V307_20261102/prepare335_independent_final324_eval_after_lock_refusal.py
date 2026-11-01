"""Prepare a new unused evaluation, preserving consumed328 and final324 unchanged."""
from pathlib import Path
import ast, hashlib, json, shutil, time

P = Path(__file__).resolve().parent
T = P.parent
A = T / 'REFERENCE_TRACKING324_POSTROUND_EVAL_V328_20261102'
E = T / 'FINAL324_RESOURCE_RECOVERY_EVAL_V335_20261102'
R = P / 'reports'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())

failure = read(A / 'reports/ROOT328_EVALUATION_FULL_RETURNED.json')
assert failure['result'] is None and failure['wrapper_error'] is None
texts = {Path(row['path']).name: json.loads(row['UTF8']) for row in failure['full_UTF8'] if row['path'].endswith('.json')}
assert 'BlockingIOError' in texts['ACTUAL328_ORIGINAL_PARENT_ERROR.json']['error']
assert 'ACTUAL328_WORKER_IDENTITY_BEFORE_WAIT.json' not in texts
assert 'PARENT328_ONCE_CONSUMED.json' not in texts
assert texts['ACTUAL328_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json']['all_own_children_waited']
assert texts['ACTUAL328_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json']['all_owned_locks_released']
assert read(A/'reports/ROOT328_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
full = read(T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102/reports/ROOT324_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
assert full['passed'] and full['SHA']=='841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050'
assert full['Pi']==4379 and full['totalWM']==16879
E.mkdir(exist_ok=False)
(E/'reports').mkdir()
shutil.copytree(A/'source', E/'source', ignore=shutil.ignore_patterns('__pycache__'))
oldworker=E/'source/evaluate328.py'
worker=oldworker.read_text('utf8').replace('328','335')
ast.parse(worker)
with (E/'source/evaluate335.py').open('x',encoding='utf8') as f:f.write(worker)
# The copied original evaluator remains as provenance; only evaluate335 executes.
contract=(A/'contract328.py').read_text('utf8').replace('328','335')
with (E/'contract335.py').open('x',encoding='utf8') as f:f.write(contract)
parent=(A/'target328_parent.py').read_text('utf8').replace('328','335')
with (E/'target335_parent.py').open('x',encoding='utf8') as f:f.write(parent)
task=read(A/'TASK328_FROZEN.json')
task.update(kind='FROZEN324_REFERENCE_TRACKING_EVAL335',worker_SHA=H(E/'source/evaluate335.py'),
    predecessor_resource_refusal=dict(report=str(A/'reports/ROOT328_EVALUATION_FULL_RETURNED.json'),SHA=H(A/'reports/ROOT328_EVALUATION_FULL_RETURNED.json'),model_reads=0,worker_started=False),
    distinct_evaluation_purpose='firstactualfinal324evaluationafter328resourcepreSDKrefusal;original328notreplayed')
with (E/'TASK335_FROZEN.json').open('x',encoding='utf8') as f:json.dump(task,f,indent=2,allow_nan=False)
shutil.copyfile(A/'reference324.npz',E/'reference324.npz')

runner=(A/'run328_eval_once.py').read_text('utf8').replace('328','335').replace('MOD4_FROZEN305_EVAL335_','MOD4_FROZEN324_EVAL335_')
start=runner.index("    parent=(T/")
end=runner.index("    patterns=",start)
runner=runner[:start]+'''    assert H(N/'INDEX335_EVAL_SOURCE_TASK_CALLERS_FROZEN.json')==args.caller_index_SHA
    for row in read(N/'INDEX335_EVAL_SOURCE_TASK_CALLERS_FROZEN.json')['files']:
        path=Path(row['path']);assert path.stat().st_size==row['bytes'] and H(path)==row['SHA']
    parent=(N/'target335_parent.py').read_text('utf8')
    import ast;ast.parse(parent)
'''+runner[end:]
runner=runner.replace('import hashlib,importlib.util,json,os,subprocess,sys,time,traceback','import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback')
runner=runner.replace("    task=read(N/'TASK335_FROZEN.json')", "    parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()\n    task=read(N/'TASK335_FROZEN.json')")
runner=runner.replace("    patterns='", "    patterns='watch_w35_resume89aca|watch_postadapt|watch_w35_adaptation_exit|watch_e1_terminal_metadata|E1_actual_qualification|collect_e1_own_case|run335_eval|")
runner=runner.replace("    put('ROOT335_ONCE_CONSUMED_BEFORE_NETWORK.json'", "    put('ROOT335_ONCE_CONSUMED_BEFORE_NETWORK.json'")
assert "p.open('x'" not in runner[:runner.index('    patterns=')]
assert "'--caller-index-SHA'" in runner and "task['model_path']" not in runner
with (E/'run335_eval_once.py').open('x',encoding='utf8') as f:f.write(runner)

templates=T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102'
view=(templates/'view328_actual_final324_replay_template.py').read_text('utf8').replace('328','335')
view=view.replace('PiPLACEHOLDER CriticPLACEHOLDER','Pi4379 Critic4379').replace('policy_updates=0','policy_updates=4379')
view=view.replace('REFERENCE TRACKER: stable0/80 / bothcross0/80; planned goals','REFERENCE TRACKER: planned goals; use saved independent evaluation facts')
with (E/'view335_actual_final324_replay.py').open('x',encoding='utf8') as f:f.write(view)
renderer=(templates/'render328_recorded_frames_template.py').read_text('utf8').replace('328','335')
renderer=renderer.replace("E=N.parent/'REFERENCE_TRACKING324_POSTROUND_EVAL_V335_20261102'",'E=N')
with (E/'render335_recorded_frames.py').open('x',encoding='utf8') as f:f.write(renderer)
analyzer=(P/'analyze334_final324_independent_eval_without_model_reads.py').read_text('utf8')
analyzer=analyzer.replace("'REFERENCE_TRACKING324_POSTROUND_EVAL_V328_20261102'","'FINAL324_RESOURCE_RECOVERY_EVAL_V335_20261102'")
analyzer=analyzer.replace('ROOT328_','ROOT335_').replace('INDEPENDENT328','INDEPENDENT335').replace('ACTUAL334_FINAL324_EVAL328','ACTUAL335_FINAL324_EVAL335')
with (E/'analyze335_saved_first_episode_facts.py').open('x',encoding='utf8') as f:f.write(analyzer)
allpy=sorted(E.rglob('*.py'))
for path in allpy:ast.parse(path.read_text('utf8'))
namespace={}
exec(compile(contract,str(E/'contract335.py'),'exec'),namespace)
assert namespace['validate_task'](task)
assert "from contract335 import" in parent and "source/evaluate335.py" in parent and "RESULT335.json" in parent
assert "from contract328" not in parent and "source/evaluate328.py" not in parent
assert "REFERENCE_TRACKING_BPTT324_COMPLETE" in worker
assert H(E/'reference324.npz')==task['reference']['SHA']
rows=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in [*allpy,E/'TASK335_FROZEN.json',E/'reference324.npz']]
index=E/'INDEX335_EVAL_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),kind='INDEPENDENT335_FINAL324_EVAL_AFTER328_RESOURCE_REFUSAL',files=rows,original328_preserved=True),f,indent=2)
report=dict(epoch=time.time(),passed=True,status='UNUSED_READY_WAIT_ACTUAL_ALL_CONTROLLER_RELEASE_AND_FRESH_CNONE',
    root=str(E),INDEX=str(index),INDEX_SHA=H(index),model_SHA=task['model_SHA'],Pi4379=True,
    predecessor328_preSDK_resource_refusal=True,model_reads_by_failed328=0,physics_by_failed328=0,
    old328_source_INDEX_once_unchanged=True,actual324_complete609finiteCPUreused=True,newCPUdecode=0,
    source_semantics='same frozen328evaluation physics/cost/action/firstepisode/seed,independent335 IDs; localguard extended to actual known watchers; no executed SDK or model',
    model_reads=0,network=0,SDK=0,GO=0,account_writes=0,new_local_watcher=False,
    next='Do not launch whileknownPID30080/create2026-11-02T05:43:59.591873+08:00 W35resume watcher holdsSSH. First readlocalactualexit/release and broadfreshCIM/serialFREE. Then only unused335 with exactINDEXSHA through originalparent private/shared/currentauthority. Do not replay328,normal324,CPU324 or start unchangedtraining.',
    replay_after_eval='run335 returns fullfacts/replay then render335_recorded_frames.py;currentmodelview_image actualpose;analyze335savedfacts;decidetargetedrepair/continuation')
with (R/'STATIC335_NEW_FINAL324_EVAL_AFTER328_RESOURCE_REFUSAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
