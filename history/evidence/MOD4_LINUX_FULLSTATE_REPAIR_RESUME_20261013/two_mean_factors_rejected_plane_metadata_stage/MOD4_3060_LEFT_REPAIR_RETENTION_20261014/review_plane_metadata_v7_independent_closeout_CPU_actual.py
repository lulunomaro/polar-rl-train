"""Prepared readonly actual V7 reader, never imports or runs a dispatcher."""
from pathlib import Path
import argparse,hashlib,json,sys,time
import numpy as np
D=Path(__file__).parent;P=D/'payload';sys.path.insert(0,str(P))
from represented_native_plane_CPU_component_v2 import represented_plane_from_readonly_metadata,compare_actual_hit_readonly
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def J(p):return json.loads(Path(p).read_bytes())


def main():
 p=argparse.ArgumentParser()
 for k in ('attempt','boundary','output'):p.add_argument('--'+k,required=True)
 a=p.parse_args();A=Path(a.attempt);O=A/'output';out=Path(a.output);assert not out.exists()
 boundary=J(a.boundary)
 assert all(boundary[x] is True for x in ('actual_parent_absent','actual_child_absent','shared_OS_lock_free'))
 manifest=J(P/'RETENTION_PLANE_METADATA_CPU_MANIFEST_V7.json')
 parent=J(A/'PARENT_EXIT_RECEIPT.json');natural=J(O/'EXIT_NATURAL.json') if (O/'EXIT_NATURAL.json').exists() else None;complete=J(O/'COMPLETE_ACTUAL.json')
 assert parent['exit_code']==0 and parent['complete_data_contract_present'] is True
 assert natural is None and parent['natural_app_close_present'] is False
 log=(A/'worker.log').read_text(errors='replace')
 assert 'SimulationContext cleared' in log and 'Traceback (most recent call last)' not in log
 # Original missing natural marker is retained; independent actual PID/lock/data closure only.
 assert not (O/'ORIGINAL_ERROR.json').exists() and parent['original_error_present'] is False
 assert parent['no_PPO'] is True and parent['canonical_budget_written'] is False
 assert parent['requested_evaluation_controls']==complete['requested_evaluation_controls']==0
 assert complete['no_policy_actor_constructed'] is True and complete['no_PPO'] is True
 assert complete['all_160_actual_queries_complete'] is True
 assert complete['original_V6_fullcase_failed_unchanged'] is True and complete['three_inherited_skills_complete'] is False
 assert complete['source_reference_only'] is True and complete['actual_shape_local_pose_read'] is False
 assert complete['public_source_to_installed_binary_bitexact_proven'] is False
 assert complete['total_physics_zero_not_claimed'] is True
 assert complete['captured_RNG_before']==complete['captured_RNG_after']
 for row in manifest['package_files']:assert H(A/'source_snapshot'/row['relative'])==row['sha256'],row['relative']
 assert H(A/'source_snapshot'/'RETENTION_PLANE_METADATA_CPU_MANIFEST_V7.json')==H(P/'RETENTION_PLANE_METADATA_CPU_MANIFEST_V7.json')
 source=J(P/'FAILED_V6_FULL1500_FIRST_LAST_XY80_ACTUAL.json')
 assert source['source_raw']['sha256']==manifest['source_positions']['source_raw_sha256']
 independent=represented_plane_from_readonly_metadata(complete['actual_metadata'])
 assert independent==complete['source_reference']
 query=O/'ACTUAL160_NATIVE_PLANE_QUERY_ALLHITS.json'
 assert H(query)==complete['query_file']['sha256'] and query.stat().st_size==complete['query_file']['bytes']
 allhits=J(query);assert allhits['source_positions']==source and allhits['source_reference']==independent
 assert allhits['completed_160_actual_rays'] is True and len(allhits['all_rays'])==160
 phases={'first_before_control':set(),'last_after_reset':set()};rows=[]
 for row in allhits['all_rays']:
  phase=row['phase'];i=row['env_id'];assert phase in phases and i not in phases[phase] and 0<=i<80;phases[phase].add(i)
  assert np.array_equal(np.asarray(row['origin'][:2],dtype=np.float32),np.asarray(source['positions'][phase][i],dtype=np.float32))
  assert row['origin'][2]==10 and row['direction']==[0,0,-1] and row['maximum_distance']==20 and row['query_return']
  assert len(row['selected_plane_hits'])==1
  hit=row['selected_plane_hits'][0]['hit'];assert not hit.get('_serializer_error')
  assert hit['_primary_stub_sha256']==manifest['actual_primary_stub']['actual_sha256']
  check=compare_actual_hit_readonly(independent,hit)
  assert check==row['independent_source_reference_comparison']
  assert check['represented_query_within_original_1e6'] and check['normal_crosscheck_maxabs']<=1e-6
  assert row['original_ideal_Z0_within_1e6']==(abs(hit['position'][2])<=1e-6)
  assert row['original_ideal_normalZ1_within_1e6']==(abs(hit['normal'][2]-1)<=1e-6)
  rows.append(dict(phase=phase,env_id=i,error_m=check['represented_query_error_m'],ideal_Z0=row['original_ideal_Z0_within_1e6']))
 assert all(v==set(range(80)) for v in phases.values())
 audit=complete['SDK_initialization_calls_disclosed'];assert audit['complete_engine_internal_step_count_claimed'] is False
 assert all(v==0 for k,v in audit['counts'].items() if k.startswith('readonly_metadata_and_queries/'))
 report=dict(epoch=time.time(),actual_new_metadata_query_consistency_review=True,source_reference_only=True,
             original_EXIT_NATURAL_missing=True,original_parent_EXIT0=True,
             independent_full_data_PID_out_shared_OS_lock_free_closeout=True,
             original_natural_marker_not_fabricated=True,
             actual_shape_local_pose_read=False,public_source_to_installed_binary_bitexact_proven=False,
             original_V6_fullcase_failed_unchanged=True,three_inherited_skills_complete=False,
             queries=160,maximum_represented_error_m=max(r['error_m'] for r in rows),
             ideal_Z0_false_count=sum(not r['ideal_Z0'] for r in rows),zero_PPO=True,
             unique_parent_zero_PPO_cost_seconds=parent['unique_actual_parent_load_run_save_exit_seconds'],
             no_canonical_operation=True,actual_boundary=boundary,source_reference=independent,
             rows=rows,files=[dict(path=str(x.resolve()),bytes=x.stat().st_size,sha256=H(x)) for x in (query,O/'COMPLETE_ACTUAL.json',A/'PARENT_EXIT_RECEIPT.json')],
             pending_Git_by_root=True)
 out.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k not in ('rows','files','source_reference','actual_boundary')},indent=2))

if __name__=='__main__':main()
