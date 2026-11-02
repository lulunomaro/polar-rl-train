"""Preserve V3sealedsource; fix exactlegacy GO ReadyJSONhash key, not GPUfullrestore field.
Static owner/protocol fieldcrosschecks before any Task/GO/SDK/source load.
"""
from pathlib import Path
import ast,json,hashlib,shutil
R=Path(__file__).resolve().parent;S=R/'staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V3';D=R/'staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4';assert not D.exists();shutil.copytree(S,D);p=D/'runtime/isaac/mod4/mod4v1_w35_protocol.py';s=p.read_text(encoding='utf-8');assert s.count("'source_GPU_RESTORE_SHA'")==2;s=s.replace("'source_GPU_RESTORE_SHA'","'source_CPU_SHA'");ast.parse(s);p.write_text(s,encoding='utf-8')
owner=ast.parse((R/'w35_mod4v1_finite_original_owner_v3.py').read_text(encoding='utf-8'));protocol=ast.parse(s)
def assigned_dict_keys(tree,name):
 ds=[n.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)and isinstance(n.value,ast.Dict)];assert len(ds)==1;(d,)=ds;return {k.value for k in d.keys if isinstance(k,ast.Constant)and isinstance(k.value,str)}
def literal_reads(tree,name):return {n.slice.value for n in ast.walk(tree)if isinstance(n,ast.Subscript)and isinstance(n.value,ast.Name)and n.value.id==name and isinstance(n.slice,ast.Constant)and isinstance(n.slice.value,str)}
go=assigned_dict_keys(owner,'go');task=assigned_dict_keys(owner,'task');ready=assigned_dict_keys(owner,'ready');expected=next(n.value for n in ast.walk(protocol)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='expected'for t in n.targets));expectedkeys={k.arg for k in expected.keywords};assert literal_reads(protocol,'go')<=go and literal_reads(protocol,'task')|expectedkeys<=task
# The remaining ready[key] loop explicitly uses dict(...) at the correct fornode.
readychecks=[]
for n in ast.walk(protocol):
 if isinstance(n,ast.For)and isinstance(n.iter,ast.Call)and isinstance(n.iter.func,ast.Attribute)and n.iter.func.attr=='items'and isinstance(n.iter.func.value,ast.Call)and isinstance(n.iter.func.value.func,ast.Name)and n.iter.func.value.func.id=='dict' and any(isinstance(x,ast.Subscript)and isinstance(x.value,ast.Name)and x.value.id=='ready'for x in ast.walk(n)):
  readychecks.extend(k.arg for k in n.iter.func.value.keywords)
assert set(readychecks)<=ready and 'source_CPU_SHA'in go and 'source_GPU_fullrestore_proof_SHA'in task and 'GPU_RESTORE_SHA'in s
for path in D.rglob('*.py'):ast.parse(path.read_text(encoding='utf-8'))
ix=D/'MOD4V1_DERIVATION_INDEX.json';index=json.loads(ix.read_bytes());index['parent_sealed_source_V3_index_SHA']=hashlib.sha256((S/'MOD4V1_DERIVATION_INDEX.json').read_bytes()).hexdigest();index['fix_scope']='Only GO originalsource_CPU_SHA ReadyJSONhash key accidentallychangedbysubstringrename; actualGPU_RESTORE_SHA proofvariable/source_GPU_fullrestore_proof_SHA staynewGPUproof';outputs=[]
for path in sorted(D.rglob('*')):
 if path.is_file()and path.name not in('MOD4V1_DERIVATION_INDEX.json','INSTALL_OVERLAY_SOURCE_MAP.json'):
  raw=path.read_bytes();outputs.append({'relative':path.relative_to(D).as_posix(),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
index['outputs']=outputs;ix.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');m=D/'INSTALL_OVERLAY_SOURCE_MAP.json';mapping=json.loads(m.read_bytes());mapping['files']=outputs;m.write_text(json.dumps(mapping,indent=2),encoding='utf-8')
old=R/'deploy_w35_finite_mod4v1_resume89aca_v4_once.py';new=R/'deploy_w35_finite_mod4v1_resume89aca_v5_once.py';assert not new.exists();s=old.read_text(encoding='utf-8').replace('W35_MOD4V1_RESUME89ACA_SOURCE_V3','W35_MOD4V1_RESUME89ACA_SOURCE_V4');ast.parse(s);new.write_text(s,encoding='utf-8');result={'kind':'STATIC_GO_HASH_NAME_JOIN_FIXED_BEFORE_EXECUTION','new_package':str(D),'V3sealedpreserved':True,'GOlegacyReadyhash_key':'source_CPU_SHA','actual_selectedsource_proof_field':'source_GPU_fullrestore_proof_SHA','owner_GO_keys':sorted(go),'ownerTask_keys':sorted(task),'ready_crosscheck_keys':readychecks,'protocolLiteralReads_GOmatch':True,'protocolLiteralAndExpectedTaskKeys_match':True,'index_SHA':hashlib.sha256(ix.read_bytes()).hexdigest(),'new_deployer_SHA':hashlib.sha256(new.read_bytes()).hexdigest(),'PT_SDK_GO_canonical_actions':0,'failures':'V3fixedspaceanchor failedbeforeowner; V4ownercreated/accountASTsame butdeployeranchor failedbeforeremote; bothoriginalpreparerskept. Protocol globalCPU_SHA renamealsoalteredlegacyGOkeyfoundbygrepbeforeanyGO; correctedonlyliteralkeysinnewV4.'};out=R/'reports/W35_RESUME_V4_PROTOCOL_OWNER_JOIN_CHECK.json';assert not out.exists();out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
