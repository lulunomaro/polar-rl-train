"""Continue unexecuted formal preparation with the verified cache ABI version."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent
def write(name,s):
 ast.parse(s);p=D/name;assert not p.exists();p.write_text(s,encoding='utf8');return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 s=(D/'s4_first_supported_gate_formal_worker_v1.py').read_text();assert s.count('from s4_original_fullstate_migration_v1 import')==1
 s=s.replace('from s4_original_fullstate_migration_v1 import','from s4_original_fullstate_migration_v2 import')
 rows=[write('s4_first_supported_gate_formal_worker_v2.py',s)]
 s=(D/'materialize_s4_first_supported_formal_target_CPU_v2.py').read_text()
 s=s.replace('zero_control_fullsave_and_own_fullrestore_sourcebound_complete','own_fullrestore0_from_valid601_complete')
 assert s.count("len(done['stages'])==2")==1
 s=s.replace("len(done['stages'])==2","len(done['stages'])==1").replace("done['stages'][1]","done['stages'][-1]")
 rows.append(write('materialize_s4_first_supported_formal_target_CPU_v3.py',s))
 p=D/'reports/S4_FORMAL_CACHE_HELPER_AND_ONE_ACTUAL_RESTORE_SOURCE_CPU_PREPARED.json';assert not p.exists()
 p.write_text(json.dumps(dict(epoch=time.time(),prepared=True,new_sources=rows,
  prior_inline_PowerShell_quote_SyntaxError_before_any_code_or_SSH_preserved=True,
  direct_one_restore_source_still_requires_actual_closed_GPU_and_independent_CPU=True,first_gate_GPU_PPO_not_yet_dispatched=True),indent=2))
 print(json.dumps(dict(prepared=True,report=str(p))))
if __name__=='__main__':main()
