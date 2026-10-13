from pathlib import Path
import json,time,shutil,zipfile,hashlib
D=Path(__file__).resolve().parent;q=D/'template_v4_capacity_guard';assert not q.exists();shutil.copytree(D/'template_v3_intermediate',q)
p=q/'temporary_worker.py';s=p.read_text(encoding='utf8');needle='        birth = birth_inputs(env, O, write, source, placement)';assert s.count(needle)==1
guard="""        def native_capacity_fault_check():
            log=O.parent/'worker_stdout.log'
            if log.exists():
                with log.open('rb') as f:
                    f.seek(max(0,log.stat().st_size-1048576));tail=f.read()
                if b'buffer overflow detected' in tail or b'Contacts have been dropped' in tail or b'PhysX scene is corrupted' in tail:
                    write('NATIVE_CAPACITY_FAILURE_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),passed=False,no_PPO=True,source_checkpoint_preserved=True,reason='PhysX allocation overflow/corrupted scene in actual own stdout; refuse physical pass and stop own worker naturally via exception'))
                    raise RuntimeError('Actual own PhysX capacity failure; contacts cannot be trusted')
        native_capacity_fault_check()
"""
s=s.replace(needle,guard+needle)
needle='            rows.append(command)';assert s.count(needle)==1;s=s.replace(needle,'            native_capacity_fault_check()\n'+needle)
compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
z=D/'CAPACITY_COMPONENTS_TEMPLATE_V4_GUARDED.zip';assert not z.exists()
with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED) as f:
 for p in sorted(q.iterdir()):
  if p.is_file():f.write(p,p.name)
s=(D/'deploy_capacity_intermediate_v3_once.py').read_text(encoding='utf8').replace('benchmark_v3_20261013','benchmark_v4_20261013').replace('CAPACITY_COMPONENTS_TEMPLATE_V3_INTERMEDIATE.zip','CAPACITY_COMPONENTS_TEMPLATE_V4_GUARDED.zip')
needle="mf['temporary_small_batch_capacities']['gpu_found_lost_aggregate_pairs_capacity']=8388608 if N<=512 else 16777216;";assert needle in s
s=s.replace(needle,needle+"mf['temporary_small_batch_capacities']['gpu_collision_stack_size']=268435456;")
p=D/'deploy_capacity_intermediate_guarded_v4_once.py';assert not p.exists();compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
(D/'reports/CAPACITY_OVERFLOW_GUARD_V4_PREPARED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),new_template=str(z),bytes=z.stat().st_size,sha256=hashlib.sha256(z.read_bytes()).hexdigest(),new_native_own_error_observer=True,own1024_observed_stack_need162398352_bytes=True,new_intermediate_stack_allocation268435456_bytes=True,physical_solver_and_thresholds_unchanged=True,oldscope_no_hotpatch=True,GPU_or_PPO_future_pass=False),indent=2),encoding='utf8')
