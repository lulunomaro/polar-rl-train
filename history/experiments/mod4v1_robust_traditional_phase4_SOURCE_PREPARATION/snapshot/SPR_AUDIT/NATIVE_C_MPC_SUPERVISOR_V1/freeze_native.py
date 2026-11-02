"""Source-only native-supervisor freeze/export. No dynamics, SDK, or old runner."""
from pathlib import Path
import hashlib,json,importlib.util,sys,ast
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
PARENT=ROOT/'C_ACTIVE_MPC_SUPERVISOR_V1';AS=ROOT/'SPR_AUDIT/ACTIVE_BOX_QP_V3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def dump(n,x):
 p=HERE/n;assert not p.exists(),n;p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def carray(name,a,ctype='double'):
 a=np.asarray(a);vals=[]
 for v in a.ravel():
  x=float(v);s=x.hex();vals.append(s+('f'if ctype=='float'else''))
 return f'const {ctype} {name}[{a.size}]={{'+','.join(vals)+'};\n'
def main():
 old={};fsm=ROOT/'SPR_AUDIT/portable_fsm_detector_v1';fr=json.loads((fsm/'SOURCE_FREEZE.json').read_text())
 def add(p):old[str(p.resolve())]=row(p)
 for r in fr['old_files']:add(Path(r['path']));assert old[r['path']]['sha256']==r['sha256']
 for r in json.loads((fsm/'INDEX.json').read_text())['files']:add(Path(r['path']));assert old[r['path']]['sha256']==r['sha256']
 for n in ['INDEX.json','VALIDATION.json','MANIFEST.json','seal_run_01.log','seal_run_02.log']:add(fsm/n)
 source=[PARENT/n for n in ['supervisor_v2.py','preflight_v3.py','README.md']]+[ROOT/n for n in ['MPC8_V1/MODEL_AND_QP_CHECKS.json','nominal_gain_v1.json','SPR_AUDIT/C_MPC8_NUMERIC_V1/actual_model_vectors.json','SPR_AUDIT/ACTIVE_BOX_QP_V3/active_box_qp.c','SPR_AUDIT/ACTIVE_BOX_QP_V3/active_box_qp.h','SPR_AUDIT/ACTIVE_BOX_QP_V3/PROBLEMS.json','SPR_AUDIT/ACTIVE_BOX_QP_V3/C_RUNS_02.jsonl','SPR_AUDIT/portable_control_v3_current/REFERENCE_VECTORS.csv','SPR_AUDIT/portable_control_v3_current/REFERENCE_LAYOUT.json','SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/ROUNDTRIP_01.jsonl']]
 assert sha(AS/'active_box_qp.c')=='b726c0acf09a13fe0114da1e1161fb2a7f57a4e138c7caf239c5fdd157ec653e'
 spec=importlib.util.spec_from_file_location('frozen_native_parent',PARENT/'supervisor_v2.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 model=json.loads((ROOT/'MPC8_V1/MODEL_AND_QP_CHECKS.json').read_text());g=json.loads((ROOT/'nominal_gain_v1.json').read_text())['gain'];eq=np.r_[g['q'],np.zeros(7)];sup=m.ActiveMPCSupervisor(model,eq,None,clock_ns=lambda:0)
 real=np.asarray(json.loads((ROOT/'SPR_AUDIT/C_MPC8_NUMERIC_V1/actual_model_vectors.json').read_text())['H32'],dtype=np.float32);assert np.array_equal(real.view('u4'),sup.H.view('u4'))
 ms=sup.grad_map@sup.F;mr=sup.grad_map.reshape(15,15,9)[:,:,:8].sum(axis=1);mv=sup.grad_map[:,::9]@(np.arange(1,16)*.01)
 arrays={'nm1_H':sup.H,'nm1_S':sup.S,'nm1_eq':eq,'nm1_Mstate':ms,'nm1_Mref':mr,'nm1_Mv':mv}
 text='#include "nm1_model.h"\n'+''.join(carray(k,v,'float'if k=='nm1_H'else'double')for k,v in arrays.items());(HERE/'nm1_model.c').write_text(text,encoding='utf-8')
 (HERE/'nm1_model.h').write_text('#ifndef NM1_MODEL_H\n#define NM1_MODEL_H\nextern const float nm1_H[225];\nextern const double nm1_S[112],nm1_eq[14],nm1_Mstate[135],nm1_Mref[120],nm1_Mv[15];\n#endif\n',encoding='utf-8')
 dump('SOURCE_FREEZE.json',dict(scope='NEW_NATIVE_SUPERVISOR_ONLY',old_files=list(old.values()),sources=[row(p)for p in source],physics_imported=False,old_IO_executed=False,parent_imports=sorted({n.names[0].name if isinstance(n,ast.Import)else n.module for n in ast.walk(ast.parse((PARENT/'supervisor_v2.py').read_text()))if isinstance(n,(ast.Import,ast.ImportFrom))})))
 dump('MODEL_EXPORT.json',dict(N=15,model='fixedleg8+lag9',H32_exact_existing_H15=True,H32_sha256=hashlib.sha256(sup.H.tobytes()).hexdigest(),arithmetic='binary64 compressed f=Mstate*state9-Mref*ref8-Mv*shaper; final f32',bit_exact_promise=False,arrays={k:np.asarray(v).tolist()for k,v in arrays.items()},const_payload_bytes=sum(v.nbytes for v in arrays.values()),no_new_model_synthesis=True,no_dynamics=True))
 dump('NUMERICAL_BUDGET.json',dict(preregistered_before_C_execution=True,H_bits_mismatches=0,box_f32_bits_mismatches=0,discrete_decision_mismatches=0,f_absolute=1e-4,f_relative=2e-7,torque_absolute_Nm=5e-4,warm_absolute_Nm=5e-4,last_u_absolute_Nm=5e-4,caller_KKT_absolute=2e-6,unchanged_solver_tol=float(np.float32(.002)),unchanged_max_pivots=64,feasibility_violation=0,guard_delta_threshold_Nm=1e-6,clock_u64_ns_exact=True,clock_remaining_whole_us_floor=True,fallback_exact_original_f32_promoted_to_binary64=True,core_rounding='RN/no-fast-math/fp-contract=off; target FPSCR untested',source_of_inputs='saved C3 replies+same-packet drive from old fixtures; independent fixed-seed numeric vectors; no plant/holdout tuning'))
 assert 'mujoco'not in sys.modules and 'physics_bridge'not in sys.modules
 print(json.dumps(dict(status='FROZEN_AND_BUDGET_PREREGISTERED',old_files=len(old),sources=len(source),H_exact=True,const_bytes=sum(v.nbytes for v in arrays.values()),new_physics_steps=0)))
if __name__=='__main__':main()
