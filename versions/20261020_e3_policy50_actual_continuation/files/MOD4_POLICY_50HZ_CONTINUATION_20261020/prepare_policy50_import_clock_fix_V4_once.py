"""Fix the actual imported duplicate clock, add pre-GPU import resolution, retain all v28 errors."""
from pathlib import Path
import ast,hashlib,importlib.machinery,importlib.util,json,shutil,time
B=Path(__file__).resolve().parent;R=B/'reports';C=B/'controller50V4';old=B/'controller50V3';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 v=json.loads((R/'POLICY50_V3_FIRST_METADATA_REMOTE_ACTUAL.json').read_bytes());assert v['GO'] is None and not v['actual_own_processes'] and v['series_error']
 raw=B/'remote_snapshot_policy50_V3/windows/hour0001/recovery/job0/clock_native50/WORKER_ORIGINAL_ERROR.json';failure=json.loads(raw.read_bytes());assert 'physics_clock.py' in failure['error'] and 'Control or impulse window changed' in failure['error'];assert not C.exists();shutil.copytree(old,C)
 rel='job0/runtime/isaac/mod4/physics_clock.py';source=Path('MOD4_E3_AUTOMATIC_CONTINUATION_20261020/cpu_factory_probe/windows/hour0001/recovery')/rel;dst=C/'overlay'/rel;shutil.copy2(C/'overlay/job0/runtime/physics_clock.py',dst)
 config=json.loads((C/'POLICY50_OVERLAY_CONFIG.json').read_bytes());config['changes'].append(dict(relative=rel,baseline_path=str(source.resolve()),baseline_bytes=source.stat().st_size,baseline_SHA=H(source),candidate_bytes=dst.stat().st_size,candidate_SHA=H(dst)))
 worker=C/'overlay/recovery_worker.py';s=worker.read_text('utf8');needle=" sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4')];";assert needle in s;s=s.replace(needle," assert int(old.get('RM_SPAWN_GRACE_STEPS','10'))==10\n os.environ['RM_SPAWN_GRACE_STEPS']='5' # preserve original 100 ms episode grace at 50 Hz\n"+needle);worker.write_text(s,encoding='utf8')
 for row in config['changes']:row.update(candidate_SHA=H(C/'overlay'/row['relative']),candidate_bytes=(C/'overlay'/row['relative']).stat().st_size)
 (C/'POLICY50_OVERLAY_CONFIG.json').write_text(json.dumps(config,indent=2),encoding='utf8')
 parent=C/'auto_E3_serial_supervisor_v1.py';s=parent.read_text('utf8').replace('MOD4_E3_AUTO50_V3_PENDING_SERIES_20261020.json','MOD4_E3_AUTO50_V4_PENDING_SERIES_20261020.json')
 marker="def CPU_source(node):\n"
 addition="def CPU_source(node):\n clock=node/'job0/runtime/isaac/mod4/physics_clock.py';local={};exec(compile(clock.read_text('utf8'),str(clock),'exec'),local);q=local['validate_clock'](.0025,.02);assert q['decimation']==8 and q['policy_hz']==50.;assert read(node/'job0/runtime/train/deploy/contract_rm2025_later.json')['policy_hz']==50;put(node/'POLICY50_ACTUAL_IMPORT_CLOCK_CPU_ACTUAL.json',dict(epoch=time.time(),actual_import_path=str(clock),clock=q,spawn_grace_seconds=.1,before_any_GPU=True))\n"
 assert marker in s;s=s.replace(marker,addition);parent.write_text(s,encoding='utf8')
 text=(B/'deploy_policy50_namespace_fixed_V3_once.py').read_text('utf8').replace("C=B/'controller50V3'","C=B/'controller50V4'").replace('E3auto50_2010v28/controller','E3auto50_2010v29/controller').replace('MOD4_E3_AUTO50_V3_PENDING_SERIES_20261020.json','MOD4_E3_AUTO50_V4_PENDING_SERIES_20261020.json').replace('POLICY50_V3_','POLICY50_V4_')
 marker="assert (old/'STOP_SERIES_AFTER_CURRENT.json').is_file()"
 extra="failed28=owned/'tasks/E3auto50_2010v28/controller';assert read(failed28/'SERIES_EXIT_ACTUAL.json')['status']=='original_error_no_automatic_retry' and not (failed28.parent/'windows/hour0001/recovery/job0/GO_PRODUCTION.json').exists();assert not any(p.pid!=os.getpid() and any(a.startswith(str(failed28.parent)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\nwith (owned/'state/MOD4_E3_AUTO50_V3_PENDING_SERIES_20261020.json').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\n"+marker
 assert marker in text;text=text.replace(marker,extra);(B/'deploy_policy50_import_fixed_V4_once.py').write_text(text,encoding='utf8')
 for before,after in [('collect_policy50_V3_first_actual_learning_finite_once.py','collect_policy50_V4_first_actual_learning_finite_once.py'),('review_policy50_V3_first_actual_learning_CPU_once.py','review_policy50_V4_first_actual_learning_CPU_once.py')]:
  s=(B/before).read_text('utf8').replace('POLICY50_V3_','POLICY50_V4_').replace('remote_snapshot_policy50_V3','remote_snapshot_policy50_V4');(B/after).write_text(s,encoding='utf8')
 actual=importlib.machinery.PathFinder.find_spec('physics_clock',[str(C/'overlay/job0/runtime/isaac/mod4')]);assert Path(actual.origin).resolve()==dst.resolve();mod=importlib.util.module_from_spec(actual);actual.loader.exec_module(mod);assert mod.validate_clock(.0025,.02)['decimation']==8
 assert all(ast.parse(p.read_text('utf8')) for p in C.rglob('*.py'));assert 5*.02==10*.01
 put('POLICY50_V4_SOURCE_PREPARED_CPU_ACTUAL.json',dict(epoch=time.time(),passed_source_CPU=True,controller_files={p.name:H(p) for p in C.iterdir() if p.is_file()},actual_imported_clock_path=str(dst.resolve()),both_clock_copies_explicitly_50Hz=True,original_100ms_spawn_grace_preserved=True,old_v28_full_original_error_retained=str(raw),old_v28_no_GO_no_PPO=True,pre_GPU_actual_clock_import_gate=True,new_unused_root='E3auto50_2010v29',not_actual_GPU_admitted=True))
 print(json.dumps(dict(prepared=True,actual_import_clock_hz=50,spawn_grace_ms=100,new_root='E3auto50_2010v29')))
if __name__=='__main__':main()
