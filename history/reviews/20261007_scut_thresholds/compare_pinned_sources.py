"""Fetch primary pinned SCUT text, hash it, and extract audit facts safely."""
from pathlib import Path
import ast,hashlib,json,re,urllib.request
from concurrent.futures import ThreadPoolExecutor

D=Path(__file__).resolve().parent;R=D/'evidence/scut';R.mkdir(parents=True,exist_ok=True)
W=D.parent;COMMIT='b8ff79f3df855faf9dc92f4a282bd80c42649466'
paths=['scripts/rsl_rl/train.py',
 'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py',
 'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py',
 'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py',
 'pretrained/26_infantry/flat_and_rotation/2026-07-29_23-20-03/params/env.yaml',
 'pretrained/26_infantry/flat_and_rotation/2026-07-29_23-20-03/params/agent.yaml']
for stamp in ('2026-07-23_10-19-59','2026-07-23_16-23-21','2026-07-30_09-16-27'):
 paths.append('pretrained/26_infantry/rough_rotation_stair/'+stamp+'/params/env.yaml')
paths.append('pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params/agent.yaml')
def fetch(p):
 url='https://raw.githubusercontent.com/scutrobotlab/wheeled-legged_RL/'+COMMIT+'/'+p
 raw=urllib.request.urlopen(url,timeout=30).read();out=R/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
 candidates=[W/'audits/20260925/scutrobotlab_wheeled-legged_RL'/p,W/'MOD4_SCUT_CLOSURE_REVIEW_20261007/original'/p,W/'MOD4_FULL_DR_ROADMAP_20261006/source_reference'/p]
 compare=[dict(path=str(x),byte_exact=x.read_bytes()==raw) for x in candidates if x.exists()]
 text=raw.decode();keys=('dt','decimation','episode_length_s','termination_duration_enabled','termination_duration_steps','termination_roll_deg','termination_pitch_deg','save_interval','max_iterations','num_steps_per_env')
 lines=[dict(line=i,text=s.strip()) for i,s in enumerate(text.splitlines(),1) if any(re.match(r'\s*'+re.escape(k)+r'\s*:',s) for k in keys)] if p.endswith('.yaml') else []
 functions=[]
 if p.endswith('.py'):
  tree=ast.parse(text)
  for n in ast.walk(tree):
   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in ('_get_dones','_apply_termination_duration','_get_rough_height_offset_curriculum_level','main'):
    chunk=ast.get_source_segment(text,n)
    if n.name!='main' or p.endswith('train.py'):functions.append(dict(name=n.name,line=n.lineno,end_line=n.end_lineno,source=chunk))
 return dict(path=p,url=url,sha256=hashlib.sha256(raw).hexdigest(),local_reference_comparison=compare,saved_config_fields=lines,functions=functions)
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,paths))
(D/'evidence/SCUT_PINNED_SOURCE_AUDIT.json').write_text(json.dumps(dict(commit=COMMIT,rows=rows),indent=2),encoding='utf-8')
for r in rows:print(json.dumps({k:r[k] for k in ('path','sha256','local_reference_comparison','saved_config_fields')},ensure_ascii=False))
