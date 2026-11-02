"""New active-set solver target objects only; previous stages stay immutable."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'portable_spin_h2_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b,1)
def main():
 old={r['path']:r['sha256'] for r in json.loads((HERE/'SOURCE_FREEZE.json').read_text())['old_files']}
 for n in ['arm_h2.ps1','target_probe.c','inspect_h2_objects.py']:assert sha(BASE/n)==old[str(BASE/n)]
 text=(BASE/'arm_h2.ps1').read_text(encoding='utf-8');start=text.index('$sources=@(');end=text.index('\n)',start)+2
 text=text[:start]+"$sources=@(\n  [pscustomobject]@{id='active_box_qp';path=(Resolve-Path -LiteralPath (Join-Path $root 'active_box_qp.c')).Path}\n)"+text[end:]
 text=once(text,"scope='SH2_NOMINAL_MATH_ONLY_NEW_STAGE_ARM_COMPILE_ONLY_NO_DISPATCH'","scope='AB3_ACTIVE_BOUND_QP_NEW_STAGE_COMPILE_ONLY_NOT_ROBOT_MPC_OR_RUNTIME'")
 assert not (HERE/'arm_active.ps1').exists();(HERE/'arm_active.ps1').write_text(text,encoding='utf-8');assert not (HERE/'target_probe.c').exists();(HERE/'target_probe.c').write_bytes((BASE/'target_probe.c').read_bytes())
 inspector=once((BASE/'inspect_h2_objects.py').read_text(encoding='utf-8'),'assert len(rows)==4','assert len(rows)==2');assert not (HERE/'inspect_active_objects.py').exists();(HERE/'inspect_active_objects.py').write_text(inspector,encoding='utf-8')
 info={'base_harness':str(BASE/'arm_h2.ps1'),'base_sha256':sha(BASE/'arm_h2.ps1'),'new_harness_sha256':sha(HERE/'arm_active.ps1'),'sources':['active_box_qp.c'],'objects_expected':2,'runtime_or_BSP':False};(HERE/'ARM_HARNESS_PROVENANCE.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8');print(json.dumps(info))
if __name__=='__main__':main()
