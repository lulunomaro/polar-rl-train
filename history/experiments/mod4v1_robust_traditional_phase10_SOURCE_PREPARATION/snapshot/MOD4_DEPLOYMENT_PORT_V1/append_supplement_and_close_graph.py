"""Approved raw supplement COPY and lexical Windows closure; no binary analysis."""
from pathlib import Path,PurePosixPath
import hashlib,json,zlib,posixpath,re,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;ROOT=O.parent;B=ROOT/'DEPLOYED_BASELINE_AUDIT_V1';D=O/'derived';P='StandardRobotpp-balance1/'
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),SHA=sha(b))
def save(n,x):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
mp=B/'build_supplement001/MANIFEST.json'
assert rec(mp)['SHA']=='524b8dd11524fece9ac7faf5f9bd842e4d06e9f020d76f64ea47378e26bdcc7c'
M=json.loads(mp.read_bytes());assert len(M['files'])==32 and M['total_original_bytes']==13506260
C={r['name']:r for r in json.loads((B/'CENTRAL_DIRECTORY.json').read_bytes())['members']};old=json.loads((O/'SOURCE.json').read_bytes());S={r['member']:r for r in old['selected']};copied=[];texts={}
for m,r in S.items():
 if m.lower().endswith(('.c','.h','.s','.inc')):texts[m]=(B/'source'/Path(*PurePosixPath(m).parts)).read_text(encoding='utf-8')
for r in M['files']:
 m=r['member'];q=PurePosixPath(m);assert m.startswith(P)and '..'not in q.parts and '.git'not in q.parts and ':'not in m and m not in S
 src=B/'build_supplement001/source_original'/Path(*q.parts);assert Path(r['original_path']).resolve()==src.resolve()and not src.is_symlink()
 b=src.read_bytes();assert len(b)==r['bytes']and sha(b)==r['raw_SHA']and ('%08x'%(zlib.crc32(b)&0xffffffff))==r['CRC32']and C[m]['CRC32']==r['CRC32']and C[m]['bytes']==len(b)
 dest=D/Path(*q.parts);dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb')as f:f.write(b)
 assert sha(dest.read_bytes())==r['raw_SHA'];S[m]=dict(r,source_origin='parent_build_supplement001')
 copied.append(dict(member=m,bytes=len(b),raw_SHA=sha(b),CRC32=r['CRC32'],opaque_library=m.lower().endswith('.lib'),encoding=r.get('encoding'),copied_original_bytes=True))
 if 'readable_path'in r:
  rp=B/'build_supplement001/source'/Path(*q.parts);assert Path(r['readable_path']).resolve()==rp.resolve();rb=rp.read_bytes();assert sha(rb)==r['readable_SHA']and len(rb)==r['readable_bytes']
  if m.lower().endswith(('.c','.h','.s','.inc')):texts[m]=rb.decode('utf-8')
for name in ('mod4_port_gate.c','mod4_port_gate.h','mod4_port_bridge.c','mod4_port_bridge.h'):
 m=P+'application/mod4_port/'+name;src=O/'new_code'/name;assert sha((D/m).read_bytes())==sha(src.read_bytes());S[m]=dict(member=m,raw_SHA=sha(src.read_bytes()),source_origin='new_tested_adapter');texts[m]=src.read_text(encoding='utf-8')
# The two changed inherited text files are taken from actual derived bytes.
pr=json.loads((O/'PATCH_RECEIPT.json').read_bytes())
for r in pr['changed']:
 b=(D/r['member']).read_bytes();assert sha(b)==r['after_SHA'];texts[r['member']]=b.decode('utf-8-sig'if r['UTF8_BOM']else r['encoding'])
proj=P+'MDK-ARM/standard_robot.uvprojx';e=ET.fromstring((D/proj).read_bytes());T=e.findall('./Targets/Target');assert len(T)==1;T=T[0]
def norm(p,base=P+'MDK-ARM'):
 x=posixpath.normpath(posixpath.join(base,p.replace('\\','/').strip()));return x if x.startswith(P)and '.git'not in PurePosixPath(x).parts and ':'not in x else None
keys={}
for n in C:
 if '.git'not in PurePosixPath(n).parts:keys.setdefault(n.casefold(),[]).append(n)
for n in S:
 if n not in C:keys.setdefault(n.casefold(),[]).append(n)
def lookup(n):
 if n is None:return None
 hits=keys.get(n.casefold(),[]);assert len(hits)<=1,('Windows case collision',n,hits);return hits[0]if hits else None
def info(m):
 return dict(member=m,central=m in C,provided=m in S,source_origin=('initial391'if m in{r['member']for r in old['selected']}else S.get(m,{}).get('source_origin')),CRC32=C.get(m,{}).get('CRC32'),raw_SHA=S.get(m,{}).get('raw_SHA'))
files=[]
for g in T.findall('./Groups/Group'):
 for f in g.findall('./Files/File'):
  p=f.findtext('FilePath');m=lookup(norm(p));inc=(g.findtext('./GroupOption/CommonProperty/IncludeInBuild')!='0'and f.findtext('./FileOption/CommonProperty/IncludeInBuild')!='0')
  files.append(dict(group=g.findtext('GroupName'),name=f.findtext('FileName'),project_path=p,included=inc,**info(m)))
assert len(files)==169 and all(x['provided']for x in files if x['included'])
I=[]
for x in T.findall('.//IncludePath'):
 if x.text:
  for p in x.text.split(';'):
   if p.strip():I.append(dict(path=p,member_directory=norm(p)))
incdirs=list(dict.fromkeys(x['member_directory']for x in I if x['member_directory']))
# Walk from actual active File roots; retain unknown conditionals, do not execute PP.
todo=[x['member']for x in files if x['included']and x['member']in texts];seen=set();edges=[];unknown={};case_alias=[]
while todo:
 m=todo.pop(0)
 if m in seen:continue
 seen.add(m);txt=texts[m]
 for z in re.finditer(r'^\s*#\s*include\s*([<\"])([^>\"\r\n]+)[>\"]',txt,re.M):
  name=z[2];bases=([posixpath.dirname(m)]if z[1]=='"'else[])+incdirs;found=None;spelling=None
  for base in bases:
   n=norm(name,base);hit=lookup(n)
   if hit is not None:found=hit;spelling=n;break
  line=txt[:z.start()].count('\n')+1;row=dict(from_member=m,line=line,include=name,style=z[1],resolved=info(found),conditional_preprocessor_evaluated=False);edges.append(row)
  if found is None:unknown.setdefault(name,[]).append(dict(from_member=m,line=line))
  elif spelling!=found:case_alias.append(dict(from_member=m,line=line,include=name,actual_member=found))
  if found in texts and found not in seen:todo.append(found)
missing=[x for x in files if x['included']and not x['provided']]
oldclosure=json.loads((O/'BUILD_CLOSURE.json').read_bytes())
final=dict(kind='SUPPLEMENTED_169_MEMBER_WINDOWS_LEXICAL_CLOSURE_NOT_PREPROCESS_OR_TARGET_LINK',initial_closure=rec(O/'BUILD_CLOSURE.json'),supplement_manifest=rec(mp),source_lock=rec(O/'SOURCE.json'),target=T.findtext('TargetName'),compiler_record=T.findtext('pCCUsed'),device=T.findtext('./TargetOption/TargetCommonOption/Device'),pack=T.findtext('./TargetOption/TargetCommonOption/PackID'),C_flags=oldclosure['C_flags'],C_defines=oldclosure['C_defines'],linker=oldclosure['linker'],original_hooks=oldclosure['hooks'],derived_flash={x.tag:x.text for x in T.findall('./TargetOption/Utilities/Flash1/*')},include_paths=I,members=files,active_members_missing_provided=missing,all_original_165_members_provided=True,new_source_and_header_members=4,reachable_lexical_text_nodes=len(seen),lexical_edges=edges,Windows_case_aliases=case_alias,unresolved_lexical_includes=unknown,conditional_preprocessor_evaluated=False,compiler_builtin_headers_or_devicepack_checked=False,AHRS_DSP_library_ABI='UNEXAMINED_OPAQUE_ONLY_COPIED',host_gate_smoke='PASS40_NEW_ONLY_NOT_RERUN',full_target_builds=0,full_target_link=False,physical_binding=False,note='Unknown includes contain compiler standard headers and inactive family/compiler/RTOS test branches; they are not silently called satisfied or all declared active missing files.')
save('BUILD_CLOSURE_FINAL.json',final)
save('SUPPLEMENT_RECEIPT.json',dict(status='APPROVED_32_RAW_PAYLOAD_COPY_AND_WINDOWS_LEXICAL_GRAPH_ONLY',parent_manifest=rec(mp),appendix=rec(O/'SUPPLEMENT_APPENDIX.md'),copies=copied,count=len(copied),bytes=sum(x['bytes']for x in copied),all_original_165_and_new4_project_members_provided=not missing,Windows_case_alias_count=len(case_alias),initial_missing17_preserved=True,initial_SOURCE_unchanged=rec(O/'SOURCE.json')==oldclosure['source_lock'],libraries_executed_or_algorithm_or_ABI_inspected=False,old_source_paths_written=False,ZIP_opened=False,host_smoke_repeated=False,full_target_builds=0))
print(json.dumps(dict(status='SUPPLEMENT_COPY_AND_FINAL_GRAPH_PASS',copied=len(copied),copied_bytes=sum(x['bytes']for x in copied),project_members=len(files),active_missing=len(missing),Windows_case_aliases=len(case_alias),reachable_text_nodes=len(seen),unresolved_names=list(unknown),final_closure=rec(O/'BUILD_CLOSURE_FINAL.json')),indent=2))
