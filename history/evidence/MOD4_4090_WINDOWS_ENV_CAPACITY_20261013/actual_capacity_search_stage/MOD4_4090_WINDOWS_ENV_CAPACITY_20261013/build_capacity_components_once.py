"""Fresh capacity benchmark source, preserve current learning; no local GPU."""
from pathlib import Path
import ast,json,zipfile,hashlib,time
D=Path(__file__).resolve().parent;W=D.parent
BASE=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013/REMOTE_ACTUAL_EVIDENCE_1791891813944594400/temporary_scope128_memory20GB_logger_ready_v12_20261013/payload'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=D/'template_v1';assert not out.exists();out.mkdir()
 for p in BASE.iterdir():
  if p.is_file():(out/p.name).write_bytes(p.read_bytes())
 for n in ('expanded_source_projection.py','PERENV128_SCHEMA_V1.json'):(out/n).write_bytes((D/'CPU_projection'/n).read_bytes())
 (out/'temporary_state_binding.py').write_bytes((D/'capacity_state_binding.py').read_bytes())
 p=out/'temporary_training_runtime.py';s=p.read_text(encoding='utf8')
 s=s.replace("max_formal_updates == 256","max_formal_updates in (4, 256)")
 anchor="saved['WINDOWS4090_TEMPORARY_BRANCH'] = copy.deepcopy(source['WINDOWS4090_TEMPORARY_BRANCH'])";assert s.count(anchor)==1
 s=s.replace(anchor,anchor+"\n        if 'WINDOWS4090_EXPANDED_ENV_BRANCH' in source:\n            saved['WINDOWS4090_EXPANDED_ENV_BRANCH']=copy.deepcopy(source['WINDOWS4090_EXPANDED_ENV_BRANCH'])\n            saved['WINDOWS4090_EXPANDED_ENV_BRANCH'].update(all12_own_CPUCUDA_restore_disk_roundtrip_and_API_offsets_pending=False,actual_current_GPU_restore_verified=True)\n        saved['WINDOWS4090_CAPACITY_ATTEMPT']=dict(num_envs=env.num_envs,benchmark_only=json.loads(Path(args.manifest).read_bytes()).get('capacity_benchmark_only',False),original_parent128_final_SHA='f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3')")
 anchor='    oldupdate = runner.alg.update';assert s.count(anchor)==1
 s=s.replace(anchor,"""    performance=[]
    oldlog=runner.logger.log
    def measured_log(*a,**kw):
        result=oldlog(*a,**kw)
        row=dict(update=updates,collection_seconds=kw['collect_time'],learning_including_save_health_seconds=kw['learn_time'],num_envs=env.num_envs,steps=24*env.num_envs)
        row['envsteps_per_second']=row['steps']/(row['collection_seconds']+row['learning_including_save_health_seconds'])
        performance.append(row)
        write('CAPACITY_ACTUAL_PPO_TIMING.json',dict(epoch=time.time(),pid=os.getpid(),rows=performance,original_runner_loop_times_not_estimated=True,full5epochs4minibatches=True,benchmark_only=json.loads(Path(args.manifest).read_bytes()).get('capacity_benchmark_only',False)))
        return result
    runner.logger.log=measured_log
"""+anchor)
 p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
 p=out/'temporary_parent.py';s=p.read_text(encoding='utf8').replace("('fullrestore', 'train')","('native', 'fullrestore', 'train')")
 s=s.replace("'no_budget_write_extension_refund_or_duplicate_charge':", "'no_budget_write_extension_refund_or_duplicate_charge':")
 p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
 # Purely read the actual filter request, view dimensions and child namespace.
 p=out/'temporary_probe_contract_base.py';s=p.read_text(encoding='utf8');anchor='    parameters = parameter_audit(env)';assert s.count(anchor)==1
 s=s.replace(anchor,"""    assert env.cfg.scene.replicate_physics and env.cfg.scene.filter_collisions and 'cuda' in str(env.device)
    paths=list(env.scene._env_prim_paths)
    assert len(paths)==env.num_envs and len(set(paths))==env.num_envs
    assert int(r.root_view.count)==env.num_envs
    write('CAPACITY_COLLISION_FILTER_REQUEST_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),num_envs=env.num_envs,unique_env_prim_paths=paths,replicate_physics=True,GPU_enable_env_ids_request=True,articulation_view_count=int(r.root_view.count),duplicate_parent_worldXY_disclosed=True,not_independent_interaction_causal_ablation=True))
"""+anchor)
 p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
 for p in out.glob('*.py'):compile(p.read_text(encoding='utf8'),str(p),'exec')
 z=D/'CAPACITY_COMPONENTS_TEMPLATE_V1.zip';assert not z.exists()
 with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED) as zip:
  for p in sorted(out.iterdir()):
   if p.is_file():zip.write(p,p.name)
 proof=dict(epoch=time.time(),template_source_only=True,source_files=[dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(out.iterdir()) if p.is_file()],package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),no_GPU_or_launch=True,old128_source_unchanged=True,actor_hidden128_dimensions_must_not_resize=True,benchmark_discard_weights_not_production_source=True)
 (D/'reports/CAPACITY_TEMPLATE_V1_PREPARED_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof['package']))
if __name__=='__main__':main()
