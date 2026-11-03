"""V5: read four saved JSON metadata files only; no archive, source payload or native tool."""
from pathlib import Path,PurePosixPath,PureWindowsPath
from collections import deque,Counter
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parent
BASE=PureWindowsPath(str(R/'MOD4_DEPLOYMENT_PORT_V1'/'derived'/'StandardRobotpp-balance1'))
FILES={'selection':'DEPLOYED_BASELINE_AUDIT_V1/SELECTED_SOURCE_MANIFEST.json','central':'DEPLOYED_BASELINE_AUDIT_V1/CENTRAL_DIRECTORY.json','graph':'MOD4_DEPLOYMENT_PORT_V1/BUILD_CLOSURE_FINAL.json','argv':'MOD4_DEPLOYMENT_TARGET_COMPILE_V4/LITERAL_ARGV_V4_01.json'}
def record(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'SHA':hashlib.sha256(b).hexdigest()}
def save(n,x):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def tu_member(t):return 'StandardRobotpp-balance1/'+PureWindowsPath(t['source']).relative_to(BASE).as_posix()
def incdirs(t):
 a=t['argv'];return [a[i+1]for i,x in enumerate(a[:-1])if x=='-I']
def absdir(t,s):
 # Pure string normalization: no source/header stat, opening or resolving.
 p=PureWindowsPath(s)
 if not p.is_absolute():p=PureWindowsPath(t['cwd'])/p
 parts=[]
 for x in p.parts:
  if x=='..':assert len(parts)>1;parts.pop()
  elif x!='.':parts.append(x)
 return str(PureWindowsPath(*parts)).casefold()
def shortest(root,target,adj):
 root=root.casefold();target=target.casefold();q=deque([root]);prev={root:None}
 while q:
  n=q.popleft()
  if n==target:
   out=[]
   while prev[n]is not None:
    e=prev[n];out.append({'from_member':e['from_member'],'line':e['line'],'include':e['include'],'to_member':e['resolved']['member']});n=e['from_member'].casefold()
   return list(reversed(out))
  for e in adj.get(n,[]):
   nxt=e['resolved']['member'].casefold()
   if nxt not in prev:prev[nxt]=e;q.append(nxt)
 return None
method=R/'MOD4_DEPLOYMENT_DEPENDENCY_STATIC_V5'/'METHOD.json';assert method.is_file();method_before=record(method)
inputs={};data={}
for k,n in FILES.items():
 p=R/n;b=p.read_bytes();inputs[k]={'path':str(p),'bytes':len(b),'SHA':hashlib.sha256(b).hexdigest()};data[k]=json.loads(b)
assert inputs['selection']['SHA']=='33a79a69e5ebd1be437b05c75de378359d969f63d0761aa9303e79ce2a47a98d'
assert inputs['graph']['SHA']=='7a2d081ad9754791b6912b10d0f1949a64a3d76aebda13feb62a1934099570ca'
assert inputs['argv']['SHA']=='163cfb3326d48b2612bda4bfe8e5d17345ab2e53ae2f89301b2fd5c373814fa4'
selection,central,graph,argv=(data[k]for k in ('selection','central','graph','argv'))
assert central['entry_count']==len(central['members'])==1184 and selection['selected_text_count']==391
reason='selected_suffix_not_decodable_text';domain_rejections=[];chosen=[]
for e in selection['excluded']:
 p=PurePosixPath(e['member']);parts=p.parts
 if e['reason']!=reason or len(parts)<3 or parts[0]!='StandardRobotpp-balance1'or parts[1]not in ('Drivers','Middlewares'):continue
 domain_rejections.append(e)
 if p.suffix.casefold()!='.h':continue
 assert not p.is_absolute()and all(x not in ('.','..')for x in parts)
 assert type(e['bytes'])is int and 0<=e['bytes']<1048576;chosen.append(e)
assert len(chosen)<=32 and sum(x['bytes']for x in chosen)<=2097152
assert len({x['member'].casefold()for x in chosen})==len(chosen)
tus=argv['translation_units'];assert len(tus)==163 and len({t['id']for t in tus})==163 and Counter(t['language']for t in tus)=={'C':162,'ASM':1}
edges=graph['lexical_edges'];adj={}
for e in edges:
 if e.get('resolved')and e['resolved'].get('member'):adj.setdefault(e['from_member'].casefold(),[]).append(e)
candidates=[]
for e in chosen:
 member=e['member'];matches=[x for x in central['members']if x['name']==member];assert len(matches)==1;c=matches[0]
 assert c['bytes']==e['bytes']and not c['is_directory']and not c['symlink'];crc=c['CRC32'];assert len(crc)==8 and int(crc,16)>=0
 sites=[x for x in edges if x.get('resolved')and x['resolved'].get('member','').casefold()==member.casefold()]
 assert all(x['resolved']['CRC32']==crc and x['resolved']['provided']is False and x['conditional_preprocessor_evaluated']is False for x in sites)
 roots=[];witnesses=[]
 for t in tus:
  path=shortest(tu_member(t),member,adj)
  if path is not None:
   roots.append({'id':t['id'],'name':t['name'],'language':t['language'],'direct':len(path)==1})
   if len(witnesses)<3:witnesses.append({'TU_id':t['id'],'source_member':tu_member(t),'path':path})
 original_parent=PurePosixPath(member).parent;expected_dir=absdir(tus[0],str(BASE.joinpath(*original_parent.parts[1:])))
 literal_ids=[];actual_argv_ids=[]
 for t in tus:
  if any(absdir(t,x)==expected_dir for x in t['literal_includes']):literal_ids.append(t['id'])
  if any(absdir(t,x)==expected_dir for x in incdirs(t)):actual_argv_ids.append(t['id'])
 assert literal_ids==actual_argv_ids
 overlay_rel='header_overlay/'+PurePosixPath(member).relative_to('StandardRobotpp-balance1').as_posix()
 candidates.append({'member':member,'bytes':e['bytes'],'CRC32':crc,'original_exclusion_reason':e['reason'],'excluded_record':e,'central_match':c,'payload_SHA':None,'actual_payload_encoding':'UNKNOWN_NOT_READ','direct_saved_lexical_sites':[{'from_member':x['from_member'],'line':x['line'],'include':x['include'],'conditional_preprocessor_evaluated':False}for x in sites],'possible_TU_roots':roots,'possible_TU_counts':dict(Counter(x['language']for x in roots)),'shortest_path_witness_examples':witnesses,'same_original_parent_in_literal_include_TU_ids':literal_ids,'same_original_parent_in_actual_argv_I_TU_ids':actual_argv_ids,'proposed_overlay_header_relative_to_future_variant':overlay_rel,'proposed_overlay_I_template':'-I<PARENT_NEW_VARIANT>/'+str(PurePosixPath(overlay_rel).parent),'proposed_applicability':'C TUs whose frozen literal/actual includes already select the original header directory; not new executable argv or approval.','relevance_limit':'Saved lexical possibility, not evaluated conditionals. A root with no saved path is not proof of independence. Missing header internal includes remain UNKNOWN until separate payload authorization.'})
for k,n in FILES.items():assert record(R/n)==inputs[k]
assert record(method)==method_before
result={'status':'SEALED_STATIC_V5_ENCODING_OMISSION_HEADER_PLAN_ONLY_NOT_PAYLOAD_OR_COMPILE_APPROVAL','method':method_before,'metadata_sources':list(inputs.values()),'four_metadata_inputs_unchanged':True,'source_payload_read_count':0,'archive_open_count':0,'native_toolchain_count':0,'compile_assemble_link_count':0,'old40_QA_PHY_Git_agent_rootgoal_count':0,'new_project_parser_or_source_scan':False,'header_count':len(candidates),'total_header_payload_bytes_proposed_not_read':sum(x['bytes']for x in candidates),'bounds':{'max_headers':32,'per_header_strictly_less_than':1048576,'total_at_most':2097152},'domain_decoding_rejection_count_all_suffixes':len(domain_rejections),'domain_decoding_rejection_suffix_counts':dict(Counter(PurePosixPath(x['member']).suffix.casefold()for x in domain_rejections)),'coding_omission_category_exhausted_for_this_saved_manifest_and_domain':True,'not_all_dependencies_closed':True,'frozen_TU_count':163,'candidates':candidates,'not_inferred':['payload bytes/charset/SHA','new header transitive/conditional includes','preprocessed closure','all-target/library ABI','hardware/flash/send qualification']}
save('HEADER_OVERLAY_PLAN_V5.json',result)
summary={'status':result['status'],'header_count':len(candidates),'proposed_header_bytes':result['total_header_payload_bytes_proposed_not_read'],'metadata_inputs':len(inputs),'headers':[{'member':x['member'],'bytes':x['bytes'],'CRC32':x['CRC32'],'direct_saved_sites':len(x['direct_saved_lexical_sites']),'possible_TU_counts':x['possible_TU_counts'],'literal_include_TU_count':len(x['same_original_parent_in_literal_include_TU_ids']),'proposed_I':x['proposed_overlay_I_template']}for x in candidates],'plan':record(O/'HEADER_OVERLAY_PLAN_V5.json'),'script':record(Path(__file__).resolve()),'payload_or_native_count':0}
save('STATIC_RESULT_V5.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
