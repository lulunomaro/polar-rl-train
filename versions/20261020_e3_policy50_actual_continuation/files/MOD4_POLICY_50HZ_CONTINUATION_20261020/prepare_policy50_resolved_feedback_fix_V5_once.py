"""Fix actual feedback callback to use resolved manager term configs; retain v29 native prefix/error."""
from pathlib import Path
import ast,hashlib,json,shutil,time
from types import SimpleNamespace
B=Path(__file__).resolve().parent;R=B/'reports';C=B/'controller50V5';old=B/'controller50V4';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 v=json.loads((R/'POLICY50_V4_FIRST_METADATA_REMOTE_ACTUAL.json').read_bytes());assert v['GO'] is None
 error=B/'remote_snapshot_policy50_V4/windows/hour0001/recovery/job0/clock_native50/WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json';e=json.loads(error.read_bytes());assert 'value.shape==(self.n,CHANNELS[key][0])' in e['error'];assert not C.exists();shutil.copytree(old,C)
 path=C/'overlay/job0/runtime/isaac/mod4/feedback_delay_runtime.py';s=path.read_text('utf8');before="                    term = getattr(self.cfg.observations.policy, name)\n                    term.func(self, **term.params)";after="                    names = self.observation_manager.active_terms['policy']\n                    term = self.observation_manager._group_obs_term_cfgs['policy'][names.index(name)]\n                    term.func(self, **term.params)";assert before in s;s=s.replace(before,after);path.write_text(s,encoding='utf8')
 config=json.loads((C/'POLICY50_OVERLAY_CONFIG.json').read_bytes())
 for row in config['changes']:row.update(candidate_SHA=H(C/'overlay'/row['relative']),candidate_bytes=(C/'overlay'/row['relative']).stat().st_size)
 (C/'POLICY50_OVERLAY_CONFIG.json').write_text(json.dumps(config,indent=2),encoding='utf8')
 parent=C/'auto_E3_serial_supervisor_v1.py';s=parent.read_text('utf8').replace('MOD4_E3_AUTO50_V4_PENDING_SERIES_20261020.json','MOD4_E3_AUTO50_V5_PENDING_SERIES_20261020.json');parent.write_text(s,encoding='utf8')
 text=(B/'deploy_policy50_import_fixed_V4_once.py').read_text('utf8').replace("C=B/'controller50V4'","C=B/'controller50V5'").replace('E3auto50_2010v29/controller','E3auto50_2010v30/controller').replace('MOD4_E3_AUTO50_V4_PENDING_SERIES_20261020.json','MOD4_E3_AUTO50_V5_PENDING_SERIES_20261020.json').replace('POLICY50_V4_','POLICY50_V5_')
 marker="assert (old/'STOP_SERIES_AFTER_CURRENT.json').is_file()"
 extra="failed29=owned/'tasks/E3auto50_2010v29/controller'\nwhile not (failed29/'SERIES_EXIT_ACTUAL.json').is_file():\n assert time.monotonic()<until;time.sleep(3)\nassert read(failed29/'SERIES_EXIT_ACTUAL.json')['status']=='original_error_no_automatic_retry' and not (failed29.parent/'windows/hour0001/recovery/job0/GO_PRODUCTION.json').exists();assert not any(p.pid!=os.getpid() and any(a.startswith(str(failed29.parent)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\nwith (owned/'state/MOD4_E3_AUTO50_V4_PENDING_SERIES_20261020.json').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\n"+marker
 assert marker in text;text=text.replace(marker,extra);(B/'deploy_policy50_resolved_feedback_V5_once.py').write_text(text,encoding='utf8')
 for before,after in [('collect_policy50_V4_first_actual_learning_finite_once.py','collect_policy50_V5_first_actual_learning_finite_once.py'),('review_policy50_V4_first_actual_learning_CPU_once.py','review_policy50_V5_first_actual_learning_CPU_once.py')]:
  s=(B/before).read_text('utf8').replace('POLICY50_V4_','POLICY50_V5_').replace('remote_snapshot_policy50_V4','remote_snapshot_policy50_V5');(B/after).write_text(s,encoding='utf8')
 # Reproduce the actual defect: raw config contains 30 unresolved joints,
 # resolved manager config contains exactly each actor channel width.
 tree=ast.parse(path.read_text('utf8'));cl=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='DelaySensorMod4Env');fn=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name=='_install_feedback_100hz_sampling');widths={'base_ang_vel':3,'projected_gravity':3,'leg_pos':4,'leg_vel':4,'wheel_vel':2};scope={'WIDTHS':widths};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual resolved feedback callback>','exec'),scope);calls=[]
 names=list(widths);resolved=[SimpleNamespace(func=lambda env,key=k,width=n:calls.append((key,width,env._feedback_100hz_tick)),params={}) for k,n in widths.items()];raw=SimpleNamespace(**{k:SimpleNamespace(func=lambda env:(_ for _ in ()).throw(AssertionError('Unresolved 30-joint config used')),params={}) for k in names})
 env=SimpleNamespace(physics_dt=.0025,step_dt=.02,scene=SimpleNamespace(update=lambda dt:None),cfg=SimpleNamespace(observations=SimpleNamespace(policy=raw)),observation_manager=SimpleNamespace(active_terms={'policy':names},_group_obs_term_cfgs={'policy':resolved}),_sim_step_counter=0)
 scope['_install_feedback_100hz_sampling'](env)
 for tick in range(1,17):env._sim_step_counter=tick;env.scene.update(.0025)
 assert len(calls)==20 and all(width==widths[key] for key,width,tick in calls) and {tick for _,_,tick in calls}=={1,2,3,4}
 assert all(ast.parse(p.read_text('utf8')) for p in C.rglob('*.py'))
 put('POLICY50_V5_SOURCE_PREPARED_CPU_ACTUAL.json',dict(epoch=time.time(),passed_source_CPU=True,controller_files={p.name:H(p) for p in C.iterdir() if p.is_file()},actual_unresolved_vs_resolved_cfg_regression_passed=True,raw_cfg_deliberately_rejected=True,feedback_channel_widths=widths,sampling_100Hz_inside_policy50Hz=True,old_v29_full_error_and_zero_optimizer_prefix_retained=str(error),old_v29_no_GO_no_PPO=True,new_unused_root='E3auto50_2010v30',not_target_GPU_admitted=True))
 print(json.dumps(dict(prepared=True,resolved_feedback_regression=True,new_root='E3auto50_2010v30')))
if __name__=='__main__':main()
