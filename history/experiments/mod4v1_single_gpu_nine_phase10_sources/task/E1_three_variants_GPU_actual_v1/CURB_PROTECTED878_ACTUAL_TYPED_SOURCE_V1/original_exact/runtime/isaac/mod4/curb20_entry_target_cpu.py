"""CPU-only source and snapshot admission; no CUDA or optimizer updates."""
from pathlib import Path
import json,torch,ast,hashlib,os
def verify(D):
 torch.set_num_threads(1)
 from curb20_entry_fullsave_cpu import fullsave
 row=json.loads((D/'reports/SOURCE_SELECTED.json').read_bytes());p=Path(row['path']);v=fullsave(p)
 assert v['finite_tensors']==102 and v['sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
 ck=torch.load(p,map_location='cpu',weights_only=False)
 assert ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1'
 for name,h in json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes())['sha256'].items():
  q=D/name;assert hashlib.sha256(q.read_bytes()).hexdigest()==h
 for name in ('train_curb20_entry_fresh_preflight_ppo.py','train_curb20_entry_resume_ppo.py','probe_curb20_entry_fresh_process_full_resume.py'):
  text=(D/'isaac/mod4'/name).read_text();ast.parse(text)
  assert 'curb20_entry_v3_runtime' in text and 'curb20_entry_full_checkpoint' in text
 assert not torch.cuda.is_initialized()
 return dict(passed=True,source_checkpoint=v,CPU_only=True,old_full_D0_D7_optimizer_global_named_private_schema_retained=True,source_G3_to_new_CURB_entry_disclosed=True,SDK_new_origin_bound_pending=True,PPO_formal_pending=True)
