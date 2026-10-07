"""First repaired2h actual learning and completed matched3060 cases; read only."""
from pathlib import Path
import sys,json,ast,hashlib,time,math
D=Path(__file__).resolve().parent;R=D/'reports';OLD=D.parent/'MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
assert not (R/'BLOCK1_MATCHED_REVIEW.json').exists()
source=OLD/'review_completed_clock2500.py';nodes=[]
for node in ast.parse(source.read_text(encoding='utf8')).body:
 if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef)):nodes.append(node)
 elif isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('D','read'):nodes.append(node)
 elif isinstance(node,ast.Expr) and ast.unparse(node).startswith('sys.path.insert'):nodes.append(node)
ns={'__file__':str(source)};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),ns)
audit=read(R/'REPAIR_BLOCK_BOUNDARY_ACTUAL.json');block=audit['blocks']['episode_repaired_block1_PASSED.json'];h=block['health'];sha=block['checkpoint']['sha256']
assert h['ordinary_episode_reset_events']==2 and h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and not h['stop_reason']
assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==104064 and h['max_closure_error_m']<.002
assert block['actual_updates']==1084 and block['actual_environment_steps']==520320000 and len(block['unique_completed_segment'])==1
segment=block['unique_completed_segment'][0];assert segment['pid']==block['own_PID_bound_receipt']['pid']==960185
assert segment in audit['budget']['completed_segments']
snapshot=read(OLD/'reports/CLOCK2500_EVALUATOR_CURRENT_ACTUAL.json');jobs={j['id']:j for j in snapshot['jobs']}
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
transport=[];c=connect_eval()
try:
 with c.open_sftp() as ftp:
  for kind in ('flat','spin','world'):
   job='clk2500-solver32-60-episode-b1-'+kind;folder=OLD/'reports/windows'/job
   for name in ('probe.json','result.json','manifest.json'):
    raw=folder.joinpath(name).read_bytes();remote=ftp.open('D:/MOD4_async_eval/sensor_clock2500_solver32_v15/jobs/'+job+'/'+name).read()
    assert raw==remote
    transport.append(dict(job=job,file=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),returned_bytes_exact=True))
finally:c.close()
report=dict(epoch=time.time(),scope='3060 matched seed20261002/white_v3/noise_bias/2.5ms-TGS32-4/A0 only',
            block1=block,training_wall_seconds=segment['ended_epoch']-segment['started_epoch'],
            source_sha256=sha,paired_with25211={},candidate26294={},pairing=[],returned_files=transport,
            ordinary_episodes_preserved_not_zeroed=True,strict_world_formula_unchanged=True,
            current_block2_continues_no_GPU_probe_or_budget_operation=True,no_full_DR_or_dualseed_graduation_claim=True)
for kind in ('flat','spin','world'):
 base=read(OLD/'reports/windows'/('clk2500-solver32-20-candidate-'+kind)/'probe.json')
 job='clk2500-solver32-60-episode-b1-'+kind;folder=OLD/'reports/windows'/job
 new,res,m=read(folder/'probe.json'),read(folder/'result.json'),read(folder/'manifest.json')
 assert jobs[job]['complete'] and jobs[job]['probe']==new and jobs[job]['result']==res
 assert res['exit_code']==0 and res['errors']==[] and res['checkpoint']['sha256']==sha and res['steps']==1500
 assert res['runtime_archive_sha256']=='d1aa584bc05a6d09e4adf0dc50e609f2ba7e9deed1e57afa69ea7bb640a54c99'
 bm=read(OLD/'reports/windows'/('clk2500-solver32-20-candidate-'+kind)/'manifest.json')
 pair=dict(kind=kind,root_exact=base['reset_root_before_physics']==new['reset_root_before_physics'],
           q_exact=base['reset_joint_pos_before_physics']==new['reset_joint_pos_before_physics'],
           actual_parameters_exact=ns['params'](base)==ns['params'](new),
           probe_runtime_exact=bm['artifacts']['runtime']==m['artifacts']['runtime'] and (kind=='flat' or base['probe_sha256']==new['probe_sha256']),
           sensor_recipe_exact=base['sensor_recipe']==new['sensor_recipe'],solver_exact=base['clock2500_actual_solver']==new['clock2500_actual_solver'],
           seed_exact=base['seed']==new['seed']==20261002)
 assert all(value for key,value in pair.items() if key!='kind'),pair
 report['pairing'].append(pair);report['paired_with25211'][kind]=ns['facts'](base,kind);report['candidate26294'][kind]=ns['facts'](new,kind)
def summary(role):
 rows=report[role]
 return dict(world=rows['world']['target_count'],max_abs_cross=rows['world']['max_abs_cross'],along=rows['world']['along_range'],
             directions=rows['world']['directions'],straight=[g for g in rows['flat']['constant_speed'] if abs(g['command'])==1.5],
             pure4pi=[{k:v for k,v in g.items() if k!='values'} for g in rows['spin']['pure4pi']],
             closure_mm={kind:rows[kind]['closure_mm'] for kind in ('flat','spin','world')})
report['summary']={role:summary(role) for role in ('paired_with25211','candidate26294')}
res=[jobs['clk2500-solver32-60-episode-b1-'+kind]['result'] for kind in ('flat','spin','world')]
report['cost']=dict(evaluation_process_wall_seconds=sum(x['physics_process_wall_seconds'] for x in res),transfer_seconds=sum(x['transfer_seconds'] for x in res),sampled_peak_MiB=max(x['observed_GPU_memory_mib'] for x in res),continuous_peak_claimed=False)
(R/'BLOCK1_MATCHED_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(summary=report['summary'],cost=report['cost'],health=h,training_wall_seconds=report['training_wall_seconds']),ensure_ascii=False))
