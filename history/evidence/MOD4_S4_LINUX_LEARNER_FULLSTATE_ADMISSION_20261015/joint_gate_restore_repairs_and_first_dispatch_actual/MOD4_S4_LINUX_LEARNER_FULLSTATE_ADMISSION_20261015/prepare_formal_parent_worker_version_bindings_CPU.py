"""Unexecuted formal filenames follow the fieldwise-cache worker version."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent
def write(name,s):
 ast.parse(s);p=D/name;assert not p.exists();p.write_text(s,encoding='utf8');return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 s=(D/'s4_first_supported_gate_formal_parent_v1.py').read_text();assert s.count('s4_first_supported_gate_formal_worker_v1.py')==1
 s=s.replace('s4_first_supported_gate_formal_worker_v1.py','s4_first_supported_gate_formal_worker_v2.py')
 rows=[write('s4_first_supported_gate_formal_parent_v2.py',s)]
 s=(D/'materialize_s4_first_supported_formal_target_CPU_v3.py').read_text();s=s.replace('from s4_first_supported_gate_formal_parent_v1 import','from s4_first_supported_gate_formal_parent_v2 import')
 rows.append(write('materialize_s4_first_supported_formal_target_CPU_v4.py',s))
 s=(D/'publish_s4_first_supported_formal_target_CPU_once_v1.py').read_text().replace('s4_first_supported_gate_formal_parent_v1.py','s4_first_supported_gate_formal_parent_v2.py').replace('materialize_s4_first_supported_formal_target_CPU_v3.py','materialize_s4_first_supported_formal_target_CPU_v4.py')
 rows.append(write('publish_s4_first_supported_formal_target_CPU_once_v2.py',s))
 p=D/'reports/S4_FORMAL_PARENT_WORKER_CACHE_VERSION_BINDINGS_PREPARED_CPU.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),prepared=True,new_sources=rows,original_unexecuted_sources_retained=True,no_formal_GPU_or_budget_dispatch_yet=True),indent=2));print(json.dumps(dict(prepared=True,report=str(p))))
if __name__=='__main__':main()
