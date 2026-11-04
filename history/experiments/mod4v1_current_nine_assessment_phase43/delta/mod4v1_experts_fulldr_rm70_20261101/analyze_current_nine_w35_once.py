"""One functional pass over this NEW assessment's W35 rows, unchanged original booleans."""
from pathlib import Path
import json,hashlib,collections,re
from project_connector import connect72
T=Path(__file__).resolve().parent;A=T.parent/'mod4v1_current_nine_assessment_20261104';out=A/'reports/W35_ORIGINAL_SPLIT_RESULT.json';mark=A/'W35_ROW_ANALYSIS_STARTED_ONCE.json';assert not out.exists()and not mark.exists();closed=json.loads((A/'reports/QUALIFIED_CLOSED_RESULT.json').read_bytes());row=next(r for r in closed['rows']if r['role']=='W35');f=row['final'];assert row['qualified_execution']and f['controls']==1600 and f['num_envs']==80 and f['source_cache']['source_SHA']=='8d6a9ab5fae3fd2689c59bcfc1f1e776eb162b8eef671417df0fc88150285c54';m=f['skill']['original_RM70_interval_route_facts']['producer'];assert m['path'].startswith(closed['root']+'/cases/W35/')and m['schema_path'].startswith(closed['root']+'/cases/W35/');H=lambda b:hashlib.sha256(b).hexdigest()
with mark.open('x',encoding='utf8')as z:json.dump(dict(root=closed['root'],raw=m['path'],schema=m['schema_path'],new_assessment_functional_completion_analysis=True,model_SDK_oldraw_operations=0),z,indent=2)
c=connect72();s=c.open_sftp()
try:
 with s.open(m['path'],'rb')as z:raw=z.read(m['bytes']+1)
 with s.open(m['schema_path'],'rb')as z:header=z.read(m['schema_bytes']+1)
 logs=[]
 bad_pattern=re.compile(r'PhysX error|CUDA (?:error|out of memory)|(?:contact|patch|pairs).{0,100}(?:overflow|buffer (?:is )?full|capacity.{0,25}(?:exceed|too small))',re.I)
 for role_row in closed['rows']:
  name=role_row['role'];path=closed['root']+'/cases/'+name+'/SDK_FULL_STDOUT_STDERR.log'
  with s.open(path,'rb')as z:log=z.read()
  bad=[line for line in log.decode('utf8','replace').splitlines()if bad_pattern.search(line)]
  logs.append(dict(role=name,path=path,bytes=len(log),SHA256=H(log),full_physical_reads=1,capacity_or_CUDA_error_lines=bad))
finally:s.close();c.close()
assert(len(raw),H(raw),len(header),H(header))==(m['bytes'],m['SHA'],m['schema_bytes'],m['schema_SHA']);h=json.loads(header);assert h['source_model_SHA']==f['source_cache']['source_SHA'];schemas={v['schema_id']:v for v in h['schemas']};rows=[];by=collections.Counter()
for line in raw.splitlines():
 sid,values=json.loads(line);schema=schemas[sid];assert len(values)==len(schema['positional_fields']);r=dict(schema['constants']);r.update(zip(schema['positional_fields'],values));assert set(r)==set(schema['fields'])and r['source_SHA']==f['source_cache']['source_SHA'];rows.append(r);by[sid]+=1
assert len(rows)==m['rows']and[by[i]for i in range(len(schemas))]==m['rows_by_schema'];cmd=[r for r in rows if r['record_type']=='same_UID_original_RM70_command'];route=[r for r in rows if r['record_type']=='same_episode_original_catalog_route'];complete=[r for r in cmd if r['natural_complete_nonterminal_interval']]
def stats(group):
 n=len(group);success=sum(bool(r['complete_interval_bounds_fact'])for r in group)
 return dict(n=success,N=n,rate=success/n if n else None,all_original_nonterminal_and_notimeout=all(not r['terminated_before_reset']and not r['truncated_before_reset']for r in group),along_speed_mean=sum(r['along_speed_m_s']for r in group)/n if n else None)
v=dict(kind='CURRENT_ASSESSMENT_W35_ORIGINAL_MOVING_STANDING_SINGLE_PASS',root=closed['root'],source_SHA=f['source_cache']['source_SHA'],raw=dict(path=m['path'],bytes=len(raw),SHA256=m['SHA'],physical_reads=1,rows=len(rows)),schema=dict(path=m['schema_path'],bytes=len(header),SHA256=m['schema_SHA'],physical_reads=1),moving_complete=stats([r for r in complete if not r['standing']]),standing_complete=stats([r for r in complete if r['standing']]),moving_partial=sum(not r['natural_complete_nonterminal_interval']and not r['standing']for r in cmd),standing_partial=sum(not r['natural_complete_nonterminal_interval']and r['standing']for r in cmd),total_commands=len(cmd),route_episodes=len(route),observed_catalog_goal_count=sum(bool(r['observed_nonterminal_catalog_goal_fact'])for r in route),original_CAD_span_reached=sum(bool(r['entire_original_CAD_x_span_reached'])for r in route),retention_limited=m['retention_limited'],dropped_rows=m['dropped_rows'],diagnostic_errors=f['skill']['original_RM70_interval_route_facts']['diagnostic_errors'],original_boolean_predicates_unchanged=True,goal_is_observer_not_training_target=True,whole_expert_graduation=None,closed_log_checks=logs,all_closed_logs_free_of_capacity_or_CUDA_errors=not any(x['capacity_or_CUDA_error_lines']for x in logs),model_SDK_oldraw_operations=0)
with out.open('x',encoding='utf8')as z:json.dump(v,z,indent=2,allow_nan=False)
print(json.dumps(v,indent=2))
