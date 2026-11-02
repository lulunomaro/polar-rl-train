"""Read saved new build evidence only; no compiler, linker, smoke or old QA run."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_bytes())
def text(p):return p.read_text(encoding='utf-8')
def elf(p):
 b=p.read_bytes();assert b[:6]==b'\x7fELF\x01\x01';h=struct.unpack_from('<HHIIIIIHHHHHH',b,16);assert h[0]==1 and h[1]==40
 so,ss,sn,si=h[5],h[10],h[11],h[12];assert ss==40
 sec=[struct.unpack_from('<10I',b,so+i*ss)for i in range(sn)]
 ns=sec[si];names=b[ns[4]:ns[4]+ns[5]]
 def string(t,o):return t[o:t.index(0,o)].decode('utf-8')
 symbols=[]
 for s in sec:
  if s[1]!=2:continue
  st=sec[s[6]];strings=b[st[4]:st[4]+st[5]];assert s[9]==16
  for at in range(s[4],s[4]+s[5],16):
   no,value,size,info,other,ndx=struct.unpack_from('<IIIBBH',b,at);name=string(strings,no)
   if name and info>>4 in (1,2):symbols.append(dict(name=name,binding=info>>4,type=info&15,section=ndx,value=value,bytes=size))
 def payload(name):
  sym=next(s for s in symbols if s['name']==name and s['section']);s=sec[sym['section']];at=s[4]+sym['value']-s[3];return b[at:at+sym['bytes']]
 return dict(format='ELF32_LE_ET_REL_EM_ARM',flags=h[6],strong=sorted(s['name']for s in symbols if s['binding']==1 and s['section']),undefined=sorted(set(s['name']for s in symbols if not s['section'])),writable_allocated=[string(names,s[0])for s in sec if s[2]&3==3 and s[5]]),payload
# Installed ARM math.h:740-741 declares _fabsf (old ARM name), fabsf calls it.
MATH={'_fabsf','acos','cos','sin','atan2','hypot','sqrt','fabs','fmax','fmin','nextafter','acosf','cosf','sinf','atan2f','hypotf','sqrtf','fabsf','fmaxf','fminf','nextafterf'}
CRT={'memcpy','memmove','memset','memcmp','__fpclassify','__fpclassifyf','__udivdi3'}
def classify(names):
 out=dict(system_math=[],system_RT_CRT=[],unexpected=[])
 for n in sorted(names):
  if n in MATH or n.startswith('__hardfp_')and n[len('__hardfp_'):]in MATH:out['system_math'].append(n)
  elif n in CRT or n.startswith(('__aeabi_','__rt_')):out['system_RT_CRT'].append(n)
  else:out['unexpected'].append(n)
 return out
def forbidden(names):return sorted(n for n in names if n in ('pc3_cycle','pc3_dispatch_reset')or re.search(r'(enqueue|socket|(^|_)send($|_))',n,re.I))
def main():
 host=load('HOST_BUILD.json');arm=load('ARM_BUILD.json');bom=load('SOURCE_BOM.json');assert host['success']and arm['success']
 runtime={str((ROOT/p).resolve())for p in bom['runtime']}
 for r in(host,arm):
  for c in r['commands']:
   assert c['exit_code']==0,c['key']
   if 'artifact'in c:assert sha(HERE/c['artifact'])==c['sha256']
 # Enforce exact once per runtime per platform, not copies from delivered ZIPs.
 counts=defaultdict(Counter)
 for rec in(host,arm):
  for c in rec['commands']:
   a=c['argv']
   if '-c'in a:
    src=str(Path(a[a.index('-c')+1]).resolve())
    if src in runtime:counts['host'if rec is host else ('cortex-m4'if '-mcpu=cortex-m4'in a else'cortex-m7')][src]+=1
 assert set(counts)=={'host','cortex-m4','cortex-m7'}
 for counter in counts.values():assert set(counter)==runtime and set(counter.values())=={1}
 # Actual GNU nm on all nine host runtime objects.
 defs=defaultdict(list);uses=set();current=''
 for line in text(HERE/'host/nm_runtime_globals.stdout.log').splitlines():
  if line.endswith('.o:'):current=line[:-1];continue
  m=re.match(r'^\s*(?:[0-9a-fA-F]+\s+)?([A-Za-z?])\s+(\S+)\s*$',line)
  if not m:continue
  kind,name=m.groups();name=name[1:]if name.startswith('_')else name
  if kind=='U':uses.add(name)
  elif kind.isupper()and kind not in('W','V'):defs[name].append(current)
 duplicates={n:p for n,p in defs.items()if len(p)>1};assert not duplicates
 host_remaining=uses-set(defs);hc=classify(host_remaining);assert not hc['unexpected'];assert not forbidden(set(defs)|uses)
 smokes={};executables=[]
 for language in('C','CPP'):
  output=text(HERE/('host/run_new_default_'+language+'.stdout.log'));m=re.search(r'checks=(\d+) failures=(\d+)',output);assert m and int(m[2])==0 and int(m[1])<=64
  smokes[language]=dict(checks=int(m[1]),failures=int(m[2]),raw=output.strip())
  p=HERE/('host/co1_'+language+'.exe');b=p.read_bytes();pe=struct.unpack_from('<I',b,0x3c)[0];assert b[:2]==b'MZ'and b[pe:pe+4]==b'PE\0\0'and struct.unpack_from('<H',b,pe+4)[0]==0x14c and struct.unpack_from('<H',b,pe+24)[0]==0x10b
  leftovers=[s.split()[-1]for s in text(HERE/('host/nm_executable_undefined_'+language+'.stdout.log')).splitlines()if s.strip()]
  assert set(leftovers)<= {'___deregister_frame_info','___register_frame_info','__Jv_RegisterClasses'}
  executables.append(dict(language=language,path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p),format='PE32_i386',actual_nm_U=leftovers,classification='optional GCC CRT/unwind/Java-registration metadata hooks; not missing kernel API, actual smoke executed'))
 # The same ten objects were used in each ARM partial, with no automatic libraries.
 keys=re.findall(r'\bX\((\w+),',text(HERE/'co1_abi.h'));assert len(keys)==29
 targets=[]
 for target in arm['targets']:
  inputs=[];owners=defaultdict(list);unresolved=set();all_names=set()
  for n in target['objects']:
   p=HERE/n;r,get=elf(p);inputs.append(dict(path=n,bytes=p.stat().st_size,sha256=sha(p),**r));unresolved.update(r['undefined']);all_names.update(r['strong']);all_names.update(r['undefined'])
   for sym in r['strong']:owners[sym].append(n)
  duplicates={n:o for n,o in owners.items()if len(o)>1};assert not duplicates
  remaining=unresolved-set(owners);categories=classify(remaining);assert not categories['unexpected'],categories
  assert not forbidden(all_names)
  assert target['partial_exit_code']==0 and target['partial_object'];p=HERE/target['partial_object'];combined,get=elf(p)
  assert set(owners)<=set(combined['strong'])
  assert set(combined['undefined'])==remaining,(combined['undefined'],remaining)
  assert not forbidden(set(combined['strong'])|set(combined['undefined']))
  layout=get('co1_target_layout');assert len(layout)==116;values=struct.unpack('<29I',layout)
  probe_get=elf(HERE/target['objects'][-1])[1];assert layout==probe_get('co1_target_layout')
  folder=HERE/target['cpu'];macros=dict(re.findall(r'^#define\s+(\w+)\s+(.+)$',text(folder/'target_macros.stdout.log'),re.M))
  assert macros['__ARM_PCS_VFP']=='1'and macros['__ARM_ARCH_7EM__']=='1'and macros['__ARM_FP']=='0x6'
  attrs=dict(re.findall(r'^\s*(Tag_\w+)\s*=\s*(.+)$',text(folder/'fromelf_combined.stdout.log'),re.M))
  assert 'v7E-M'in attrs['Tag_CPU_arch']and attrs['Tag_ABI_VFP_args'].endswith('(=1)')and '32-bit'in attrs['Tag_ABI_enum_size']
  targets.append(dict(cpu=target['cpu'],objects=inputs,strong_duplicate_definitions=duplicates,remaining_system_dependencies=categories,internal_peer_references_resolved=True,partial=dict(path=target['partial_object'],bytes=p.stat().st_size,sha256=sha(p),**combined),ABI_layout=dict(zip(keys,values)),macros={n:macros[n]for n in ('__ARM_PCS_VFP','__ARM_ARCH_7EM__','__ARM_FP','__FLT_EVAL_METHOD__','__FLT_MANT_DIG__','__DBL_MANT_DIG__','__SIZEOF_DOUBLE__')},attributes=attrs))
 result=dict(status='PASS_BUILD_COHABITATION_DEFAULT_ONLY_NOT_SEND_CHAIN',runtime_unique=9,source_closure=22,compiles_per_runtime_per_platform=1,host=dict(strong_definitions=len(defs),duplicate_strong_definitions={},remaining_before_system_link=hc,smokes=smokes,executables=executables,CPP_matches_C_29_layout_fields=True),ARM=targets,old_QA_or_physics_runs=0,partial_is_not_executable=True,full_control_transaction_qualified=False)
 with(HERE/'COMBINATION_AUDIT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(status=result['status'],new_smoke_checks={k:v['checks']for k,v in smokes.items()},host_runtime_strong_symbols=len(defs),ARM_partials=[dict(cpu=t['cpu'],bytes=t['partial']['bytes'],system_unresolved=len(t['partial']['undefined']))for t in targets],unexpected_dependencies=0,old_QA_runs=0),indent=2))
if __name__=='__main__':main()
