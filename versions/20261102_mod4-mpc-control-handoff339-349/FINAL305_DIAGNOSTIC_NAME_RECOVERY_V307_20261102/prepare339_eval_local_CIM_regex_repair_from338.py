"""Independent339 repairs the observed local338 invalid-regex refusal; no SDK/model."""
from pathlib import Path
import ast, hashlib, json, shutil, subprocess, sys, time

P=Path(__file__).resolve().parent
T=P.parent
A=T/'FINAL324_IMPORT_REPAIR_EVAL_V338_20261102'
E=T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102'
R=P/'reports'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (A/'reports/ROOT338_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
errors=list((A/'reports').glob('ROOT338_ORIGINAL_ERROR_*.json'))
assert len(errors)==1 and 'len(rows)==1' in read(errors[0])['error']
E.mkdir(exist_ok=False)
(E/'reports').mkdir()
shutil.copytree(A/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
worker=(A/'source/evaluate338.py').read_text('utf8').replace('338','339')
with (E/'source/evaluate339.py').open('x',encoding='utf8')as f:f.write(worker)
for oldname,newname in(('contract338.py','contract339.py'),('target338_parent.py','target339_parent.py'),('run338_eval_once.py','run339_eval_once.py'),('view338_actual_final324_replay.py','view339_actual_final324_replay.py'),('render338_recorded_frames.py','render339_recorded_frames.py')):
    source=(A/oldname).read_text('utf8').replace('338','339')
    if oldname.startswith('run'):
        tree=ast.parse(source)
        main=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='main')
        assignment=next(node for node in main.body if isinstance(node,ast.Assign)and any(isinstance(target,ast.Name)and target.id=='patterns'for target in node.targets))
        pattern=ast.literal_eval(assignment.value).replace('F:\\RMPOLAR','RMPOLAR')
        assert '\\' not in pattern
        lines=source.splitlines(keepends=True)
        lines[assignment.lineno-1]='    patterns='+repr(pattern)+'\n'
        source=''.join(lines)
        source=source.replace("    rows=json.loads(q.stdout)","    assert not q.stderr.strip(), q.stderr\n    rows=json.loads(q.stdout)")
    with (E/newname).open('x',encoding='utf8')as f:f.write(source)
shutil.copyfile(A/'reference324.npz',E/'reference324.npz')
task=read(A/'TASK338_FROZEN.json')
task.update(kind='FROZEN324_REFERENCE_TRACKING_EVAL339',worker_SHA=H(E/'source/evaluate339.py'),
    predecessor_local_CIM_failure=dict(report=str(errors[0]),SHA=H(errors[0]),network=0,SDK=0,model_reads=0,physics=0,reason='PowerShell regex unrecognized escape sequence backslashR; original338 retained'),
    distinct_evaluation_purpose='firstactualfinal324evaluationafter335rootimport_and338localCIMregex_failures')
with (E/'TASK339_FROZEN.json').open('x',encoding='utf8')as f:json.dump(task,f,indent=2)
analyzer=(A/'analyze338_saved_first_episode_facts.py').read_text('utf8').replace('338','339').replace('FINAL324_IMPORT_REPAIR_EVAL_V339_20261102','FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102')
with (E/'analyze339_saved_first_episode_facts.py').open('x',encoding='utf8')as f:f.write(analyzer)
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'))
namespace={}
exec(compile((E/'contract339.py').read_text('utf8'),str(E/'contract339.py'),'exec'),namespace)
assert namespace['validate_task'](task)
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
check=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
assert not check.stderr.strip(),check.stderr
rows=json.loads(check.stdout)
if isinstance(rows,dict):rows=[rows]
assert any(row['ProcessId']==__import__('os').getpid()for row in rows)
rows_index=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))if path.is_file()]
index=E/'INDEX339_EVAL_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='OBSERVED338_LOCAL_REGEX_REPAIR339',files=rows_index,old335338_retained=True),f,indent=2)
report=dict(epoch=time.time(),passed=True,root=str(E),INDEX=str(index),INDEX_SHA=H(index),
    observed338error='PowerShell regex unrecognized escape sequence backslashR; qreturncode0,stderrnotempty,rows empty',
    repair='match plain RMPOLAR root token without Windows slash escape; require stderr empty to distinguish queryerror from zero processes',
    actual_local_CIM_test_passed=True,exact_local_processes=rows,root_contract_import_fix_inherited=True,
    old338source_INDEX_report_unchanged=True,network=0,SDK=0,model_reads=0,physics=0,GO=0,account_writes=0,
    final324_unchanged=True,fullCPU324_reused=True,unused=True)
with (R/'STATIC339_FINAL324_EVAL_LOCAL_CIM_REPAIR.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
print(json.dumps({key:value for key,value in report.items()if key!='exact_local_processes'},indent=2))
