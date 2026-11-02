"""Bounded read-only new reward/command audit source acquisition.
Read own sealed install manifests and direct mod4 Python plus config only.
No selected models, binary banks, raw logs, SDK/GPU/GO/locks/canonical access.
"""
from pathlib import Path,PurePosixPath
import sys,json,hashlib
R=Path(__file__).resolve().parent;D=R/'discovery/reward_command_audit_v1';report=R/'reports/ACTUAL_REWARD_COMMAND_SOURCE_FETCH_V1.json';assert not D.exists()and not report.exists();D.mkdir(parents=True)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
plan=json.loads((R/'payload_supermimic_eight_v1/SOURCE_PLAN.json').read_bytes());c=connect72();s=c.open_sftp();rows=[]
H=lambda raw:hashlib.sha256(raw).hexdigest()
try:
 for entry in plan['entries']:
  root=entry['job_root'];role=entry['role'];base=D/role;base.mkdir()
  with s.open(root+'/INSTALL_MANIFEST.json','rb')as f:raw=f.read()
  manifest=json.loads(raw);(base/'INSTALL_MANIFEST_SOURCE_REFERENCE.json').write_bytes(raw)
  candidates=[]
  for item in manifest['files']:
   rel=item['relative'];p=PurePosixPath(rel)
   if p.parent==PurePosixPath('runtime/isaac/mod4')and p.suffix=='.py':candidates.append(item)
   elif p.parent==PurePosixPath('.')and p.name in ('original_run_manifest.json','E1_CANONICAL_SOURCE_METADATA.json','VARIANT_SOURCE_METADATA.json'):candidates.append(item)
   elif rel.startswith(('lib/','original_field/'))and p.suffix=='.py'and any(key in p.name.lower()for key in ('reward','command','scut_rescue','skill')):candidates.append(item)
  copied=[]
  for item in candidates:
   rel=item['relative'];assert not PurePosixPath(rel).is_absolute()and'..'not in PurePosixPath(rel).parts
   with s.open(root+'/'+rel,'rb')as f:raw=f.read()
   assert len(raw)==item['bytes']and H(raw)==item['SHA'],(role,rel,'Sealedsource mismatch')
   dest=base/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);copied.append(dict(relative=rel,bytes=len(raw),SHA=H(raw)))
  rows.append(dict(role=role,source_root=root,manifest_SHA=H((base/'INSTALL_MANIFEST_SOURCE_REFERENCE.json').read_bytes()),files=copied))
 v=dict(kind='READONLY_CURRENT_SEALED_REWARD_COMMAND_SOURCE_AUDIT_NOT_RUNTIME_REWARD_MEASUREMENT',rows=rows,selected_PT_binary_raw_SDK_GPU_C_GO_lock_or_mutation_operations=0)
 report.write_text(json.dumps(v,indent=2),encoding='utf-8');print(report);print(json.dumps(dict(roles=[dict(role=x['role'],Python_config_files=len(x['files']),bytes=sum(f['bytes']for f in x['files']))for x in rows],source_only=True),indent=2))
finally:s.close();c.close()
