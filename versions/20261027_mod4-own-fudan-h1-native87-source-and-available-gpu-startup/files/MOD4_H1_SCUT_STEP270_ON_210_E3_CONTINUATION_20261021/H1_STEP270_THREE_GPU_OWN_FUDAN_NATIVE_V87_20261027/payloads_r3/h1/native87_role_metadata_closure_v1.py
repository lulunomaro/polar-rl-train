"""Role metadata closure only. The original forwarder retains actual verification."""
from pathlib import Path
import hashlib,json,re
RELATIVE='OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'
EXPECTED_SHA='14271a0c033e98c88b434513fff7ad614996a94386e4a6fbbd6b926f319fd621'
EXPECTED=dict(schema='mod4.owner72.source210.control_dependencies.v1',actual_target210_CPU_passed=True,
 host72_original_pin_SHA256='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795',
 DEPS_root='/mnt/mod4_linux_durable_20261013/mod4_owner72_control_deps_v86_20261026',
 target_CPU_receipt_SHA='5b8abc5e3ba023bdd3600ab43145badc77113e69bcfef71d7870089447a88663',
 original_source_receipt_SHA='770a17505e6c25cd70477690d48acd0ae0bb167cc7bad109e48e2ce597b3fd14')
def require(v,message):
 if not v:raise ValueError(message)
def validate_role_metadata_closure(B,task,contract,manifest):
 B=Path(B).resolve();key=task['key'];backend=task['execution_backend']
 if key in ('e2','recovery'):
  require(backend=='target72','target role backend mismatch')
  return dict(passed=True,checked=True,scope='target72_original_loopback_not_required',source_metadata_only=True)
 require(key=='h1' and backend=='source210','source210 is exactly h1')
 pin=task.get('owner_control_dependency_binding_SHA')
 require(pin==EXPECTED_SHA,'h1 Task exact approved control binding SHA required')
 require(contract['candidate_pins'].get(RELATIVE)==pin,'h1 control binding absent from source contract pins')
 rows=[r for r in manifest['files'] if r['relative']==RELATIVE]
 require(len(rows)==1 and rows[0]['SHA']==pin,'h1 control binding exact manifest row required')
 path=B/RELATIVE
 require(path.resolve().is_relative_to(B) and path.is_file() and not path.is_symlink(),'h1 required control binding missing/nonregular')
 raw=path.read_bytes();require(len(raw)==rows[0]['bytes'] and hashlib.sha256(raw).hexdigest()==pin,'h1 binding exact file/manifest/Task bytes required')
 require(json.loads(raw)==EXPECTED,'h1 binding exact historical installed-dependency schema required')
 return dict(passed=True,checked=True,scope='source210_h1_exact_binding_file_manifest_contract_Task',
             binding_SHA=pin,source_metadata_only=True,actual_installed_dependency_verification_pending=True)
