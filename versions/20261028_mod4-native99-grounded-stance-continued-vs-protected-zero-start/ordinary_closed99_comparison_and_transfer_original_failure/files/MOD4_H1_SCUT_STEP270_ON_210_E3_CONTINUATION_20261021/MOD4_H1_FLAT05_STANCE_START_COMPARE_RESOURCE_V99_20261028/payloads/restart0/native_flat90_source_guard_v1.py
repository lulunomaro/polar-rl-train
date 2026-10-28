"""Exact new flat-task payload inventory; no legacy guard exceptions."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json
from native88C_to_flat_migration_v1 import assert_declared_admission,SOURCE_SHA,SOURCE_PINS,REFERENCE_SHA

CONTRACT='FLAT90_SOURCE_CONTRACT_ACTUAL.json'
MANIFEST='THREE_SLOT_COMPLETE_MANIFEST_V1.json'
METADATA_SHA='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'

def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def require(v,message):
 if not bool(v):raise ValueError(message)
def contained(B,rel):
 root=Path(B).resolve();p=PurePosixPath(rel)
 require(not p.is_absolute() and '..' not in p.parts and '\\' not in rel and ':' not in rel,'unsafe manifest path')
 path=root/rel;require(path.resolve().is_relative_to(root) and not path.is_symlink(),'escaped manifest path')
 return path

def validate_task_go(task,go,manifest_SHA):
 require(task['key']=='h1' and task['execution_backend']=='target72','new single72 flat role')
 require(task['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842','explicit available card')
 require(task['native_reference_SHA']==REFERENCE_SHA and task['source_SHA']==SOURCE_SHA,'flat reference/native source')
 require(go['payload_manifest_SHA']==manifest_SHA and go['num_envs']==4096,'actual source-bound grant')
 require(task.get('logical_slot')=='restart' and task.get('canonical_worker_key')=='h1' and go.get('logical_slot')==task['logical_slot'] and go.get('canonical_worker_key')=='h1','exact physical target alias and native worker ABI')
 return assert_declared_admission('h1',task,go)

def check_payload(B,verify_model_bytes=True):
 B=Path(B).resolve();m=read(B/MANIFEST);c=read(B/CONTRACT);task=read(B/'job0/TASK.json')
 require(c['schema']=='mod4.native.flat05.stance99.restart0.complete_source.v1','new typed flat source schema')
 require(c['source_SHA']==m['source_SHA']==task['source_SHA']==SOURCE_SHA,'source binding')
 require(task['flat05_objective_changed_from_native88C'] and task['changed_plant700_to_nominal400'] is True,'same400 newtask')
 require(task['source_native_contract']==SOURCE_PINS['native_contract'],'exact qualified88C input contract')
 require(task['source_progress']=={'updates': 0, 'world_updates': 0, 'policy_updates': 0},'source global counters')
 require(H(B/CONTRACT)==task['flat_source_contract_SHA'],'contract pin')
 rows={}
 for row in m['files']:
  rel=row['relative'];require(rel not in rows,'duplicate file');rows[rel]=row
  p=contained(B,rel)
  if not verify_model_bytes and p.suffix.lower() in ('.pt','.pth','.npz'):continue
  require(p.is_file() and p.stat().st_size==row['bytes'] and H(p)==row['SHA'],'payload file mismatch '+rel)
  if p.suffix=='.py':ast.parse(p.read_bytes())
 actual={p.relative_to(B).as_posix() for p in B.rglob('*.py')}
 require(actual==set(c['approved_python']),'exact Python inventory required')
 for rel,SHA in c['approved_python'].items():require(rows[rel]['SHA']==SHA,'unapproved Python '+rel)
 for rel,SHA in c['protected_current88C_files'].items():require(rows[rel]['SHA']==SHA,'protected original runtime changed '+rel)
 require(H(B/'same_optimized_source_contract_metadata_candidate_v1.py')==METADATA_SHA and (B/'same_optimized_source_contract_metadata_candidate_v1.py').stat().st_size==2536,'byteexact metadata CRLF')
 require(H(B/task['native_reference_relative'])==REFERENCE_SHA,'own flat reference pin')
 for rel,SHA in c['small_evidence_pins'].items():require(H(contained(B,rel))==SHA,'evidence mismatch')
 return dict(task=task,contract=c,manifest=m,manifest_SHA=H(B/MANIFEST),model_bytes_verified=verify_model_bytes)

def validate_precontrol_actual(runner,env,task,go,B):
 from native88_source_guard_v1 import validate_precontrol_actual as original
 # Original function's only contract-file dependency is its named-order row.
 # Keep original88C contract unchanged in this new payload for that exact check.
 value=original(runner,env,task,go,B)
 value.update(source_native88C400_environment_not_restored=True,
              flat05_task=True,plant_already400=True)
 return value
