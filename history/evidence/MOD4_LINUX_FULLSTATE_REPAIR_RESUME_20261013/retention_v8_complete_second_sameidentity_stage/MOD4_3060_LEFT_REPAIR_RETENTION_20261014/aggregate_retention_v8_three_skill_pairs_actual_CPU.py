"""One-shot CPU aggregation of independently reviewed V8 cases; no polling/SSH.

Missing reports are pending in --snapshot-only mode. Normal mode requires all
three own native admissions and all six full cases. This script never decides
whether to continue learning, and never creates a graduation score.
"""
from pathlib import Path
import argparse,hashlib,json,math,time,traceback
import numpy as np
D=Path(__file__).parent
BASE='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
OWN='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'


def H(path):
 digest=hashlib.sha256()
 with Path(path).open('rb') as f:
  while chunk:=f.read(4*1024*1024):digest.update(chunk)
 return digest.hexdigest()


def J(path):return json.loads(Path(path).read_bytes())
def file_index(path):return dict(path=str(Path(path).resolve()),bytes=Path(path).stat().st_size,sha256=H(path))
def canonical_H(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def actual_case_provenance(reports,case,review):
 collectors=sorted(reports.glob(case+'_CURRENT_ACTUAL_*.json'))
 assert collectors,('No own actual collection',case)
 collection_path=collectors[-1];collection=J(collection_path)
 assert collection['case']==case and collection['shared_OS_lock_free'] is True
 assert all(x['actual_alive'] is False for x in collection['actual_PID_identities'])
 marker='attempts/'+case+'/output/COMPLETE_ACTUAL.json'
 own=[x for x in collection['collected_files'] if x['relative'].replace('\\','/')==marker]
 assert len(own)==1,('Own COMPLETE is not uniquely indexed',case)
 attempt=Path(own[0]['local_path']).parent.parent;output=attempt/'output'
 boundary_path=reports/(case+'_INDEPENDENT_BOUNDARY.json');boundary=J(boundary_path)
 assert all(boundary[k] is True for k in ('actual_parent_absent','actual_child_absent','shared_OS_lock_free'))
 assert boundary['complete_dataset_present'] is True and boundary['original_failure'] is None
 parent=J(attempt/'PARENT_EXIT_RECEIPT.json');complete=J(output/'COMPLETE_ACTUAL.json');probe=J(output/'probe.json')
 assert parent['exit_code']==0 and parent['no_PPO'] is True and parent['canonical_budget_written'] is False
 assert parent['original_error_present'] is False and parent['complete_data_contract_present'] is True
 assert not (output/'ORIGINAL_ERROR.json').exists()
 assert complete['checkpoint_sha256']==review['checkpoint_sha256']
 assert complete['num_envs']==review['num_envs'] and complete['steps']==review['steps'] and complete['callbacks']==review['steps']*4
 raw=output/Path(complete['raw']['path']).name
 assert raw.stat().st_size==complete['raw']['bytes'] and H(raw)==complete['raw']['sha256']==review['data']['raw_sha256']
 assert H(output/'probe.json')==review['original_report_sha256']==complete['probe']['sha256']
 relative='attempts/'+case+'/output/'+raw.name
 rawindex=[r for r in collection['collected_files'] if r['relative'].replace('\\','/')==relative]
 assert len(rawindex)==1 and rawindex[0]['two_host_byteSHA_exact'] is True
 assert rawindex[0]['sha256']==review['data']['raw_sha256'] and rawindex[0]['bytes']==raw.stat().st_size
 metadata=probe['native_readonly_witness'];query=J(output/'retention_plane_query_actual.json')
 assert H(output/'retention_plane_query_actual.json')==metadata['actual_plane_query']['sha256']
 binary_files=query['initial']['loaded_PhysX_binary_fingerprints']['files']
 assert binary_files==query['final']['loaded_PhysX_binary_fingerprints']['files']
 assert query['initial']['actual_USD_and_native_actor_metadata']==query['final']['actual_USD_and_native_actor_metadata']
 assert query['initial']['source_reference']==query['final']['source_reference']
 manifest=J(D/'payload/RETENTION_CPU_MANIFEST_V8.json')
 for row in manifest['package_files_v8']:assert H(attempt/'source_snapshot'/row['relative'])==row['sha256'],row['relative']
 assert H(attempt/'source_snapshot/RETENTION_CPU_MANIFEST_V8.json')==H(D/'payload/RETENTION_CPU_MANIFEST_V8.json')
 with np.load(raw,allow_pickle=False) as z:
  terminated=z['terminated'];truncated=z['truncated'];reasons=z['reasons'];done=terminated|truncated
  S,N=done.shape;assert (S,N)==(review['steps'],review['num_envs'])
  reason_names=metadata['reason_names'];reason_timeout=metadata['reason_time_out']
  assert reasons.shape==(S,N,len(reason_names))
  assert int(terminated.sum())==review['data']['ordinary'] and int(truncated.sum())==review['data']['truncation']
  prefixes=[]
  for i in range(N):
   failures=np.flatnonzero(done[:,i]);first=int(failures[0]) if len(failures) else S
   prefixes.append(dict(env_id=i,first_failure_control=first,valid_prefix_controls=first,
       valid_prefix_duration_s=first*.01,full15s_prefix=first==1500,
       failure_reasons=[] if first==S else [name for k,name in enumerate(reason_names) if reasons[first,i,k]],
       post_failure_or_reset_samples_used=False))
  reset_counts=dict(ordinary=int(terminated.sum()),truncation=int(truncated.sum()),
                   unique=int(done.sum()),overlap=int((terminated&truncated).sum()),
                   per_reason={name:dict(count=int(reasons[...,k].sum()),time_out=bool(reason_timeout[name])) for k,name in enumerate(reason_names)})
 return dict(case=case,attempt=str(attempt.resolve()),collection=file_index(collection_path),boundary=file_index(boundary_path),
             parent=file_index(attempt/'PARENT_EXIT_RECEIPT.json'),raw=file_index(raw),probe=file_index(output/'probe.json'),
             source_snapshot=file_index(attempt/'SOURCE_SNAPSHOT_ACTUAL.json'),
             source_actor_SHA=review['checkpoint_sha256'],fixed_manifest_SHA=H(D/'payload/RETENTION_CPU_MANIFEST_V8.json'),
             actual_initial_root_q30_parameters_recipes_RNG_queues_SHA=canonical_H({k:review['initial'][k] for k in ('root','q30','physical_parameters','phase')}),
             loaded_PhysX_binary_files=binary_files,actual_native_actor_and_USD_metadata=query['initial']['actual_USD_and_native_actor_metadata'],
             binary_identity_scope='Own already-loaded PhysX-named DLL/PYD files; not all binaries globally or source-to-binary certification',
             original_missing_EXIT_NATURAL_preserved=not parent['natural_app_close_present'],
             original_flags=review['old_original_flags'],data_audit=review['data'],
             reset_counts=reset_counts,all_valid_prefixes=prefixes,
             actual_parent_unique_zero_PPO_cost_seconds=parent['unique_actual_parent_load_run_save_exit_seconds'])


def validate_result(value,kind,steps,sha):
 assert value['kind']==kind and value['steps']==steps and value['num_envs']=={'flat':80,'spin':88,'world':88}[kind]
 assert value['checkpoint_sha256']==sha and value['full_behavior_review']==(steps==1500)
 d=value['data']
 for key in ('all_controls_and_substeps_finite','actual_q30_policy35_action6_exact','no_reset_teleport_credit',
             'DC_hardware_actual_bounds_exact','COM_frame_original1e5_passed','actual_represented_plane_query_1e6_passed','complete_data_contract'):
  assert d[key] is True,(kind,key)
 assert d['mean_load_integral_error_N']<=.1
 assert d['query_source_reference_only'] and d['native_shape_local_pose_not_directly_read'] and d['public_source_to_binary_bitexact_not_proven']


def flat_compare(base,own):
 b={r['command']:r for r in base['straight']};o={r['command']:r for r in own['straight']};assert set(b)==set(o)=={-1.5,1.5}
 return [dict(command_vx=command,baseline=b[command],candidate=o[command],
              candidate_minus_baseline_error=o[command]['error']-b[command]['error'],
              candidate_minus_baseline_steady_error=o[command]['steady_error']-b[command]['steady_error']) for command in (-1.5,1.5)]


def spin_compare(base,own):
 b={r['command']:r for r in base['pure4pi']};o={r['command']:r for r in own['pure4pi']};assert set(b)==set(o) and len(b)==2
 result=[]
 for command in sorted(b):
  assert abs(abs(command)-4*math.pi)<1e-6 and b[command]['count']==o[command]['count']==8
  bv,ov=b[command]['values'],o[command]['values'];assert len(bv)==len(ov)==8
  result.append(dict(command_yaw_rad_s=command,original_absolute_yaw_error_tolerance=.2,baseline=b[command],candidate=o[command],
      per_paired_sample=[dict(sample_index=i,baseline_yaw=bv[i],candidate_yaw=ov[i],
          baseline_absolute_error=abs(bv[i]-command),candidate_absolute_error=abs(ov[i]-command),
          candidate_minus_baseline_absolute_error=abs(ov[i]-command)-abs(bv[i]-command)) for i in range(8)]))
 return result


def world_compare(base,own):
 assert base['world_sample_count']==own['world_sample_count']==64
 assert base['world_original_tolerance_m_s']==own['world_original_tolerance_m_s']==max(.03,.1*.5)
 bt={r['env_id']:r for r in base['whole_signedcircle_original_target']['rows']};ot={r['env_id']:r for r in own['whole_signedcircle_original_target']['rows']}
 bp={r['env_id']:r for r in base['all_valid_prefixes']};op={r['env_id']:r for r in own['all_valid_prefixes']}
 bm={r['env_id']:r for r in base['fullsignedcircle_actual_prefix']};om={r['env_id']:r for r in own['fullsignedcircle_actual_prefix']}
 assert set(bt)==set(ot)==set(bp)==set(op)==set(bm)==set(om) and len(bt)==64
 rows=[]
 for i in sorted(bt):
  for key in ('group_id','goal_m_s','command_yaw_rad_s'):assert bt[i][key]==ot[i][key],(i,key)
  for prefix in (bp[i],op[i]):assert prefix['post_failure_or_reset_samples_used'] is False
  rows.append(dict(env_id=i,baseline_target=bt[i],candidate_target=ot[i],
                   baseline_complete_signedcircle=bm[i],candidate_complete_signedcircle=om[i],
                   baseline_whole_valid_prefix=bp[i],candidate_whole_valid_prefix=op[i],
                   cross_dedrift_definition='Whole valid prefix endpoint linear cross drift removed; diagnostic only, no new gate'))
 return dict(baseline_count=base['world_count'],candidate_count=own['world_count'],sample_count=64,
             factual_tolerance_m_s=max(.03,.1*.5),improved_envs=[i for i in sorted(bt) if not bt[i]['pass_'] and ot[i]['pass_']],
             regressed_envs=[i for i in sorted(bt) if bt[i]['pass_'] and not ot[i]['pass_']],rows=rows,
             no_incomplete_turn_or_post_failure_credit=True,no_new_dedrift_threshold=True,
             original_target_is_observation_not_learning_veto=True)


def aggregate(reports,snapshot_only):
 native={};pairs={};pending=[];complete_cases={};files=[]
 for kind in ('flat','spin','world'):
  paths={label:reports/(f'retention_{source}_{kind}_{steps}_v8_FULL_CPU_REVIEW.json')
         for label,source,steps in [('native','baseline1aa',120),('baseline','baseline1aa',1500),('candidate','repair2b',1500)]}
  loaded={}
  for label,path in paths.items():
   if not path.exists():pending.append(dict(kind=kind,label=label,reason='actual_full_CPU_review_not_generated',path=str(path.resolve())));continue
   report=J(path);assert report['original_false_and_failure_prefix_preserved'] and report['no_GPU_no_SSH_no_PPO'] and report['qualification_not_claimed']
   loaded[label]=report['result'];files.append(file_index(path))
  if 'native' in loaded:
   value=loaded['native'];validate_result(value,kind,120,BASE)
   native[kind]=actual_case_provenance(reports,f'retention_baseline1aa_{kind}_120_v8',value)
  if 'baseline' in loaded:
   value=loaded['baseline'];validate_result(value,kind,1500,BASE)
   complete_cases[f'baseline_{kind}']=actual_case_provenance(reports,f'retention_baseline1aa_{kind}_1500_v8',value)
  if 'candidate' in loaded:
   pair=loaded['candidate'];assert pair['actual_initial_root_q30_parameters_recipes_RNG_queues_exact'] is True
   base,own=pair['baseline'],pair['candidate'];validate_result(base,kind,1500,BASE);validate_result(own,kind,1500,OWN)
   assert 'baseline' in loaded and base==loaded['baseline'],'Nested baseline differs from its independently saved own review'
   for key in ('root','q30','physical_parameters','phase'):assert base['initial'][key]==own['initial'][key],(kind,key)
   aq,bq=base['initial']['plane_query'],own['initial']['plane_query']
   for key in ('actual_USD_and_native_actor_metadata','source_reference'):assert aq[key]==bq[key],(kind,key)
   assert aq['loaded_PhysX_binary_fingerprints']['files']==bq['loaded_PhysX_binary_fingerprints']['files']
   own_provenance=actual_case_provenance(reports,f'retention_repair2b_{kind}_1500_v8',own)
   base_provenance=complete_cases[f'baseline_{kind}'];complete_cases[f'candidate_{kind}']=own_provenance
   comparison={'flat':flat_compare,'spin':spin_compare,'world':world_compare}[kind](base,own)
   reset_diff={key:own_provenance['reset_counts'][key]-base_provenance['reset_counts'][key] for key in ('ordinary','truncation','unique','overlap')}
   pairs[kind]=dict(comparison=comparison,ordinary_reset_differences=reset_diff,
                    source_Dll_actor_root_q30_parameters_recipes_RNG_queues_exact=True,
                    baseline_provenance=base_provenance,candidate_provenance=own_provenance,
                    legacy_false_preserved=dict(baseline=base['old_original_flags'],candidate=own['old_original_flags']))
 all_complete=not pending and set(native)==set(pairs)=={'flat','spin','world'}
 if not snapshot_only:assert all_complete,('Actual aggregation remains pending',pending)
 costs=[];seen=set()
 for case in list(native.values())+list(complete_cases.values()):
  if case['case'] in seen:continue
  seen.add(case['case']);costs.append(dict(case=case['case'],seconds=case['actual_parent_unique_zero_PPO_cost_seconds']))
 return dict(all_three_pairs_actual_complete=all_complete,actual_pending=pending,native_admissions=native,
             full_pairs=pairs,actual_complete_full_cases=list(complete_cases),source_reports=files,
             actual_zero_PPO_parent_cost_segments=costs,
             actual_zero_PPO_cost_total_seconds=sum(r['seconds'] for r in costs),no_canonical_budget_operation=True,
             root_decision_on_second_learning_block_required=True,second_block_automatically_approved=False,
             no_mechanical_graduation_score_or_qualification=True,source_reference_only=True,
             actual_shape_local_pose_not_directly_read=True,public_source_to_installed_binary_bitexact_not_proven=True,
             original_V6_failure_unchanged=True)


def main():
 p=argparse.ArgumentParser();p.add_argument('--reports-dir',default=str(D/'reports'));p.add_argument('--output',required=True);p.add_argument('--snapshot-only',action='store_true');a=p.parse_args()
 out=Path(a.output);assert not out.exists();result=aggregate(Path(a.reports_dir),a.snapshot_only)
 report=dict(epoch=time.time(),trial='V8_three_inherited_skill_actual_CPU_aggregation',snapshot_only=a.snapshot_only,
             no_SSH_no_GPU_no_PPO_no_watch_loop=True,result=result,pending_Git_by_root=True)
 out.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(output=str(out),all_complete=result['all_three_pairs_actual_complete'],pending_count=len(result['actual_pending']),
                      complete_pair_kinds=list(result['full_pairs']),second_block_automatically_approved=False),indent=2))

if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'reports'/('AGGREGATE_CPU_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  p.write_text(json.dumps(dict(error=traceback.format_exc(),local_CPU_schema_or_data_only=True,no_SSH_no_GPU_no_PPO=True),indent=2),encoding='utf8');raise
