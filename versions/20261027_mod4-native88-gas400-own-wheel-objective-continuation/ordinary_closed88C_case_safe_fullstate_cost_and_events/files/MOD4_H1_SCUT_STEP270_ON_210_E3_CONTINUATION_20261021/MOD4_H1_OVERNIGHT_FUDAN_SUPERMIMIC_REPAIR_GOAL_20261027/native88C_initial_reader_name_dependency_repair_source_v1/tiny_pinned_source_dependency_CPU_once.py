"""Tiny Python/JSON only. Never load a model or execute old reviewer/fixture."""
from pathlib import Path
import sys,json,hashlib,ast,traceback
D=Path(__file__).resolve().parent;OLD=D.parent/'native88C_exact_reset_bank_lifecycle_source_v1';sys.path[:0]=[str(D),str(OLD)]
import native88_initial_CPU_reader_primitives_v1 as r
assert Path(r.__file__).resolve()==(D/'native88_initial_CPU_reader_primitives_v1.py').resolve()
def put(p,raw):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not isinstance(raw,bytes):raw=json.dumps(raw,indent=2).encode()
 with p.open('xb') as f:f.write(raw)
 return dict(relative=p.name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
def main():
 checks=[]
 def yes(name,fn):
  value=fn();checks.append(dict(name=name,passed=True));return value
 def no(name,fn):
  try:fn()
  except (ValueError,RuntimeError,KeyError) as e:checks.append(dict(name=name,passed=True,rejected=str(e)));return
  raise AssertionError('bad source fixture accepted: '+name)
 root=D/'fixtures/TINY_SOURCE'
 py=b'SCALE=3\ndef multiply(x):return x*SCALE\n';jraw=b'{"source_fixture":true,"value":7}\n'
 a=put(root/'tiny.py',py);b=put(root/'tiny.json',jraw);put(root/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dict(files=[a,b]))
 spec=dict(manifest_SHA=r.H(root/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
 assert r.H(root/'tiny.json')==b['SHA'] and r.read(root/'tiny.json')==dict(source_fixture=True,value=7);checks.append(dict(name='new H/read definitions actual small JSON bytes',passed=True))
 pins=yes('PinnedSource init exact source manifest + Python inventory',lambda:r.PinnedSource(root,spec))
 assert pins.raw('tiny.py')==py and pins.raw('tiny.json')==jraw;checks.append(dict(name='PinnedSource raw Python and JSON exact bytes',passed=True))
 ns=pins.extract('tiny.py',('SCALE','multiply'));assert ns['multiply'](4)==12 and len(pins.extracted)==1;checks.append(dict(name='pure named AST extraction retains source hash record',passed=True))
 no('wrong prepared manifest SHA remains rejected',lambda:r.PinnedSource(root,dict(manifest_SHA='0'*64)))
 # Standalone bad fixtures leave every previous file untouched.
 bad=D/'fixtures/TINY_CHANGED_SOURCE';put(bad/'tiny.py',py.replace(b'SCALE=3',b'SCALE=4'));put(bad/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dict(files=[a]))
 no('changed source bytes remain rejected',lambda:r.PinnedSource(bad,dict(manifest_SHA=r.H(bad/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))))
 extra=D/'fixtures/TINY_EXTRA_PYTHON';put(extra/'tiny.py',py);put(extra/'unapproved.py',b'EXTRA=True\n');put(extra/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dict(files=[a]))
 no('extra Python inventory remains rejected',lambda:r.PinnedSource(extra,dict(manifest_SHA=r.H(extra/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))))
 escape=D/'fixtures/TINY_CONTAINMENT';put(escape/'tiny.py',py);put(escape/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dict(files=[a,dict(relative='../outside.json',SHA='0'*64,bytes=1)]))
 ep=r.PinnedSource(escape,dict(manifest_SHA=r.H(escape/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')))
 no('raw containment guard unchanged',lambda:ep.raw('../outside.json'))
 # Original definitions, including one-initial-load/finite/optimizer guards,
 # remain identical, not mocked or monkeypatched to repair names.
 defs=lambda p:{n.name:ast.dump(n) for n in ast.parse(p.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 before=defs(OLD/'native88_initial_CPU_reader_primitives_v1.py');after=defs(D/'native88_initial_CPU_reader_primitives_v1.py')
 assert set(after)-set(before)=={'H','read'} and all(after[k]==v for k,v in before.items());checks.append(dict(name='all original source validator definitions frozen AST exact',passed=True))
 result=dict(passed=True,count=len(checks),checks=checks,new_primitives_SHA=r.H(D/'native88_initial_CPU_reader_primitives_v1.py'),
  pure_external_dependency=dict(module='native88_closing_protocol_v1.py',path=str(OLD/'native88_closing_protocol_v1.py'),SHA=r.H(OLD/'native88_closing_protocol_v1.py')),
  real_model_or_PT_stat_read_or_hash=False,torch_or_SDK_or_GPU_or_remote=False,old_reviewer_or_fixture_executed=False,
  actual_load_history_from_root=dict(previous_shared_normal86_witness_completed_loads=1,previous_new_FINAL_completed_or_attempted_loads=0,previous_process_exited=True,next_new_purpose_shared_witness_reread_required=1))
 with (D/'TINY_PINNED_SOURCE_DEPENDENCY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(passed=True,count=len(checks),new_primitives_SHA=result['new_primitives_SHA'])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (D/'TINY_PINNED_SOURCE_DEPENDENCY_CPU_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),no_model_or_SDK_execution=True),f,indent=2)
  raise
