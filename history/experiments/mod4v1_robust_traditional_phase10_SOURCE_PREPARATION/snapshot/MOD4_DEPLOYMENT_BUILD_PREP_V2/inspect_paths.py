"""Narrow exact include/Pack/RTE/header existence only. Never walks user directories."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;R=O.parent;S=R/'MOD4_DEPLOYMENT_PORT_V1';P=S/'derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx'
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def exists(p):return dict(path=str(p),is_file=p.is_file(),is_directory=p.is_dir())
F=json.loads((S/'BUILD_CLOSURE_FINAL.json').read_bytes());E=ET.fromstring(P.read_bytes());T=E.find('./Targets/Target');assert T is not None
source_refs=[ref(p)for p in (P,S/'BUILD_CLOSURE_FINAL.json',S/'NEXT_TARGET_BUILD_PLAN.md',S/'RECEIPT.json')]
assert source_refs[1]['SHA']=='7a2d081ad9754791b6912b10d0f1949a64a3d76aebda13feb62a1934099570ca'
rows=[];unique={}
for el in T.findall('.//VariousControls/IncludePath'):
 for text in (el.text or '').split(';'):
  if not text.strip():continue
  text=text.strip();assert '$'not in text and ':'not in text
  p=(P.parent/text.replace('\\','/')).resolve();assert p.is_relative_to(S.resolve())
  x=dict(literal=text,**exists(p));rows.append(x);unique[str(p).casefold()]=x
packs=[]
for p in (Path('C:/Keil_v5/ARM/PACK/Keil/STM32F4xx_DFP/2.17.1/Keil.STM32F4xx_DFP.pdsc'),Path('C:/Keil_v5/ARM/PACK/ARM/CMSIS/5.8.0/ARM.CMSIS.pdsc')):packs.append(exists(p))
# Exact project-derived candidates only, not a search for alternate versions.
rtes=[exists(p)for p in(P.parent/'RTE/_standard_robot/RTE_Components.h',P.parent/('RTE/_'+T.findtext('TargetName')+'/RTE_Components.h'))]
std=[]
for n in ('stdint.h','stddef.h','stdbool.h','stdio.h','stdlib.h','string.h','math.h','float.h','limits.h','assert.h','stdarg.h','inttypes.h','time.h'):
 std.append(exists(Path('C:/Keil_v5/ARM/ARMCC/include')/n))
headers=[]
for n in ('core_cm4.h','cmsis_armcc.h','cmsis_gcc.h','cmsis_compiler.h','cmsis_version.h'):
 headers.append(exists(S/'derived/StandardRobotpp-balance1/Drivers/CMSIS/Include'/n))
headers.append(exists(S/'derived/StandardRobotpp-balance1/Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f407xx.h'))
libs=[]
for f in T.findall('./Groups/Group/Files/File'):
 if f.findtext('FileName')in('AHRS.lib','arm_cortexM4lf_math.lib'):
  p=(P.parent/f.findtext('FilePath').replace('\\','/')).resolve();st=p.stat();libs.append(dict(name=f.findtext('FileName'),path=str(p),bytes=st.st_size,mtime_ns=st.st_mtime_ns,hash='NOT_RECOMPUTED_V2; STAGE1_PARENT_VERIFIED'))
assert len(libs)==2
unresolved=F['unresolved_lexical_includes']
v=dict(scope='ACTUAL_PROJECT_XML_AND_NARROW_DECLARED_PATHS_NO_PREPROCESS',source_refs=source_refs,target=T.findtext('TargetName'),pArmCC=T.findtext('pArmCC'),pCCUsed=T.findtext('pCCUsed'),Cpu=T.findtext('./TargetOption/TargetCommonOption/Cpu'),PackID=T.findtext('./TargetOption/TargetCommonOption/PackID'),RTE_components=[dict(component=c.attrib,packages=[p.attrib for p in c.findall('package')])for c in E.findall('./RTE/components/component')],Cads={c.tag:c.text for c in T.findall('./TargetOption/TargetArmAds/Cads/*')if len(c)==0},C_various={c.tag:c.text for c in T.findall('./TargetOption/TargetArmAds/Cads/VariousControls/*')},ArmAdsMisc={c.tag:c.text for c in T.findall('./TargetOption/TargetArmAds/ArmAdsMisc/*')if len(c)==0},literal_include_checks=rows,unique_include_directories=list(unique.values()),pack_pdsc_exact_candidates=packs,pack_root_scope='ONLY_C:/Keil_v5/ARM/PACK; alternate/user caches UNKNOWN_NOT_SEARCHED',RTE_header_exact_candidates=rtes,tool_standard_headers=std,local_header_candidates=headers,libraries=libs,previous_unresolved_lexical_kind=type(unresolved).__name__,previous_unresolved_lexical_keys=list(unresolved)if isinstance(unresolved,dict)else None,actual_preprocessing=0,old_423_rehashed=False,stage1_files_written=False)
with(O/'PATHS_AND_PROJECT.json').open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(target=v['target'],includes=len(rows),unique=len(unique),missing_includes=[x for x in unique.values()if not x['is_directory']],packs=packs,RTE=rtes,missing_std=[x for x in std if not x['is_file']],Cads=v['Cads'],ArmAdsMisc=v['ArmAdsMisc'],libraries=libs),indent=2))
