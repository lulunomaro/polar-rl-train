"""Freeze exact current source BOM before any new compilation. No old tree scan."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 runtime=['PC3_CANDIDATE_BUNDLE_V1/cb1_candidate.c','portable_control_v3_current/pc3_estimator.c','portable_control_v3_current/pc3_controller.c','portable_core_v2_kinematics/ct_kinematics.c','portable_fsm_detector_v1/fd1_detector.c','NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c','NATIVE_C_MPC_SUPERVISOR_V1/nm1_model.c','ACTIVE_BOX_QP_V3/active_box_qp.c','PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.c']
 initial=[(ROOT/'SPR_AUDIT'/n).resolve()for n in runtime];assert len(set(initial))==9
 pending=list(initial);seen=set();edges=[]
 while pending:
  p=pending.pop()
  if p in seen:continue
  assert p.is_relative_to(ROOT/'SPR_AUDIT')and p.is_file();seen.add(p)
  for n in re.findall(r'^\s*#\s*include\s+"([^"]+)"',p.read_text(encoding='utf-8'),re.M):
   q=(p.parent/n).resolve();edges.append([p.relative_to(ROOT).as_posix(),q.relative_to(ROOT).as_posix()]);pending.append(q)
 assert len(seen)==22,len(seen)
 bom=dict(scope='EXACT_UNIQUE_CURRENT_RUNTIME_AND_QUOTED_HEADER_CLOSURE',runtime=[p.relative_to(ROOT).as_posix()for p in initial],files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p),role='runtime_C'if p in initial else'header_or_inc')for p in sorted(seen)],quoted_include_edges=edges,prebuild=dict(ARCHITECTURE=sha(HERE/'ARCHITECTURE.md'),BUDGET=sha(HERE/'BUDGET.json')),no_old_tree_scan=True)
 with(HERE/'SOURCE_BOM.json').open('x',encoding='utf-8')as f:json.dump(bom,f,indent=2)
 print(json.dumps(dict(runtime=9,source_closure=len(seen),BOM_sha256=sha(HERE/'SOURCE_BOM.json'),BUDGET_sha256=sha(HERE/'BUDGET.json'),no_compilation_or_old_tests=True),indent=2))
if __name__=='__main__':main()
