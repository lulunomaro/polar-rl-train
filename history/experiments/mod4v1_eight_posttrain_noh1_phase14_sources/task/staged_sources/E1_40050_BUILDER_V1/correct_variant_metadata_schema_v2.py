"""Saved metadata schema casing normalization; preserve V1raw/UNKNOWNs, no PT."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;T=B.parent.parent;L=T/'legacy_source_joins';original=[];normalized=[]
for family,path in [('CURB',L/'E1_CURB20_SOURCE_JOIN_v1.json'),('SLOPE',L/'E1_SLOPE5_SOURCE_JOIN_v1.json')]:
 raw=path.read_bytes();j=json.loads(raw);original.append(dict(path=str(path),SHA=hashlib.sha256(raw).hexdigest()))
 for v in j['variants']:
  m=v.get('model',{});sha=m.get('sha256',m.get('SHA'));assert sha and len(sha)==64
  normalized.append(dict(family=family,alias=v['alias'],original_source_SHA=sha,historical_source_path=m.get('path',m.get('checkpoint')),source_bytes=v.get('model_bytes',m.get('bytes','UNKNOWN')),saved_iteration=m.get('iteration_stored',v.get('stored_iteration','UNKNOWN_NOT_PROVEN_FROM_SAVED_METADATA')),saved_LR=v.get('saved_LR','UNKNOWN_NOT_PROVEN_FROM_SAVED_METADATA'),saved_Adam17=v.get('Adam17_step',m.get('Adam_step','UNKNOWN_NOT_PROVEN_FROM_SAVED_METADATA')),saved_source_keys=m.get('keys','UNKNOWN_NOT_IN_SAVED_METADATA'),selection_level=v.get('selection_level','EXPLICIT_SAVED_SCOPE_SEE_PROVENANCE_JOIN'),frozen=v.get('frozen','UNKNOWN_NOT_PROVEN_FROM_METADATA'),review_only_not_selected=v.get('qualified_selected') is False or 'REVIEW_ONLY' in v['alias'],new_GPU_or_skill_qualification=False,no_maxiter_or_rank_substitution=True))
assert len(normalized)==6
for name,pin in [('CURB141','7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43'),('SLOPE135','24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411')]:
 root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');old=root/'EXPLICIT_FROZEN_VARIANTS_SCOPE_V1.json';oldraw=old.read_bytes();canonical=next(v for v in normalized if v['original_source_SHA']==pin);keys=canonical['saved_source_keys'];rows=[]
 for v in normalized:
  x=dict(v);x['runtime_adaptation_scope']='THIS_CANONICAL_SOURCE_ONLY_IMPLEMENTED_NOT_EXECUTED' if v['original_source_SHA']==pin else 'VARIANT_SPECIFIC_FULLSTATE_HELPER_PENDING_NOT_DROPPED_OR_CLOSED'
  x['extra_vs_canonical_keys']=sorted(set(v['saved_source_keys'])-set(keys)) if isinstance(v['saved_source_keys'],list) and isinstance(keys,list) else 'UNKNOWN_VARIANT_SPECIFIC_STATE_KEYSET_REVIEW_PENDING'
  rows.append(x)
 with (root/'EXPLICIT_FROZEN_VARIANTS_SCOPE_V2.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SAVED_VARIANT_SCHEMA_NORMALIZED_SOURCE_ONLY_NOT_ALLHISTORY_CLOSED',canonical=name,rows=rows,original_joins=original,preserved_V1_path=str(old),preserved_V1_SHA=hashlib.sha256(oldraw).hexdigest(),reader_correction='Three later model receipts use SHA/Adam_step/checkpoint orpath, not earlysha256/Adam17_step. V1partialnulls preserved; V2binds actualsavedreceiptfields only, no PT/arithmetic.',shared878_one_actor_rankshards_not_SLOPE=True,independent113_G3sibling_not878descendant=True,all_historical_variants_closed=False),f,indent=2)
 with (root/'VARIANT_METADATA_READER_SCHEMA_ERROR_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='METADATA_READER_FIELD_CASE_VARIANT_MISMATCH_PRESERVED',V1_source_scope=str(old),error='V1lookedsha256/Adam17_step for later receipts that useSHA/Adam_step; threeSHA nulls +counterUNKNOWN were metadatareadererrors, not missingmodels',V2_additive_corrected_fields_only=True,PT_stats_reads_hashes_decodes=0),f,indent=2)
 print(name,'six exactSHA/actualsavedcounter rows normalized, extra states remainpending')
