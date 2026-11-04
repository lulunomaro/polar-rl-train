"""One new completed-quality stage; after record/push failure continue existing objects only."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_n20000_closed69_quality_20261104');dest=repo/rel

def G(*a):
    p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
    if p.returncode:
        print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
    return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','4fc5baf6c8a1df672bbb3d281475d6b370d70a4b','HEAD')
r=json.loads((D/'FDN_N20000_CLOSED69_QUALITY_DECISION_V1.json').read_bytes())
assert r['training']['new_N20000']['updates']==69 and r['training']['cumulative']['updates']==133
assert r['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_8AF4_PROMOTION'and r['goal_complete']is False
assert r['original_N80']['execution_qualified']is True and r['original_N80']['recovery_first_episode_credits']==0 and r['original_N80']['original_request_denominator']==74
assert all(v['complete_finite_cases']==5 and v['engineering_credits']==0 for v in r['nominal_MuJoCo31']['comparison'].values())
assert all(r['training']['original_owner_exit'][k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
assert r['training']['outer_wait']['original_owner_reaped']is True
note=(D/'CURRENT_PROGRESS_V11_N20000_CLOSED69_QUALITY_NOT_IMPROVED.md').read_text(encoding='utf8')+'\n\n'+(D/'NEXT_SINGLE_INTERVENTION_LOWTIMEOUT8_PLAN_V1.md').read_text(encoding='utf8')
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
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual N20000 window ended with 69 new PPO updates, 1380 steps for each Adam, 66240000 optimized transitions, and a fully saved 48-control unoptimized pending rollout. Complete candidate 8af4 is preserved; source4096, full N20000 continuation, and derived pi-only deployment are separate artifacts and purposes. Qualified original N80 reports 0/74 first-episode recovery credits and 0/6 normal physical terminations. Ten actual nominal MuJoCo runs remain separate from native/fullDR acceptance; both engineering scores are 0/5 but the mother raises its body while the candidate stays low and drifts. Keep Registryv12/1cd and H1; no candidate promotion. Preserve the pre-connect materializer indentation failure and new-source correction. Next low-only timeout8 intervention is a source-level hypothesis, not a proven cause or already-run training. Original physics, DR, resources, canonical accounting and actual closure remain unchanged. This script is consumed after record; never repeat record/tag/physical tasks for sync.\n',encoding='utf8')
files.extend((rel/n).as_posix()for n in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
trial_id='e3-fudan-n20000-closed69-quality-keep-mother'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 N20000 full learner closed69; qualified original and nominal quality results; keep frozen mother','--kind','evaluation','--note-file',str(dest/'NOTE.md'),'--validation','actual-N20000-T48-69PPO-bothAdam1380;64-N4096-base-separate;optimized66240000-and-48-control-pending-not70;complete-save-actual-inner-outer-waits-cost-leases;qualified-original-N80-74plus6-firstepisode-no-resetstitch;actual-MuJoCo31-five-poses-8s-both-means-no-fullDR-claim;keep-1cd-no-8af4-promotion;pi-only-not-resume;input-model-no-status-Git-opens;materializer-preconnect-source-failure-preserved;next-timeout8-source-hypothesis-only;H1-and-other-experts-fixed;all-text-failures-reports-feature-only-main-readonly','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(x.split()for x in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,main_push_or_reset=False,physical_or_once_replay_for_Git=False,source_entries=len(rows)),indent=2))
