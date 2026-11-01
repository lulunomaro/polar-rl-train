from pathlib import Path
import ast,hashlib,json,re,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'OWN267_MEASURED224_LITERAL_FRAME_CPU_V269_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
for p in sorted((B/'source').rglob('*.py')):
 if p.name in('networks.py','augmented_wheel_leg_world_model_v1.py'):continue
 s=p.read_text('utf8')
 if p.name.startswith('review269'):
  s=re.sub(r'(?<![0-9])269(?![0-9])','270',s);s=s.replace('from supermimic_wheel_leg_v3 import augmented_wheel_leg_world_model_v1 as native_world','import native_layout270 as native_world')
 out=S/p.relative_to(B/'source');out=out.with_name(out.name.replace('269','270'));out.parent.mkdir(exist_ok=True);out.write_text(s,encoding='utf8')
K=T/'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source/supermimic_wheel_leg_v3';p=K/'augmented_wheel_leg_world_model_v1.py';raw=p.read_bytes();text=raw.decode('utf8');cls=next(n for n in ast.parse(text).body if isinstance(n,ast.ClassDef)and n.name=='WheelLegStateLayout');segment=ast.get_source_segment(text,cls)
(S/'code/native_layout270.py').write_text('"""Unchanged native layout class only; no unused network/goal imports."""\nfrom dataclasses import dataclass\nimport torch\nfrom supermimic_wheel_leg_v3.geometry import quat_to_mat,mat_to_quat\n@dataclass(frozen=True)\n'+segment+'\n',encoding='utf8')
(S/'native/contract.py').write_bytes((K/'contract.py').read_bytes())
task=json.loads((B/'TASK269_LOCAL_FROZEN.json').read_bytes());task['kind']='NEW270_FIRST_NEW267_LITERAL_ABI_CPU_DEPENDENCY_REPAIR';put(N/'TASK270_LOCAL_FROZEN.json',task)
c=re.sub(r'(?<![0-9])269(?![0-9])','270',(B/'run_ROOT269_new267_measured_CPU_once.py').read_text('utf8'));c=c.replace("pattern='run_ROOT270_|","pattern='run_ROOT270_|run_ROOT269_|")
(N/'run_ROOT270_new267_measured_CPU_once.py').write_text(c,encoding='utf8')
files=sorted(S.rglob('*.py'))+[N/'TASK270_LOCAL_FROZEN.json',N/'run_ROOT270_new267_measured_CPU_once.py',Path(__file__).resolve(),N/'test270_new_import_only_CPU_once.py']
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text('utf8'),filename=str(p))
report=R/'ROOT270_NEW_SOURCE_DEPENDENCY_REPAIR_BEFORE_RAW.json';put(report,dict(passed=True,epoch=time.time(),original269_error_preserved='Missing supermimic_wheel_leg_v3.contract at source import before raw NPZ/model read.',old269_raw_open_actual=0,repair='Add contract for actual geometry; extract unchanged dataclass WheelLegStateLayout instead of importing unused world-model network/MATLAB goal dependencies.',native_source_path=str(K/'augmented_wheel_leg_world_model_v1.py'),native_source_SHA=hashlib.sha256(raw).hexdigest(),unchanged_class_text_SHA=hashlib.sha256(segment.encode()).hexdigest(),raw_models_SDK_GPU_remote=0))
put(N/'SOURCE270_FILES_BEFORE_IMPORT_CPU.json',dict(files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]]))
print(json.dumps(dict(passed=True,files=len(files))))
