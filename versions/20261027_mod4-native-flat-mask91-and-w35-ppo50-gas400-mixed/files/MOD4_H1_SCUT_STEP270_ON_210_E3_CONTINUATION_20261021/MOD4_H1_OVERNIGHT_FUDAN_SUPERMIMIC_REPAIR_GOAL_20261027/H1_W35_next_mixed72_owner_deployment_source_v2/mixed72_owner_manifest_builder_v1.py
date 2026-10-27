"""Seal next owner only after root supplies exact qualified H1 protocol bytes."""
from pathlib import Path
import hashlib,json
FILES=['mixed72_next_finite_owner_authority72_v1.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py','mixed72_next_protocol_v1.py','mixed72_next_bound_cfg_v1.py','mixed72_next_detached_launcher_v1.py','W35_mixed72_protocol_v1.py','W35_mixed72_bound_spec_v1.py','mixed72_owner_manifest_builder_v1.py','h1_next72_protocol.py','W35_first_real_GPU_PPO_metadata_observer_v2.py','W35_shared72_natural_closing_metadata_v2.py']

def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build_owner_manifest(base,exact_qualified_H1_protocol_SHA):
 base=Path(base).resolve()
 assert isinstance(exact_qualified_H1_protocol_SHA,str) and len(exact_qualified_H1_protocol_SHA)==64
 assert H(base/'h1_next72_protocol.py')==exact_qualified_H1_protocol_SHA
 return dict(schema='mod4.mixed72.h1_w35.owner.source.v1',keys=['h1','w35'],H1_qualified_protocol_SHA=exact_qualified_H1_protocol_SHA,
  files=[dict(relative=n,bytes=(base/n).stat().st_size,SHA=H(base/n)) for n in FILES])
