"""One bounded NEW combination build; never calls old build/test scripts or SDKs."""
from pathlib import Path
import hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
GCC=Path('C:/MinGW/bin/gcc.exe');GPP=GCC.with_name('g++.exe');NM=GCC.with_name('nm.exe')
ARM=Path('C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe');LINK=ARM.with_name('armlink.exe');FROM=ARM.with_name('fromelf.exe')
CFLAGS=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
CPPFLAGS=['-std=c++11','-O2','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 mode=sys.argv[1];assert mode in ('host','ARM');bom=json.loads((HERE/'SOURCE_BOM.json').read_bytes());runtime=[ROOT/n for n in bom['runtime']]
 assert len(set(runtime))==9 and len(set(p.stem for p in runtime))==9
 for r in bom['files']:assert sha(ROOT/r['path'])==r['sha256']
 receipt=dict(scope='NEW_COMBINATION_'+mode,status='RUNNING_NOT_A_SEAL',runtime=bom['runtime'],commands=[],new_inputs={})
 for n in ('build_co1.py','co1_abi.h','co1_abi_probe.c','co1_smoke_body.h','co1_smoke_c.c','co1_smoke_cpp.cpp','BUDGET.json','SOURCE_BOM.json'):
  receipt['new_inputs'][n]=sha(HERE/n)
 outname=HERE/('HOST_BUILD.json'if mode=='host'else'ARM_BUILD.json');assert not outname.exists()
 def save():outname.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
 def run(folder,key,args,artifact=None,optional=False):
  folder.mkdir(exist_ok=True);o=folder/(key+'.stdout.log');e=folder/(key+'.stderr.log');assert not o.exists()and not e.exists()
  with o.open('wb')as fo,e.open('wb')as fe:r=subprocess.run([str(a)for a in args],cwd=HERE,stdout=fo,stderr=fe)
  rec=dict(key=key,argv=[str(a)for a in args],exit_code=r.returncode,stdout=str(o.relative_to(HERE)),stderr=str(e.relative_to(HERE)))
  if artifact is not None:
   rec['artifact']=str(artifact.relative_to(HERE));rec['artifact_exists']=artifact.is_file()
   if artifact.is_file():rec.update(bytes=artifact.stat().st_size,sha256=sha(artifact))
  receipt['commands'].append(rec);save()
  if r.returncode==0 and artifact is not None and not artifact.is_file():raise RuntimeError('EXIT0_ARTIFACT_MISSING_STOP_NO_RETRY_'+key)
  if r.returncode and not optional:raise RuntimeError('COMMAND_FAILED_STOP_'+key)
  return r.returncode
 try:
  if mode=='host':
   folder=HERE/'host';folder.mkdir();run(folder,'gcc_version',[GCC,'--version']);run(folder,'gpp_version',[GPP,'--version'])
   objects=[]
   for src in runtime:
    obj=folder/(src.stem+'.o');run(folder,'compile_'+src.stem,[GCC,*CFLAGS,'-c',src,'-o',obj],obj);objects.append(obj)
   probe=folder/'co1_abi_probe.o';run(folder,'compile_new_abi',[GCC,*CFLAGS,'-c',HERE/'co1_abi_probe.c','-o',probe],probe)
   run(folder,'nm_runtime_globals',[NM,'-g',*objects])
   for language,compiler,flags,source in [('C',GCC,CFLAGS,'co1_smoke_c.c'),('CPP',GPP,CPPFLAGS,'co1_smoke_cpp.cpp')]:
    obj=folder/('smoke_'+language+'.o');exe=folder/('co1_'+language+'.exe')
    run(folder,'compile_smoke_'+language,[compiler,*flags,'-c',HERE/source,'-o',obj],obj)
    run(folder,'link_complete_'+language,[compiler,obj,*objects,probe,'-lm','-o',exe],exe)
    run(folder,'run_new_default_'+language,[exe])
    run(folder,'nm_executable_undefined_'+language,[NM,'-u',exe])
   # Exit0 disappearance even after initial link is not a success.
   for c in receipt['commands']:
    if 'artifact'in c:assert (HERE/c['artifact']).is_file()and sha(HERE/c['artifact'])==c['sha256']
  else:
   assert '--partial'in(HERE/'armlink_help.log').read_text(encoding='utf-8')
   receipt['targets']=[]
   for cpu,fpu in [('cortex-m4','fpv4-sp-d16'),('cortex-m7','fpv5-sp-d16')]:
    folder=HERE/cpu;folder.mkdir();flags=['--target=arm-arm-none-eabi','-mthumb','-mcpu='+cpu,'-mfpu='+fpu,'-mfloat-abi=hard','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
    objects=[]
    for src in runtime+[HERE/'co1_abi_probe.c']:
     obj=folder/(src.stem+'.o');run(folder,'compile_'+src.stem,[ARM,*flags,'-c',src,'-o',obj],obj);objects.append(obj)
    run(folder,'target_macros',[ARM,*flags,'-dM','-E',HERE/'co1_abi_probe.c'])
    combined=folder/'control_cores_partial.o'
    code=run(folder,'partial_once',[LINK,'--partial','--no_remove','--no_scanlib','--output',combined,*objects],combined,optional=True)
    target=dict(cpu=cpu,fpu=fpu,object_count=len(objects),objects=[str(p.relative_to(HERE))for p in objects],partial_exit_code=code,partial_object=str(combined.relative_to(HERE))if combined.is_file()else None)
    receipt['targets'].append(target);save()
    if combined.is_file()and code==0:run(folder,'fromelf_combined',[FROM,'--text','-v',combined])
  receipt['status']='NEW_BUILD_FINISHED_SAVED_EVIDENCE_AWAITING_SYMBOL_AUDIT';receipt['success']=True;save();print(json.dumps(dict(mode=mode,commands=len(receipt['commands']),status=receipt['status']),indent=2))
 except Exception as exc:
  receipt['status']='PARTIAL_BUILD_NOT_A_SEAL';receipt['success']=False;receipt['error']=str(exc);save();raise
if __name__=='__main__':main()
