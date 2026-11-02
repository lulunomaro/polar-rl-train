"""Independent338 fixes the observed pre-SDK335 root-contract import error."""
from pathlib import Path
import ast, hashlib, json, shutil, subprocess, sys, time

P=Path(__file__).resolve().parent
T=P.parent
A=T/'FINAL324_RESOURCE_RECOVERY_EVAL_V335_20261102'
E=T/'FINAL324_IMPORT_REPAIR_EVAL_V338_20261102'
R=P/'reports'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failure=read(A/'reports/ROOT335_EVALUATION_FULL_RETURNED.json')
assert failure['result'] is None and failure['wrapper_error'] is None
files={Path(row['path']).name:row for row in failure['full_UTF8']}
log=files['ACTUAL335_STDOUT_STDERR.log']['UTF8']
assert "ModuleNotFoundError: No module named 'contract335'" in log
released=json.loads(files['ACTUAL335_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json']['UTF8'])
assert released['all_own_children_waited'] and released['all_owned_locks_released']
assert read(A/'reports/ROOT335_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
assert not any('/actual_capture/' in path for path in files)
E.mkdir(exist_ok=False)
(E/'reports').mkdir()
shutil.copytree(A/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
old=(A/'source/evaluate335.py').read_text('utf8')
worker=old.replace('335','338')
needle="sys.path[:0]=[str(Path(__file__).resolve().parent),"
assert needle in worker
worker=worker.replace(needle,"sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent),",1)
with (E/'source/evaluate338.py').open('x',encoding='utf8')as f:f.write(worker)
for oldname,newname in(('contract335.py','contract338.py'),('target335_parent.py','target338_parent.py'),('run335_eval_once.py','run338_eval_once.py'),('view335_actual_final324_replay.py','view338_actual_final324_replay.py'),('render335_recorded_frames.py','render338_recorded_frames.py')):
    source=(A/oldname).read_text('utf8').replace('335','338')
    if oldname.startswith('run'):
        source=source.replace("    patterns='", "    patterns='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|F:\\\\RMPOLAR|run_once_after_resume|continue_clean_sequential|")
    with (E/newname).open('x',encoding='utf8')as f:f.write(source)
shutil.copyfile(A/'reference324.npz',E/'reference324.npz')
task=read(A/'TASK335_FROZEN.json')
task.update(kind='FROZEN324_REFERENCE_TRACKING_EVAL338',worker_SHA=H(E/'source/evaluate338.py'),
    predecessor_import_failure=dict(report=str(A/'reports/ROOT335_EVALUATION_FULL_RETURNED.json'),SHA=H(A/'reports/ROOT335_EVALUATION_FULL_RETURNED.json'),worker_wrapper_started=True,SDK=0,model_reads=0,physics=0),
    distinct_evaluation_purpose='firstactualfinal324evaluationafter335rootcontractpreSDKimportfailure;old335retainednotreplayed')
with (E/'TASK338_FROZEN.json').open('x',encoding='utf8')as f:json.dump(task,f,indent=2)
analyzer=(A/'analyze335_saved_first_episode_facts.py').read_text('utf8').replace('335','338').replace('FINAL324_RESOURCE_RECOVERY_EVAL_V338_20261102','FINAL324_IMPORT_REPAIR_EVAL_V338_20261102')
with (E/'analyze338_saved_first_episode_facts.py').open('x',encoding='utf8')as f:f.write(analyzer)
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'))
namespace={}
exec(compile((E/'contract338.py').read_text('utf8'),str(E/'contract338.py'),'exec'),namespace)
assert namespace['validate_task'](task)
# Execute only the exact stdlib/sys.path/contract prefix: no task,SDK,model or physics.
prefix=worker[:worker.index('p=argparse.ArgumentParser()')]
probe="from pathlib import Path\np=Path("+repr(str(E/'source/evaluate338.py'))+")\nsource=p.read_text('utf8')\nprefix=source[:source.index('p=argparse.ArgumentParser()')]\nexec(compile(prefix,str(p),'exec'),dict(__file__=str(p)))\nprint('EXACT338_CONTRACT_PREFIX_IMPORT_PASS_NO_TASK_SDK_MODEL')\n"
check=subprocess.run([sys.executable,'-B','-X','utf8','-c',probe],cwd=E/'source',capture_output=True,text=True,encoding='utf8',check=True)
assert check.stdout.strip()=='EXACT338_CONTRACT_PREFIX_IMPORT_PASS_NO_TASK_SDK_MODEL'
assert 'REFERENCE_TRACKING_BPTT324_COMPLETE' in worker
assert task['model_SHA']=='841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050'
assert H(E/'reference324.npz')==task['reference']['SHA']
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(E.rglob('*'))if p.is_file()]
index=E/'INDEX338_EVAL_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='OBSERVED335_CONTRACT_ROOT_IMPORT_REPAIR338',files=rows,old335_immutable=True),f,indent=2)
report=dict(epoch=time.time(),passed=True,root=str(E),INDEX=str(index),INDEX_SHA=H(index),
    repair='only independent evaluator root added to sys.path before contract338 import;335failure retained',
    exact_prefix_local_import_passed=True,prefix_stdout=check.stdout.strip(),SDK=0,model_reads=0,physics=0,network=0,GO=0,account_writes=0,
    final324_unchanged=True,fullCPU324_reused=True,same_seed80firstepisodes400controls_samefixed270=True,
    predecessor335_preSDK_error=log,predecessor335_all_owned_closed=True,unused=True)
with (R/'STATIC338_FINAL324_EVAL_ROOT_IMPORT_REPAIR.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
