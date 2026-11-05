"""Archive this genuinely new task intervention and actual native full-learner resume.
Consumed after record; synchronization failures continue existing objects only.
"""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_n20000_timeout8_native_fullresume_20261104');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:
  print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','21763dd0c4ca97cb009913c1075caa6ca09160e6','HEAD')
e=json.loads((D/'FDN_N20000_W6_TIMEOUT8_FIRST_REAL_TRAINING_EVIDENCE.json').read_bytes());r=e['source_receipt'];w=e['window_counters'];base=e['base_counters'];cum=e['cumulative_counters'];n=e['native_counters']
assert e['kind']=='ACTUAL_N20000_FULL_LEARNER_RESUME_TIMEOUT8_FIRST_POSITIVE_POINT_NOT_SKILL_PASS'and e['skill_improvement_claim']is False
assert base==dict(updates=133,policy_optimizer_steps=2660,encoder_optimizer_steps=2660,transitions_seen=78822912)
assert w['updates']>0 and w['policy_optimizer_steps']==w['encoder_optimizer_steps']==20*w['updates']and w['transitions_seen']==960000*w['updates']and all(cum[k]==base[k]+w[k]for k in base)
assert r['source_sha256']=='8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78'and r['source_bytes']==1204250903 and r['complete_learner_loaded']is True
assert all(r[k]==1 for k in('physical_byte_opens','SHA_calculations','CPU_decodes','learner_source_reads'))and r['original_mother_reads']==r['ancestor_N4096_reads']==0
assert n['actual_native_policy_steps']==48*w['updates']and n['actual_native_transitions']==20000*n['actual_native_policy_steps']and n['physical_callbacks']==8*n['actual_native_policy_steps']and n['feedback_callbacks']==2*n['actual_native_policy_steps']
assert e['actual_original_global_episode_length_s']==20 and e['lowrise_timeout8']['policy_steps']==400 and e['lowrise_timeout8']['time_out']is True
pointer=json.loads((D/'FDN_N20000_W6_TIMEOUT8_FIRST_ADMISSION_PATH.json').read_bytes());ad=json.loads(Path(pointer['path']).read_bytes())
assert ad['root']==e['root']and ad['actual_root_admission']['actual_original_authority_EX_private_GPU_EX_finite_SH']is True and ad['actual_parent_identity']['pid']==1621824
required=('stage_fudan_timeout8_frozen_original_once.py','dispatch_fudan_timeout8_frozen_original_once.py','collect_fudan_timeout8_frozen_original_once.py','export_fudan_timeout8_pi_for_mujoco_once.py','evaluate_fudan_timeout8_pi_mujoco31_lowrise_once.py')
assert all((D/name).is_file()for name in required)
note=(D/'CURRENT_PROGRESS_V12_TIMEOUT8_NATIVE_RESUME_AND_EVAL_READY.md').read_text(encoding='utf8')
dest.mkdir(parents=True);files=[];rows=[]
NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle','.npz','.npy','.png','.jpg','.jpeg','.webp','.usd','.usda','.usdc','.zip','.mp4','.xml','.stl','.obj','.ply','.dae','.mesh','.pyc','.pyo','.tmp','.partial'}
for p in sorted(D.rglob('*')):
 if '__pycache__'in p.parts:continue
 row=dict(source_path=str(p))
 if p.suffix.lower()in NO or p.name=='RESULT.json':
  row['status']='weight_geometry_image_video_raw_or_transient_reference_only_skipped_before_stat_read_hash';rows.append(row);continue
 if not p.is_file():continue
 raw=p.read_bytes();target=dest/'files'/p.relative_to(D);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);rp=target.relative_to(repo).as_posix();files.append(rp)
 row.update(status='complete_text_point_in_time',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),archive_path=rp);rows.append(row)
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,all_current_text_reports_snapshot=True,models_raw_images_video_geometry_not_opened_for_Git=True,physical_or_once_replay_for_Git=False,main_push_or_reset=False),indent=2),encoding='utf8')
(dest/'.gitattributes').write_text('* -text\n',encoding='utf8')
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual new W6 N20000 full learner continuation from complete 8af4 source, model/critic/STD/LR/both Adam/private generator restored, sole physical read/hash/CPU decode once. Current source ancestor reads zero. Five positive native PPO updates and actual 20-second global episode configuration with separate low-only 400-control time_out are frozen evidence, not final-window or skill acceptance. No production promotion: Registryv12/1cd, H1 and other experts unchanged. New ten-source original N80 evaluator and CPU pi-only/MuJoCo follow-ups are source-ready but unexecuted. Preserve all text source/failure/report history. Later final save/actual waits/account/release and original quality assessment remain pending. Original physics/fullDR/PPO/resources/budget/closure semantics unchanged. This record is consumed; never replay for synchronization.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
trial_id='e3-fudan-n20000-timeout8-real-fullresume-native'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 N20000 true full learner resume and low-only timeout8 native updates; original eval sources ready','--kind','training','--note-file',str(dest/'NOTE.md'),'--validation','actual-native-N20000-T48-positive-window-deltas;source8af4-complete-model-critic-STD-LR-twoAdam-privateGenerator;source-read-hash-decode1-current-ancestor-reads0;base133-and-64plus69-lineage-not133times20k;fresh-environment-DR-history-stream-cut;actual-global20s-plus-low-only400-control-time_out;no-reward-PPO-physics-DR-resource-budget-change;frozen-original-N80-74plus6-and-MuJoCo-followup-sources-not-executed;first5-point-not-skill-or-window-closed;keep-Registryv12-1cd-H1-others;all-current-text-reports-feature-only-main-readonly','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,main_push_or_reset=False,physical_or_once_replay_for_Git=False,source_entries=len(rows)),indent=2))
