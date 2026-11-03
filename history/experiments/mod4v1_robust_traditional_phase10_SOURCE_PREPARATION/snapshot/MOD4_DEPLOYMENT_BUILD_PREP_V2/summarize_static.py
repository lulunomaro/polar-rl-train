"""Saved fromelf metadata + exact declared DFP node/path inspection. No external tools."""
from pathlib import Path
import json,re,hashlib,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;R=O.parent;S=R/'MOD4_DEPLOYMENT_PORT_V1';P=S/'derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx'
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
A=json.loads((O/'LIBRARY_ATTRIBUTE_COMMANDS.json').read_bytes());facts=[]
for label in ('AHRS_ahrs_o','DSP_arm_abs_f32_o','DSP_arm_add_q31_o'):
 p=O/(label+'_attributes_stdout.log');txt=p.read_text(encoding='utf-8');groups=[];group=None;tags={}
 for n,line in enumerate(txt.splitlines(),1):
  if 'build attributes' in line:
   group=dict(header=line.strip(),line=n,tags=[]);groups.append(group)
  m=re.match(r'\s*(Tag_\w+)\s*=\s*(.*)',line)
  if m:
   k,v=m.groups();tags.setdefault(k,[])
   if v not in tags[k]:tags[k].append(v)
   assert group is not None;group['tags'].append(dict(name=k,value=v,line=n))
 facts.append(dict(object=label,metadata=ref(p),ELF32='ELFCLASS32'in txt,little_endian='ELFDATA2LSB'in txt,relocatable='ET_REL'in txt,machine_ARM='EM_ARM'in txt,EABI5='ARM ELF revision: 5'in txt,producer_lines=[dict(line=n,text=s.strip())for n,s in enumerate(txt.splitlines(),1)if 'Component: ARM Compiler'in s],build_attribute_groups=groups,distinct_observed_tags=tags))
K=Path('C:/Keil_v5/ARM/PACK/Keil/STM32F4xx_DFP/2.17.1');pdsc=K/'Keil.STM32F4xx_DFP.pdsc';E=ET.fromstring(pdsc.read_bytes());parents={c:p for p in E.iter()for c in p};node=next(e for e in E.iter('variant')if e.attrib.get('Dvariant')=='STM32F407IGHx');chain=[]
while node is not None:
 chain.append(dict(tag=node.tag,attributes=node.attrib,device_attributes=[dict(tag=c.tag,attributes=c.attrib)for c in node if c.tag in('processor','compile','debug','memory')]))
 node=parents.get(node)
 # Stop at the devices tree, not the full package descriptions.
 if node is not None and node.tag=='devices':break
px=ET.fromstring(P.read_bytes());literal=px.findtext('./Targets/Target/TargetOption/TargetCommonOption/SFDFile');relative=literal.split('$')[-1].replace('\\','/');svd=K/relative
refs=[ref(p)for p in(P,S/'BUILD_CLOSURE_FINAL.json',S/'NEXT_TARGET_BUILD_PLAN.md',S/'RECEIPT.json',pdsc,S/'derived/StandardRobotpp-balance1/Drivers/CMSIS/Include/cmsis_version.h',S/'derived/StandardRobotpp-balance1/MDK-ARM/RTE/_standard_robot/RTE_Components.h')]
counts={}
for f in px.findall('./Targets/Target/Groups/Group/Files/File'):
 k=f.findtext('FileType');counts[k]=counts.get(k,0)+1
v=dict(scope='METADATA_ONLY_NOT_COMPATIBILITY_OR_BUILD_APPROVAL',library_objects=facts,DSP_attribute_coverage='2_OF_272_NOT_FULL',AHRS_attribute_coverage='1_OF_1',DFP=dict(source=ref(pdsc),vendor=E.findtext('vendor'),name=E.findtext('name'),latest_release=E.find('./releases/release').attrib,device_chain=chain,project_svd_literal=literal,project_svd_resolved=str(svd),project_svd_file_exists=svd.is_file()),source_refs=refs,project_FileType_counts=counts,whole_423_source_rehash=False,compile_link_or_execution=False)
with(O/'STATIC_FACTS.json').open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(objects=[dict(name=x['object'],ELF32=x['ELF32'],EABI5=x['EABI5'],CPU=x['distinct_observed_tags'].get('Tag_CPU_arch'),VFP_args=x['distinct_observed_tags'].get('Tag_ABI_VFP_args'),enum=x['distinct_observed_tags'].get('Tag_ABI_enum_size'),wchar=x['distinct_observed_tags'].get('Tag_ABI_PCS_wchar_t'),denormal=x['distinct_observed_tags'].get('Tag_ABI_FP_denormal'))for x in facts],DFP=v['DFP'],FileType_counts=counts),indent=2))
