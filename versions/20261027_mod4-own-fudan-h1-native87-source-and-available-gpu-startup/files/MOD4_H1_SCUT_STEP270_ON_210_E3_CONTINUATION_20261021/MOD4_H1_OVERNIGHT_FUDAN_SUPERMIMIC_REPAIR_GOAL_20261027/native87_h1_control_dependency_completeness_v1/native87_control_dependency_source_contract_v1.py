"""Role-specific bundle completeness only; no connection, model, fee or launch."""
from pathlib import Path
import hashlib,json,re
RELATIVE='OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'
DEPS='/mnt/mod4_linux_durable_20261013/mod4_owner72_control_deps_v86_20261026'
HOST_PIN='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
SOURCE_RECEIPT_SHA='770a17505e6c25cd70477690d48acd0ae0bb167cc7bad109e48e2ce597b3fd14'
TARGET_RECEIPT_SHA='5b8abc5e3ba023bdd3600ab43145badc77113e69bcfef71d7870089447a88663'
def require(v,message):
 if not v:raise ValueError(message)
def validate_control_dependency_closure(B,spec,manifest):
 """Require the precise already-approved h1 metadata AND its manifest row.

 This does not assert current remote dependency bytes/connectivity. The unchanged
 forwarder still verifies all actual installed files and pinned72 SSH at send.
 """
 B=Path(B).resolve();key=spec['key'];backend=spec['execution_backend']
 if backend=='target72':
  require(key in ('e2','recovery'),'target72 role mismatch')
  return dict(passed=True,scope='target72_original_loopback',h1_binding_required=False,
              source_metadata_only=True,actual_connection_tested=False)
 require(backend=='source210' and key=='h1','source210 is exactly h1')
 expected=spec.get('owner_control_dependency_binding_SHA')
 require(isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected) is not None,'h1 control binding SHA absent')
 rows=[r for r in manifest['files'] if r['relative']==RELATIVE]
 require(len(rows)==1,'required h1 control binding must have exactly one manifest row')
 p=B/RELATIVE
 require(p.resolve().is_relative_to(B) and p.is_file() and not p.is_symlink(),'required h1 control binding missing/nonregular')
 raw=p.read_bytes();SHA=hashlib.sha256(raw).hexdigest();row=rows[0]
 require(SHA==expected==row['SHA'] and len(raw)==row['bytes'],'h1 control binding manifest/spec byte pin differs')
 value=json.loads(raw)
 require(set(value)=={'schema','actual_target210_CPU_passed','host72_original_pin_SHA256','DEPS_root','target_CPU_receipt_SHA','original_source_receipt_SHA'},'unreviewed binding schema fields')
 require(value['schema']=='mod4.owner72.source210.control_dependencies.v1' and value['actual_target210_CPU_passed'] is True,'actual historical target210 dependency proof absent')
 require(value['host72_original_pin_SHA256']==HOST_PIN and value['DEPS_root']==DEPS,'original pinned72/expanded durable dependency root differs')
 require(value['original_source_receipt_SHA']==SOURCE_RECEIPT_SHA and value['target_CPU_receipt_SHA']==TARGET_RECEIPT_SHA,'approved source/target dependency receipts differ')
 return dict(passed=True,scope='source210_h1_exact_borrowed_HTTP_dependency_metadata',
             h1_binding_required=True,relative=RELATIVE,SHA=SHA,source_metadata_only=True,
             actual_connection_tested=False,actual_installed_dependency_readback_not_repeated=True,
             unchanged_forwarder_actual_dependency_and_host_verification_still_required=True)
