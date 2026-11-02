"""One declared CPU read of this NEW evaluator's complete, bounded telemetry only.
No checkpoint, legacy raw, training, SDK, writer or budget accesses.
"""
from pathlib import Path
import json,hashlib,collections,math,statistics,sys
B=Path(sys.argv[1]);O=B/'actual_latest32';rawpath=O/'RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl';schema=O/'RM70_SAME_UID_COMMAND_AND_ROUTE_SCHEMAS227.json'
plan=json.loads(Path(sys.argv[2]).read_bytes());assert str(B)==plan['job'] and plan['source_parent_SHA']=='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f' and plan['source_model_SHA']==plan['actual_saved_source_producer_metadata']['SHA'] and plan['actual_saved_source_producer_metadata']['source_SHA']==plan['source_parent_SHA']
EXPECTED_BYTES=plan['producer']['bytes'];EXPECTED_SHA=plan['producer']['SHA']
assert plan['actual_eval_passed_execution'] and plan['actual_eval_complete32s'] and plan['actual_parent_all_children_waited_released']
assert not plan['producer']['retention_limited'] and plan['producer']['dropped_rows']==0 and plan['producer']['rows']==sum(plan['producer']['rows_by_schema'])
assert str(rawpath)==plan['producer']['path'] and rawpath.stat().st_size==EXPECTED_BYTES
hb=schema.read_bytes();assert str(schema)==plan['producer']['schema_path'] and len(hb)==plan['producer']['schema_bytes'] and hashlib.sha256(hb).hexdigest()==plan['producer']['schema_SHA']
header=json.loads(hb);assert header['format']=='mod4.227.lossless_fieldset_positional_jsonl.v1'
for i,s in enumerate(header['schemas']):assert s['schema_id']==i and set(s['fields'])==set(s['constants'])|set(s['positional_fields']) and not(set(s['constants'])&set(s['positional_fields']))
count=collections.Counter();end=collections.Counter();by=collections.defaultdict(collections.Counter);values=collections.defaultdict(list);samples=[];routes=[];sha=hashlib.sha256();total=0;rowcount=0;last_model=None
with rawpath.open('rb')as f:
 for line in f:
  total+=len(line);assert total<=EXPECTED_BYTES;sha.update(line);sid,items=json.loads(line);s=header['schemas'][sid];assert len(items)==len(s['positional_fields']);r=dict(s['constants']);r.update(zip(s['positional_fields'],items));rowcount+=1;kind=r['record_type'];count[kind]+=1;end[(kind,r.get('end_reason',''))]+=1
  if r.get('source_SHA') is not None:assert r['source_SHA']==plan['source_model_SHA']
  if kind=='same_UID_original_RM70_command':
   complete=bool(r['natural_complete_nonterminal_interval']);standing=bool(r['standing']);label=('stand' if standing else 'moving')+('_complete' if complete else '_partial');by[label]['count']+=1;by[label]['bounds_met']+=int(bool(r['original_kinematic_bounds_met']));by[label]['terminated']+=int(bool(r['terminated_before_reset']));by[label]['truncated']+=int(bool(r['truncated_before_reset']))
   v=float(r['nominal_speed']);band='v<.03' if v<.03 else '.03<=v<.1' if v<.1 else '.1<=v<.2' if v<.2 else '.2<=v<=.3';key=label+' '+band;by[key]['count']+=1;by[key]['bounds_met']+=int(bool(r['original_kinematic_bounds_met']))
   if complete:
    for name in ('along_speed_m_s','cross_speed_m_s','along_nominal_error_m_s','BODY_reference_along_tracking_error_m_s','BODY_reference_cross_tracking_error_m_s','signed_yaw_error_rad_s','seconds','maximum_closure_m','maximum_mimic_rad'):values[label+' '+name].append(float(r[name]))
  if kind=='same_episode_original_catalog_route':
   by['route']['count']+=1
   for field in ('observed_reset_origin','entire_original_CAD_x_span_reached','terminated_before_reset','truncated_before_reset','observed_nonterminal_catalog_goal_fact'):by['route'][field]+=int(bool(r[field]))
   by['route']['any_goal_entry']+=int(r['catalog_goal_entry_control']>=0)
   x0=float(r['local_x_min']);x1=float(r['local_x_max']);values['route local_x_min'].append(x0);values['route local_x_max'].append(x1);values['route x_range'].append(x1-x0);values['route controls'].append(float(r['last_control'])-float(r['first_control']))
   label='route_even' if r['env_id']%2==0 else 'route_odd';by[label]['count']+=1;by[label]['span_flag']+=int(bool(r['entire_original_CAD_x_span_reached']));by[label]['goal']+=int(r['catalog_goal_entry_control']>=0)
   if len(samples)<16:samples.append(r)
assert total==EXPECTED_BYTES and sha.hexdigest()==EXPECTED_SHA and rowcount==plan['producer']['rows']
summ={}
for k,v in values.items():
 v.sort();n=len(v);summ[k]={'n':n,'min':v[0],'q10':v[int((n-1)*.1)],'median':v[(n-1)//2],'q90':v[int((n-1)*.9)],'max':v[-1],'mean':sum(v)/n}
result={'kind':'MOD4V1_W35_AFTER_RESUME89ACA_OWN32S_CPU_ONEPASS_V1','status':'COMPLETE_OWN_CASE_BOUND_AND_SHA_VERIFIED','source_file':str(rawpath),'source_bytes':total,'source_SHA':sha.hexdigest(),'schema_bytes':len(hb),'schema_SHA':hashlib.sha256(hb).hexdigest(),'source_rows':rowcount,'raw_opens':1,'schema_opens':1,'PT_opens':0,'SDK_or_canonical_access':False,'counts':dict(count),'end_reasons':[{'record_type':k[0],'reason':k[1],'count':v} for k,v in end.items()],'groups':{k:dict(v) for k,v in by.items()},'distributions':summ,'route_samples':samples,'interpretation_boundary':'Descriptive original-domain measurements, not new aggregate pass threshold; y exposure lacks per-route y extrema, so no fabricated full-route exposure/graduation.'}
p=B/'CPU_AFTER_RESUME89ACA_OWN32S_TELEMETRY_ANALYSIS_V1.json'
with p.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps(result,allow_nan=False))
