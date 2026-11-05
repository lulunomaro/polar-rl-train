"""Read only a closed own-purpose SDK log to locate the module-structure gate failure, never checkpoints."""
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;p=D/'SCUT_PROBE3_CLOSED_MODEL_LOG.txt';assert not p.exists();v=json.loads(Path(json.loads((D/'E0_SCUT_PROBE_ADMISSION3_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=v['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert v['closed']is True and end['all_own_children_waited']is end['original_cost_settled']is end['original_private_finite_authority_leases_released']is outer['original_owner_reaped']is True
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 with s.open(v['root']+'/roles/E0/PPO_FULL_STDOUT_STDERR.log','rb')as f:
  n=f.stat().st_size;f.seek(max(0,n-250000));raw=f.read()
 p.write_bytes(raw);lines=raw.decode('utf8','replace').splitlines();selected=[]
 for i,line in enumerate(lines):
  if any(x in line for x in('MLP','Linear(','ELU(','actor','critic','normalization','norm','ValueError: Original 256')):
   if len(selected)<90:selected.extend(lines[max(0,i-1):min(len(lines),i+2)])
 print(json.dumps(dict(path=str(p),closed_source_error=v['cases']['E0']['V2_MIGRATION_FINAL.json']['error'],model_print_lines=selected[:140],own_closed_log_only=True,model_bytes_hash_decode_SDK_GPU_C_or_foreign_operations=0),indent=2))
finally:s.close();c.close()
