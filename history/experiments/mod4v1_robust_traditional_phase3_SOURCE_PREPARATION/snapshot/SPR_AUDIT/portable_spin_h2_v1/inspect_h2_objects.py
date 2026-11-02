"""Offline small ELF object/metadata QA only; never executes ARM code."""
from pathlib import Path
import json,re,struct,hashlib,csv,traceback
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 receipt=json.loads((HERE/'BUILD_RECEIPT.json').read_text(encoding='utf-8-sig'));rows=[];macros={}
 for target in receipt['targets']:
  text=(HERE/target['id']/'target_macros_01.log').read_text(encoding='utf-8-sig');m=dict(re.findall(r'^#define\s+(\S+)\s+(.*)$',text,re.M))
  selected={k:m.get(k) for k in ['__ARMCC_VERSION','__ARM_ARCH','__ARM_ARCH_7EM__','__ARM_ARCH_PROFILE','__ARM_FP','__ARM_PCS_VFP','__thumb__','FLT_RADIX','FLT_MANT_DIG','FLT_EVAL_METHOD','__SIZEOF_FLOAT__']}
  assert selected['__ARM_ARCH_7EM__']=='1' and selected['__ARM_FP']=='0x6' and selected['__ARM_PCS_VFP']=='1'
  assert selected['FLT_MANT_DIG']=='24' and selected['FLT_EVAL_METHOD']=='0';macros[target['id']]=selected
 for obj in receipt['objects']:
  p=Path(obj['object']);raw=p.read_bytes();assert obj['compile_exit']==0 and obj['present'] and len(raw)==obj['bytes'] and sha(p)==obj['sha256']
  assert raw[:4]==b'\x7fELF' and raw[4]==1 and raw[5]==1
  elf_type,machine=struct.unpack_from('<HH',raw,16);flags=struct.unpack_from('<I',raw,36)[0]
  assert elf_type==1 and machine==40
  header=(HERE/obj['target']/(obj['source_id']+'_fromelf_01.log')).read_text(encoding='utf-8-sig')
  cpu=re.search(r'Tag_CPU_name = "([^"]+)"',header).group(1)
  assert cpu==obj['cpu'] and 'Tag_CPU_arch = ARM v7E-M' in header
  assert re.search(r'Tag_ABI_HardFP_use[^\n]*\(=1\)',header) and re.search(r'Tag_ABI_VFP_args[^\n]*\(=1\)',header)
  fp_arch=re.search(r'Tag_FP_arch = ([^\n]+)',header).group(1)
  rows.append({**obj,'ELF_class':'ELF32','ELF_endianness':'little','ELF_type':'ET_REL','ELF_machine':'EM_ARM','ELF_e_flags_hex':hex(flags),
   'CPU_attribute':cpu,'CPU_arch_attribute':'ARMv7E-M','ABI_HardFP_use':1,'ABI_VFP_args':1,'FP_arch_fromelf_original':fp_arch,
   'fromelf_log':str(HERE/obj['target']/(obj['source_id']+'_fromelf_01.log'))})
 assert len(rows)==4
 summary={'mode':'ARM_OBJECT_COMPILE_ONLY_NO_LINK_OR_RUNTIME','macros':macros,'objects':rows,
  'limits':['candidate CPUs not board bindings','hard-float object ABI not BSP/RTOS setup','ELF flags alone not hard-float proof; VFP args attributes and target macros checked','M7 FP_arch attribute8 is FP ISA encoding, not CPU v8-A','runtime numerics/FPSCR denormals/WCET untested']}
 dump('OBJECT_SUMMARY.json',summary)
 fields=['source_id','target','cpu','fpu','abi','compile_exit','bytes','sha256','ELF_type','ELF_machine','ABI_HardFP_use','ABI_VFP_args']
 with (HERE/'OBJECT_SUMMARY.csv').open('w',newline='',encoding='utf-8') as stream:
  w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows({k:x[k] for k in fields} for x in rows)
 print(json.dumps({'compiled_objects':len(rows),'failed':0,'objects':[{k:x[k] for k in ['source_id','target','bytes','sha256']} for x in rows],'macros':macros},indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'inspection_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
