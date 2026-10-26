"""Preserve81N preGO import refusal; snapshot small pure-Python dependencies in new81O."""
from pathlib import Path
import ast
import hashlib
import importlib.metadata as md
import importlib.util
import json
import shutil
import time

H=Path(__file__).resolve().parent;T=H.parent
N=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81N_20261026'
O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026'
assert not O.exists();shutil.copytree(N,O,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
read=lambda p:json.loads(Path(p).read_bytes())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
errors=list((N/'reports').glob('THREE_EXPERT_DEPLOY_ORIGINAL_ERROR_*.json'));assert len(errors)==1
assert 'ModuleNotFoundError' in read(errors[0])['error'] and 'rich' in read(errors[0])['error']
assert not (N/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').exists()
deps=O/'payloads/e2/source/sm_deps';deps.mkdir()
versions={}
for distribution,module in [('rich','rich'),('pygments','pygments'),('markdown-it-py','markdown_it'),('mdurl','mdurl')]:
    dist=md.distribution(distribution);versions[distribution]=dist.version
    src=Path(importlib.util.find_spec(module).submodule_search_locations[0])
    shutil.copytree(src,deps/module,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    target=deps/(distribution.replace('-','_')+'-'+dist.version+'.dist-info');target.mkdir()
    for f in dist.files or []:
        text=str(f).replace('\\','/')
        if '.dist-info/' in text and any(part in text.upper() for part in ('LICENSE','COPYING','METADATA','WHEEL')):
            p=Path(dist.locate_file(f));out=target/text.split('.dist-info/',1)[1]
            if p.is_file():out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
bridge=O/'payloads/e2/source/h1_supermimic_bridge_v1.py';s=bridge.read_text('utf8')
assert s.count('from pathlib import Path\n')==1
s=s.replace('from pathlib import Path\n',"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent/'sm_deps'))\n",1);bridge.write_text(s,'utf8')
qpath=O/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json';q=read(qpath)
for key in ('h1','e2','recovery'):
    q['payloads'][key]=str(O/'payloads'/key);q['roots'][key]=q['roots'][key].replace('2610v81n','2610v81o')
    B=O/'payloads'/key;m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');oldrows={r['relative']:r for r in m['files']}
    if key!='e2':
        role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
        p=B/role;p.write_text(p.read_text('utf8').replace('AUTH_81N_ACTUAL.json','AUTH_81O_ACTUAL.json'),'utf8')
        oldauth=B/'THREE_EXPERT_V8_LIFETIME_DIAG_CONTINUATION_AUTH_81N_ACTUAL.json';auth=read(oldauth)
        auth.update(guard_SHA=sha(p),new_unused_namespace81O_after_prior_preGO_dependency_refusal=True)
        (B/'THREE_EXPERT_V8_LIFETIME_DIAG_CONTINUATION_AUTH_81O_ACTUAL.json').write_text(json.dumps(auth,indent=2),'utf8')
    task=read(B/'job0/TASK.json');task['id']=task['id'].replace('RESOURCE_V81N_','RESOURCE_V81O_');(B/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
    rows=[]
    for p in sorted(B.rglob('*')):
        if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
        rel=p.relative_to(B).as_posix()
        if p.suffix=='.py':ast.parse(p.read_text('utf8'))
        digest=oldrows[rel]['SHA'] if p.suffix in ('.pt','.npz','.usd','.stl') else sha(p)
        rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
    m['files']=rows;(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),'utf8');q['specs'][key]['manifest_SHA']=sha(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
q['owner_root']=q['owner_root'].replace('2610v81n','2610v81o');qpath.write_text(json.dumps(q,indent=2),'utf8')
for name in ['deploy_actual_mixed81n_H1_method_original_writer_unused_once.py','collect_actual_mixed81n_PPO_and_H1_native_policy_first_finite_unused_once.py','collect_actual_mixed81m_finals_original_cost_unused_once.py','e2_target72_same_backend_install_source_v1.py']:
    source=(N/name).read_text('utf8');source=source.replace('RESOURCE_V81N_','RESOURCE_V81O_').replace('2610v81n','2610v81o').replace('MIXED81N_ACTUAL_GO','MIXED81O_ACTUAL_GO')
    target=name.replace('mixed81n','mixed81o').replace('mixed81m','mixed81o')
    (O/target).write_text(source,'utf8')
# The inherited deployer/source files for81N stay as unselected history; only81O exact entries run.
with (H/'reports/ACTUAL81N_PREGO_RICH_DEPENDENCY_REFUSAL_AND_ISOLATED81O_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_error=read(errors[0]),prior81N_no_owner_node_GO_or_fee=True,new_unused_namespace=str(O),dependencies=versions,dependency_python_files=sum(1 for p in deps.rglob('*.py')),dependency_bytes=sum(p.stat().st_size for p in deps.rglob('*') if p.is_file()),source='existing local CPU-test pure-Python installed distributions and licenses; no target global install or model weights',original_algorithm_update_source_unchanged=True,H1_E3_guards_only_auth_filename_changed=True,metadata_CRLF_bytes_retained=True,no_runtime_hotpatch_or_refund=True),f,indent=2)
print(json.dumps(dict(new81O_isolated_dependencies_ready=True,versions=versions,no_GO=True)))
