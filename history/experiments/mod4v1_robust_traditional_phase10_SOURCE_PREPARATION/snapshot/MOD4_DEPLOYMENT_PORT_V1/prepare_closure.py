"""Own bounded metadata/copy tool; never imports project code or opens ZIP/.git."""
from pathlib import Path,PurePosixPath
import hashlib,json,posixpath,re,zlib,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;ROOT=O.parent;BASE=ROOT/'DEPLOYED_BASELINE_AUDIT_V1';PREFIX='StandardRobotpp-balance1/'
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),SHA=sha(b))
def out(n,v):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
cm=BASE/'CENTRAL_DIRECTORY.json';sm=BASE/'SELECTED_SOURCE_MANIFEST.json'
assert rec(sm)['SHA']=='33a79a69e5ebd1be437b05c75de378359d969f63d0761aa9303e79ce2a47a98d'
central=json.loads(cm.read_bytes());sel=json.loads(sm.read_bytes());assert central['entry_count']==1184 and sel['selected_text_count']==391
C={r['name']:r for r in central['members']};S={r['member']:r for r in sel['files']};assert len(C)==1184 and len(S)==391
raws={};texts={};rs=[]
for m,r in S.items():
 q=PurePosixPath(m);assert m.startswith(PREFIX)and not q.is_absolute()and '..'not in q.parts and '.git'not in q.parts and ':'not in m
 p=BASE/'source_original'/Path(*q.parts);expected=Path(r['original_path']);assert expected.resolve()==p.resolve()and p.resolve().is_relative_to((BASE/'source_original').resolve())and not p.is_symlink()
 b=p.read_bytes();assert len(b)==r['raw_bytes']<=1048576 and sha(b)==r['raw_SHA']and ('%08x'%(zlib.crc32(b)&0xffffffff))==r['CRC32']
 assert C[m]['bytes']==len(b)and C[m]['CRC32']==r['CRC32']and not C[m]['symlink']
 rb=(BASE/'source'/Path(*q.parts)).read_bytes();assert len(rb)==r['readable_bytes']and sha(rb)==r['readable_SHA']
 texts[m]=rb.decode('utf-8');raws[m]=b;rs.append(dict(member=m,bytes=len(b),raw_SHA=sha(b),CRC32=r['CRC32'],encoding=r['encoding'],readable_SHA=sha(rb)))
assert sum(map(len,raws.values()))==7724844 and sum(map(len,raws.values()))<8*1024*1024
# Lock before any derived project/adaptor code is created.
out('SOURCE.json',dict(kind='PRE_CODE_BOUNDED_ORIGINAL_BYTES_AND_SELECTED_LINEAGE_LOCK',method=rec(O/'METHOD.md'),central=rec(cm),selection=rec(sm),selected_original_count=391,selected_original_bytes=sum(map(len,raws.values())),selected=rs,archive_opened=False,archive_whole_hash=False,unselected_payloads_read=False,project_code_executed=False,physical_MOD4_binding=False))
project=PREFIX+'MDK-ARM/standard_robot.uvprojx';E=ET.fromstring(raws[project]);T=E.findall('./Targets/Target');assert len(T)==1;T=T[0]
PD=PREFIX+'MDK-ARM'
def norm(p,base=PD):
 p=p.replace('\\','/').strip();q=posixpath.normpath(posixpath.join(base,p));return q if q.startswith(PREFIX)and '.git'not in PurePosixPath(q).parts and ':'not in q else None
def existence(m):
 if m is None:return dict(member=None,central=False,selected=False,reason='external/macro/escape path unresolved')
 c=C.get(m);s=S.get(m);return dict(member=m,central=c is not None,selected=s is not None,central_bytes=None if c is None else c['bytes'],CRC32=None if c is None else c['CRC32'],raw_SHA=None if s is None else s['raw_SHA'])
F=[]
for g in T.findall('./Groups/Group'):
 gi=g.findtext('./GroupOption/CommonProperty/IncludeInBuild')
 for f in g.findall('./Files/File'):
  fi=f.findtext('./FileOption/CommonProperty/IncludeInBuild');p=f.findtext('FilePath');e=existence(norm(p))
  F.append(dict(group=g.findtext('GroupName'),name=f.findtext('FileName'),file_type=f.findtext('FileType'),project_path=p,included=(gi!='0'and fi!='0'),group_include_override=gi,file_include_override=fi,**e))
assert len(F)==165
incs=[]
for el in T.findall('.//IncludePath'):
 if el.text:
  for p in el.text.split(';'):
   if not p.strip():continue
   m=norm(p);prefix=''if m is None else m.rstrip('/')+'/'
   incs.append(dict(project_path=p,member_directory=m,central_descendants=0 if m is None else sum(n.startswith(prefix)for n in C),selected_descendants=0 if m is None else sum(n.startswith(prefix)for n in S)))
uniqueincs=list(dict.fromkeys(x['member_directory']for x in incs if x['member_directory']))
# Lexical dependencies: conditionals are intentionally NOT executed/preprocessed.
Q=[];unresolved={}
for m,txt in texts.items():
 if not m.lower().endswith(('.c','.h','.s','.inc')):continue
 for mt in re.finditer(r'^\s*#\s*include\s*([<\"])([^>\"\r\n]+)[>\"]',txt,re.M):
  style=mt[1];name=mt[2];bases=([posixpath.dirname(m)]if style=='"'else[])+uniqueincs
  candidates=[norm(name,b)for b in bases];hits=[p for p in candidates if p in C];chosen=hits[0]if hits else None
  row=dict(from_member=m,line=txt[:mt.start()].count('\n')+1,include=name,style=style,resolved=existence(chosen),other_central_candidates=list(dict.fromkeys(hits[1:])),conditional_preprocessor_evaluated=False)
  Q.append(row)
  if chosen is None:unresolved.setdefault(name,[]).append(dict(from_member=m,line=row['line']))
missing=[x for x in F if x['included']and not x['selected']]
hooks=[]
for tag in ('BeforeCompile','BeforeMake','AfterMake'):
 e=T.find('./TargetOption/TargetCommonOption/'+tag);hooks.append(dict(stage=tag,fields={}if e is None else{ch.tag:ch.text for ch in e},executed=False))
flash=T.find('./TargetOption/Utilities');link=T.find('./TargetOption/TargetArmAds/LDads');cad=T.find('./TargetOption/TargetArmAds/Cads');aads=T.find('./TargetOption/TargetArmAds/Aads')
closure=dict(kind='ACTUAL_KEIL_STATIC_CLOSURE_SELECTED_GAPS_NOT_A_TARGET_BUILD',source_lock=rec(O/'SOURCE.json'),project_member=project,target=T.findtext('TargetName'),toolset=T.findtext('ToolsetName'),pArmCC=T.findtext('pArmCC'),pCCUsed=T.findtext('pCCUsed'),device=T.findtext('./TargetOption/TargetCommonOption/Device'),pack=T.findtext('./TargetOption/TargetCommonOption/PackID'),CPU=T.findtext('./TargetOption/TargetCommonOption/Cpu'),C_flags={}if cad is None else{e.tag:e.text for e in cad if len(e)==0},C_defines=T.findtext('./TargetOption/TargetArmAds/Cads/VariousControls/Define'),ASM_defines=T.findtext('./TargetOption/TargetArmAds/Aads/VariousControls/Define'),include_paths=incs,linker={}if link is None else{e.tag:e.text for e in link},flash_configuration=[]if flash is None else[(e.tag,e.text)for e in flash.iter()if len(e)==0],hooks=hooks,members=F,missing_selected_active_members=missing,missing_from_central_active_members=[x for x in missing if not x['central']],libraries=[x for x in F if x['name'].lower().endswith('.lib')],startup=[x for x in F if x['name'].lower().endswith(('.s','.asm'))],scatter_candidate=existence(PREFIX+'MDK-ARM/standard_tpye_c/standard_tpye_c.sct'),lexical_include_edges=Q,unresolved_lexical_include_names=unresolved,conditional_preprocessor_evaluated=False,compiler_builtin_headers_or_devicepack_existence_checked=False,library_binary_ABI_checked=False,full_build_ready=False,full_target_builds=0,archive_opened=False,old_hooks_executed=False)
out('BUILD_CLOSURE.json',closure)
out('NEEDED_MEMBERS.json',dict(kind='EXACT_PARENT_EXTRACTION_REQUEST_NO_PAYLOAD_OPENED',active_project_members=missing,resolved_lexical_headers_in_central_not_selected=list({x['resolved']['member']:x['resolved']for x in Q if x['resolved']['central']and not x['resolved']['selected']}.values()),unresolved_lexical_names=list(unresolved),note='Do not substitute dummy AHRS/CMSIS or silently delete music. Parent must approve exact members and compiler/library ABI before target link; header list is lexical and conditional, not a proven preprocessed closure.'))
# New independent project preserves all original bytes. No old path is a write target.
for m,b in raws.items():
 p=O/'derived'/Path(*PurePosixPath(m).parts);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(b)
out('COPIED_ORIGINALS.json',dict(count=len(raws),bytes=sum(map(len,raws.values())),files=rs,all_destination_SHA_match=all(sha((O/'derived'/Path(*PurePosixPath(m).parts)).read_bytes())==sha(b)for m,b in raws.items()),patches_applied=False))
print(json.dumps(dict(status='SOURCE_LOCK_AND_STATIC_CLOSURE_AND_391_RAW_BYTE_COPY_COMPLETE',members=len(F),selected_active=sum(x['included']and x['selected']for x in F),missing_active=len(missing),exact_missing=[dict(member=x['member'],central=x['central'],bytes=x['central_bytes'])for x in missing],unresolved_lexical_names=list(unresolved),lexical_edges=len(Q),source=rec(O/'SOURCE.json'),closure=rec(O/'BUILD_CLOSURE.json')),indent=2))
