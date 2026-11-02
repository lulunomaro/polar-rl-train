"""Read-only object facts: actual compiled data bits, ABI, unresolved symbols."""
from pathlib import Path
import json,struct,hashlib,re
HERE=Path(__file__).resolve().parent
LAYOUT={'nm1_H':('f',225),'nm1_S':('d',112),'nm1_eq':('d',14),'nm1_Mstate':('d',135),'nm1_Mref':('d',120),'nm1_Mv':('d',15)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flatten(x):return sum((flatten(v)if isinstance(v,list)else[v]for v in x),[])if isinstance(x,list)else[x]
def coff(raw):
 machine,ns,_,pos,count,op,_=struct.unpack_from('<HHIIIHH',raw);assert machine==0x14c;sections=[struct.unpack_from('<8sIIIIIIHHI',raw,20+op+i*40)for i in range(ns)];strings=raw[pos+count*18:];symbols={};i=0
 while i<count:
  b=raw[pos+i*18:pos+(i+1)*18];name,value,section,_,_,aux=struct.unpack('<8sIhHBB',b)
  if name[:4]==b'\0'*4:
   off=struct.unpack_from('<I',name,4)[0];name=strings[off:strings.index(b'\0',off)]
  else:name=name.split(b'\0')[0]
  text=name.decode('ascii');i+=1+aux
  if section>0:
   s=sections[section-1];symbols[text.lstrip('_')]=raw[s[4]+value:s[4]+s[3]]
 return symbols,[]
def elf(raw):
 assert raw[:6]==b'\x7fELF\x01\x01';assert struct.unpack_from('<HH',raw,16)==(1,40);pos=struct.unpack_from('<I',raw,32)[0];size,num=struct.unpack_from('<HH',raw,46);ss=[struct.unpack_from('<IIIIIIIIII',raw,pos+i*size)for i in range(num)];symbols={};undef=[]
 for s in ss:
  if s[1]!=2:continue
  st=ss[s[6]];strings=raw[st[4]:st[4]+st[5]]
  for i in range(s[4],s[4]+s[5],s[9]):
   name,value,sz,_,_,section=struct.unpack_from('<IIIBBH',raw,i)
   if not name:continue
   text=strings[name:strings.index(b'\0',name)].decode('ascii')
   if section==0:undef.append(text)
   elif section<len(ss):d=ss[section];symbols[text]=raw[d[4]+value:d[4]+value+sz]
 return symbols,sorted(set(undef))
def main():
 model=json.loads((HERE/'MODEL_EXPORT.json').read_text())['arrays'];host=json.loads((HERE/'HOST_BUILD_01.json').read_text());reports=[]
 p=HERE/'revisions/host_attempt_01/nm1_model.o';s,_=coff(p.read_bytes())
 def check_data(symbols):
  proof={}
  for n,(fmt,count)in LAYOUT.items():
   expected=struct.pack('<'+fmt*count,*flatten(model[n]));actual=symbols[n][:len(expected)];assert actual==expected,n;proof[n]=dict(elements=count,bytes=len(expected),compiled_bits_equal_export=True,sha256=hashlib.sha256(actual).hexdigest())
  return proof
 hostproof=check_data(s)
 arm=json.loads((HERE/'ARM_BUILD_01.json').read_text());assert arm['success']and len(arm['objects'])==4
 for r in arm['objects']:
  p=Path(r['object']);assert sha(p)==r['sha256'];symbols,undefined=elf(p.read_bytes());folder=HERE/r['target'];txt=(folder/'target_macros_01.log').read_text();macros=dict(re.findall(r'^#define\s+(\S+)\s+(.*)$',txt,re.M));names=['__ARM_FP','__ARM_PCS_VFP','__ARM_ARCH_7EM__','FLT_EVAL_METHOD','DBL_MANT_DIG','DBL_MAX_EXP','__SIZEOF_DOUBLE__'];m={n:macros[n]for n in names};assert m=={'__ARM_FP':'0x6','__ARM_PCS_VFP':'1','__ARM_ARCH_7EM__':'1','FLT_EVAL_METHOD':'0','DBL_MANT_DIG':'53','DBL_MAX_EXP':'1024','__SIZEOF_DOUBLE__':'8'}
  log=folder/(Path(r['source']).stem+'_fromelf_01.log');attr=log.read_text();assert f'Tag_CPU_name = "{r["cpu"]}"'in attr and 'Tag_CPU_arch = ARM v7E-M'in attr and re.search(r'Tag_ABI_VFP_args[^\n]*\(=1\)',attr)
  reports.append({**r,'ELF':'ELF32 LE ET_REL EM_ARM','macros':m,'undefined_symbols':undefined,'compiled_model_bits':check_data(symbols)if Path(r['source']).stem=='nm1_model'else None,'FP_arch_original':re.search(r'Tag_FP_arch[^\n]+',attr)[0],'HardFP_use_original':re.search(r'Tag_ABI_HardFP_use[^\n]+',attr)[0]if 'Tag_ABI_HardFP_use'in attr else None})
 proof=dict(host_COFF_i386_compiled_model=hostproof,ARM_compiled_model_H_and_all_maps_bits_equal=True,model_payload_bytes=4068)
 (HERE/'COMPILED_DATA_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
 (HERE/'OBJECT_SUMMARY.json').write_text(json.dumps(dict(scope='NEW_OBJECTS_ONLY_NOT_ARM_RUNTIME',objects=reports,old_ASQP_ARM_objects_rebuilt=False,BSP_link=False,software_double_and_libm_linked=False,target_execution_FPSCR_stack_WCET=False),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(new_ARM_objects=len(reports),compiled_data_payload=4068,all_compiled_const_bits_match=True,undefined={r['target']+'/'+Path(r['source']).stem:r['undefined_symbols']for r in reports})))
if __name__=='__main__':main()
