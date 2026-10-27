from pathlib import Path
import json,hashlib
OWNER_FILES=['W35_single72_finite_owner_authority72_v2.py','W35_single72_protocol_v2.py','W35_single72_bound_cfg_v2.py','W35_single72_detached_launcher_v2.py','W35_single72_install_manifest_v2.py','W35_mixed72_protocol_v1.py','W35_mixed72_bound_spec_v1.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py']
NODE_FILES=['W35_mixed72_protocol_v1.py','W35_mixed72_bound_spec_v1.py','W35_mixed72_finite_node_v1.py','W35_mixed72_resource_guard_v1.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py']
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def manifest(base,names):
 base=Path(base);return dict(schema='mod4.W35.fixed92.controller.source.v2',key='w35',source_SHA='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393',worker_SHA='0ec27aae56bba060bac4ca1b68c5e977ad89da6c6abda0272bc46596460b6254',files=[dict(relative=n,bytes=(base/n).stat().st_size,SHA=H(base/n)) for n in names])
def validate_owner_manifest(base,sha):
 base=Path(base).resolve();p=base/'W35_FIXED92_OWNER_COMPLETE_MANIFEST_V2.json';assert H(p)==sha;m=json.loads(p.read_bytes())
 for r in m['files']:
  q=(base/r['relative']).resolve();assert q.is_relative_to(base) and not q.is_symlink() and q.stat().st_size==r['bytes'] and H(q)==r['SHA']
 return True
