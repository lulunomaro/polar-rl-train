"""Derive NEW compile-only harness; never edit or rerun old stage outputs."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'ARM_OBJECT_BUILD_V1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b,1)
def main():
 frozen={x['path']:x['sha256'] for x in json.loads((HERE/'SOURCE_FREEZE.json').read_text())['old_sealed_snapshot']}
 for name in ['arm_build.ps1','target_probe.c','inspect_objects.py']:assert sha(BASE/name)==frozen[str(BASE/name)]
 for name in ['target_probe.c','inspect_objects.py']:
  out=HERE/name;assert not out.exists();out.write_bytes((BASE/name).read_bytes())
 text=(BASE/'arm_build.ps1').read_text(encoding='utf-8')
 text=once(text,"id='ct_core';path=(Resolve-Path -LiteralPath (Join-Path $root '..\\portable_core_v1\\ct_core.c')).Path","id='pc3_estimator';path=(Resolve-Path -LiteralPath (Join-Path $root 'pc3_estimator.c')).Path")
 text=once(text,"id='ct_kinematics';path=(Resolve-Path -LiteralPath (Join-Path $root '..\\portable_core_v2_kinematics\\ct_kinematics.c')).Path","id='pc3_controller';path=(Resolve-Path -LiteralPath (Join-Path $root 'pc3_controller.c')).Path")
 text=once(text,"id='boxqp_fast';path=(Resolve-Path -LiteralPath (Join-Path $root '..\\portable_mpc_qp_v2_fast\\boxqp_fast.c')).Path","id='pc3_dispatch';path=(Resolve-Path -LiteralPath (Join-Path $root 'pc3_dispatch.c')).Path")
 text=once(text,"scope='ARM_COMPILE_ONLY_NOT_BSP_LINK_OR_RUNTIME'","scope='PC3_CURRENT_NEW_STAGE_ARM_COMPILE_ONLY_NOT_BSP_LINK_OR_RUNTIME'")
 out=HERE/'arm_current.ps1';assert not out.exists();out.write_text(text,encoding='utf-8')
 provenance={'base_harness':str(BASE/'arm_build.ps1'),'base_sha256':sha(BASE/'arm_build.ps1'),'current_harness':str(out),'current_sha256':sha(out),'source_ids':['pc3_estimator','pc3_controller','pc3_dispatch'],'mode':'new V3-current stage only, old ARM stage objects/metadata not overwritten'}
 (HERE/'ARM_HARNESS_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8');print(json.dumps(provenance))
if __name__=='__main__':main()
