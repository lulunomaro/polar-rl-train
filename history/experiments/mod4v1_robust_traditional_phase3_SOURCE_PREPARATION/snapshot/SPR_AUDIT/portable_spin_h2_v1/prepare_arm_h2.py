"""NEW H2 math object harness, derived read-only, with exactly two new sources."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'portable_control_v3_current'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b,1)
def main():
 old={r['path']:r['sha256'] for r in json.loads((HERE/'SOURCE_FREEZE.json').read_text())['old_files']}
 for name in ['arm_current.ps1','target_probe.c','inspect_objects.py']:assert sha(BASE/name)==old[str(BASE/name)]
 text=(BASE/'arm_current.ps1').read_text(encoding='utf-8');start=text.index('$sources=@(');end=text.index('\n)',start)+2
 replacement="$sources=@(\n  [pscustomobject]@{id='sh2_controller';path=(Resolve-Path -LiteralPath (Join-Path $root 'sh2_controller.c')).Path},\n  [pscustomobject]@{id='sh2_pipeline';path=(Resolve-Path -LiteralPath (Join-Path $root 'sh2_pipeline.c')).Path}\n)"
 text=text[:start]+replacement+text[end:];text=once(text,"scope='PC3_CURRENT_NEW_STAGE_ARM_COMPILE_ONLY_NOT_BSP_LINK_OR_RUNTIME'","scope='SH2_NOMINAL_MATH_ONLY_NEW_STAGE_ARM_COMPILE_ONLY_NO_DISPATCH'")
 assert not (HERE/'arm_h2.ps1').exists();(HERE/'arm_h2.ps1').write_text(text,encoding='utf-8')
 assert not (HERE/'target_probe.c').exists();(HERE/'target_probe.c').write_bytes((BASE/'target_probe.c').read_bytes())
 inspector=once((BASE/'inspect_objects.py').read_text(encoding='utf-8'),'assert len(rows)==6','assert len(rows)==4');assert not (HERE/'inspect_h2_objects.py').exists();(HERE/'inspect_h2_objects.py').write_text(inspector,encoding='utf-8')
 report={'base':str(BASE/'arm_current.ps1'),'base_sha256':sha(BASE/'arm_current.ps1'),'new_harness_sha256':sha(HERE/'arm_h2.ps1'),'new_sources':['sh2_controller.c','sh2_pipeline.c'],'expected_objects':4,'no_old_stage_output_changed':True};(HERE/'ARM_HARNESS_PROVENANCE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
