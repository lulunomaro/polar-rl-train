"""Bounded exact member extraction to V2 only, then trusted fromelf metadata only.
AHRS: entire one-member coverage. DSP: two explicit representative members, NOT whole-library ABI proof.
No code/data disassembly or target execution.
"""
from pathlib import Path
import subprocess,json,hashlib,re
O=Path(__file__).resolve().parent;L=json.loads((O/'LIBRARY_MEMBERS.json').read_bytes())
plans=[(L[0],['ahrs.o'],'AHRS'),(L[1],['arm_abs_f32.o','arm_add_q31.o'],'DSP')]
rows=[];commands=[]
def run(a,cwd,label):
 c=subprocess.run(a,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20,check=False)
 r=dict(argv=a,cwd=str(cwd),exit=c.returncode)
 for k,b in [('stdout',c.stdout),('stderr',c.stderr)]:
  p=O/(label+'_'+k+'.log');p.write_bytes(b);r[k]=dict(path=p.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
 commands.append(r);return c
for lr,names,sub in plans:
 assert lr['exit']==0 and lr['members']is not None
 for n in names:assert n in lr['members']and re.fullmatch(r'[A-Za-z0-9_]+\.o',n)
 lib=Path(lr['library']['path']);st=lib.stat();out=O/'attributes'/sub;out.mkdir(parents=True,exist_ok=False)
 c=run(['C:/Keil_v5/ARM/ARMCC/bin/armar.exe','-x','-C',str(lib),*names],out,sub+'_extract')
 rr=dict(library=lr['library'],archive_members=len(lr['members']),inspected_members=names,complete_archive_attribute_coverage=len(names)==len(lr['members']),extract_exit=c.returncode,objects=[])
 if c.returncode==0:
  for i,n in enumerate(names):
   p=out/n;b=p.read_bytes();assert b[:7]==b'\x7fELF\x01\x01\x01'and len(b)<1048576,'BOUND_OR_ELF_SHAPE'
   cc=run(['C:/Keil_v5/ARM/ARMCC/bin/fromelf.exe','--text','-v',str(p)],O,sub+'_'+n.replace('.','_')+'_attributes')
   rr['objects'].append(dict(name=n,path=p.relative_to(O).as_posix(),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),fromelf_exit=cc.returncode))
 assert (lib.stat().st_size,lib.stat().st_mtime_ns)==(st.st_size,st.st_mtime_ns)
 rows.append(rr)
v=dict(scope='AR_MEMBER_NAMES_AND_3_ELF_METADATA_ONLY_NO_CODE_DATA_DUMP',libraries=rows,commands=commands,compiled_or_linked=False,algorithm_or_target_executed=False,stage1_written=False)
with(O/'LIBRARY_ATTRIBUTE_COMMANDS.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2);f.write('\n')
print(json.dumps(v,indent=2))
