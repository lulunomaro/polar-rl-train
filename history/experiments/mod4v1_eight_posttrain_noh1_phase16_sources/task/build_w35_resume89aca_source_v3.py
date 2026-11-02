"""Source-only next finite adaptation from the actuallyevaluated89aca, not old2d.
No model/SDK/budget access. Original learner/asset/reward/STD/physics/accounting unchanged.
"""
from pathlib import Path
import ast,json,hashlib,shutil,difflib
R=Path(__file__).resolve().parent;S=R/'staged_sources/W35_MOD4V1_SOURCE_V2_FINAL';D=R/'staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V3';assert not D.exists();cert=json.loads((R/'staged_sources/W35_89ACA_SOURCE_CERTIFICATE/CERTIFICATE_INDEX.json').read_bytes());source=cert['source'];assert source['SHA']=='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f'and source['saved_iteration']==32561 and source['Adam_min']==652860 and cert['source_actual_LR']==.00011390625000000006
D.mkdir();inputs=[];H=lambda raw:hashlib.sha256(raw).hexdigest()
for p in S.rglob('*'):
 if not p.is_file():continue
 raw=p.read_bytes();rel=p.relative_to(S);inputs.append({'path':str(p),'relative':rel.as_posix(),'bytes':len(raw),'SHA':H(raw)})
 if rel.as_posix()in('MOD4V1_DERIVATION_INDEX.json','INSTALL_OVERLAY_SOURCE_MAP.json'):continue
 q=D/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
oldSHA='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b';oldkind='MOD4V1_W35_LATEST32481_FULLD0D7_RM70_V2';kind='MOD4V1_W35_RESUME32561_FULLD0D7_RM70_V3';oldmodel='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72/production/model_final_complete.pt';changes=[]
for rel in ('worker_mod4v1_w35.py','runtime/isaac/mod4/mod4v1_w35_protocol.py'):
 p=D/rel;before=p.read_text(encoding='utf-8');s=before.replace(oldSHA,source['SHA']).replace(oldkind,kind).replace(oldmodel,source['path']).replace('17619333','17621509').replace('32481','32561').replace('651260','652860').replace('.0002562890625000001','.00011390625000000006').replace('source_prior_new_PPO_updates=77','source_prior_new_PPO_updates=80').replace('PRIOR_UPDATES = 32561, 652860, 77','PRIOR_UPDATES = 32561, 652860, 80')
 if rel=='worker_mod4v1_w35.py':
  s=s.replace("cache.state['actual_new_PPO_updates']==77","cache.state['actual_new_PPO_updates']==80")
  a="assert cache.state['typed_W35_RM70_task']['kind']=='MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227'";b="assert cache.state['typed_W35_RM70_task']['kind']=="+repr(oldkind)+" and cache.state['typed_W35_RM70_task']['source_SHA']=="+repr(oldSHA);assert s.count(a)==1;s=s.replace(a,b)
  s=s.replace("'--run_name','W35_LATEST32561_MOD4V1_FULLDR_RM70'","'--run_name','W35_RESUME32561_MOD4V1_FULLDR_RM70'")
 else:
  s=s.replace('CPU_SHA','GPU_RESTORE_SHA').replace('saved_source_CPU_proof_SHA','source_GPU_fullrestore_proof_SHA').replace('e55cad0a6d1e70b99ed8b527a8d50241c4b30c59f4cdf449842889d2ee84e5fb',cert['restore_proof_SHA']).replace('MOD4V1_W35_REVIEWABLE_SOURCE_ONLY_V2','MOD4V1_W35_REVIEWABLE_RESUME_SOURCE_ONLY_V3').replace('not saved CPU proof','not source GPU-fullrestore proof')
 ast.parse(s);p.write_text(s,encoding='utf-8');changes.extend(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile=rel+'(previous)',tofile=rel+'(resume89aca)'))
# Leave oldhistoricaldiff/history as provenance; replace operationalsource-only README/requiredmap.
(D/'RESUME89ACA_SOURCE_DIFF.patch').write_text(''.join(changes),encoding='utf-8')
(D/'README.md').write_text('# W35 resume89aca SOURCE_ONLY V3\n\nInput89aca/17621509/32561/652860/actualLR.00011390625000000006/priorwindow80; inputtypedkindV2/sourceparent2d remain asserted, newoutputtypedkindV3/source89aca. Existingnew20kGPUfullrestore/full32/noupdatecertificate, not old2dCPUproof. OriginalGO source_CPU_SHA is only historicalReadyJSONhash convention, not proof that a new CPU modeldecode occurred. Wholecurrentstate/RNG/STD17Adam/fullDR restored thenONEfreshreset, no slicing. Saveclock/Adam=source+20*n/newwindowupdatesn unchanged. Source-only doesnotissueReadyGO or budget.\n\nNo changes to originalPPO/trainer/reward/commands/geometry/material/torques/normalization/STD/physics; after completednegativefull32 and mechanismdiagnostic proving command->obs andprocessed->actualwheel targets wired correctly, onefutureboundedoriginalowner adaptation may proceed. FullRM70graduationstillfalse. Preservepreviouscheckpoint andallfailures.\n',encoding='utf-8')
protocol=ast.parse((D/'runtime/isaac/mod4/mod4v1_w35_protocol.py').read_text(encoding='utf-8'));assert any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GPU_RESTORE_SHA'for t in n.targets)for n in protocol.body)
required=json.loads((S/'REQUIRED_ROOT_INPUTS.json').read_bytes());text=json.dumps(required,ensure_ascii=False,indent=2).replace('saved_source_CPU_proof_SHA','source_GPU_fullrestore_proof_SHA');(D/'REQUIRED_ROOT_INPUTS.json').write_text(text,encoding='utf-8')
# Operational index/map were not copied; write new ones below, without deletes.
outputs=[]
for p in sorted(D.rglob('*')):
 if not p.is_file():continue
 raw=p.read_bytes()
 if p.suffix=='.py':ast.parse(raw.decode('utf-8'))
 outputs.append({'relative':p.relative_to(D).as_posix(),'bytes':len(raw),'SHA':H(raw)})
index={'kind':'MOD4V1_W35_REVIEWABLE_RESUME_SOURCE_ONLY_V3','source_model_metadata':dict(path=source['path'],SHA=source['SHA'],bytes=source['bytes'],iteration=32561,Adam17=652860,LR=cert['source_actual_LR'],prior_new_PPO_updates=80,metadata_only_not_read_or_copied=True),'input_typed_kind_expected':oldkind,'input_source_parent_SHA':oldSHA,'source_GPU_fullrestore_proof_SHA':cert['restore_proof_SHA'],'source_certificate':cert,'generator':{'path':str(Path(__file__).resolve()),'SHA':H(Path(__file__).read_bytes())},'inputs':inputs,'outputs':outputs,'PT_reads':0,'SDK_or_canonical_access':False,'not_generated':['Task','Ready','GO','canonical_copy','PPOupdate']};(D/'MOD4V1_DERIVATION_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');mapping={'kind':'MOD4V1_W35_RESUME89ACA_SOURCE_MAP_NOT_INSTALL_RECEIPT','source_model':index['source_model_metadata'],'files':outputs};(D/'INSTALL_OVERLAY_SOURCE_MAP.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8');print(json.dumps({'source_dir':str(D),'index_SHA':H((D/'MOD4V1_DERIVATION_INDEX.json').read_bytes()),'outputs':len(outputs),'PY_AST':True,'source89aca_kind_join':True,'model_reads':0,'SDK_budget_actions':0},indent=2))
