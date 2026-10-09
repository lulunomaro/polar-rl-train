"""Record the new actual paired admission and parallel retention publication once."""
from pathlib import Path
import json,hashlib,time,sys,subprocess,shutil
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=R/'D7_MATCHED_D9_RETENTION_GIT_RECORDED.json';assert not receipt.exists()
v=read(R/'D7_BLOCK1_D9_SOURCE_SELECTED.json');p=read(R/'PUBLISHED.json');a=read(R/'D9_RETENTION_CURRENT_ACTUAL.json');s=read(R/'NEXT_S3_E1_SHALLOW_TERRAIN_WORK_ORDER.json')
assert v['master_SHA_unchanged']==sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==s['master_SHA_unchanged']
assert p['source']==v['source'] and a['published']==p and a['completed_conditions']==3 and a['pending_conditions']==15
assert a['worker_receipts']['SDK_PREPARATION_ISOLATION_WORKER_ATTENTION.json'] is None
assert any(x['ProcessId']==31896 and x['creation_epoch']==1791502470.165 and x['CommandLine'].endswith('eval_worker_sdk_preparation_isolation.py') for x in a['actual_processes'])
assert any('101-d9-retention-' in x['CommandLine'] for x in a['actual_processes'])
note=f'''# D7 complete paired31903 admitted for D9 development retention

D7 first stable block model31903 SHA {v['source']['source']['sha256']} is independently verified from its own PID1516991 receipt, fullCPU94 checkpoint,277-source freeze,44 snapshots and one completed canonical segment. It has488 PPO updates,11712 control ticks,234240000 environment policy steps and46848 actual callbacks. Elapsed{v['unique_elapsed_seconds']:.9f}s includes load/save/exit and was already settled once by its original parent; this review performs no settlement. Healthv3 preserves seven ordinary single-environment resets (six orientation,one closure), peak2.086289926mm and legacy_single_peak_2mm_pass=false. Integrity/unknown/mimic/nonfinite/STOP are absent; reset zero is not labelled natural recovery.

Three same3060/seed20261002/white_v3/D0-D7/flat80-spin88-world88/1500control15s cases are actually complete. Full initial root/30q, parameters, all sensor-feedback-action-spring-gas-COM/PD recipes and assignments, actual feedback ages, per-actiongroup6000 callbacks, target error zero, original model/task/data checks and returned JSON byteSHA are verified against anchor31416 in the same immutable8a964c1d package. Straight negative/positive error improves0.030663744/0.056608647 to0.022649303/0.039943967m/s. Whole signed world circles remain64/64, maximum absolute netcross0.040780827 to0.037223728m/s, along0.476243373–0.534592671m/s. Pure left/right4pi each8/8; means12.529360/-12.452513rad/s within the original signed tolerance. Original finite-quality/legacy flags and raw remain. This is firstseed-white3 development evidence, not heldout/allDR or hardware certification.

An explicit SELECTED_D7_BEHAVIOR_SOURCE.json now admits this complete balanced source to the already-running CPU-only D9 publisher. The publisher copied its exactSHA, reused these exact three firstseed-white3 cases and published only15 new conditions, total18 development conditions: seeds20261002/3 x D0nominal/white_v2/white_v3 x flat/spin/world; D1-D7 stay on. Nominal uses the previously actual-SDK-reviewed D0 lifecycle package654014eb, whites use originalD7 package8a964c1d. The CPU publisher naturally completed and exited with no current attention. Actual unchanged worker31896/creation1791502470.165 and its real new nominal-flat GPU child prove evaluation has started. At this snapshot three reused cases are complete and15 new cases pending; publication/start does not prove their behavior passed. No D9 learning executor, duplicate nine-group course or repeated45min clock/PPO preflight.

Main4090 D7 block2 remains its own actual trainer1558067/start67258143 using31903, with original source277 and no performance candidate installed. Main source is not hot-swapped. The separately completed3060 performance study70298cc9 remains a bounded frozen benchmark with only~0.376% measured collection gain, not a20k4090 PPO improvement; this stage does not rerun/archive it. No training launch, live source mutation or canonical/budget transaction by this review/publication.

S3/E1 preparation now reads actual nine earlier terrain/reset/recipe/raycast/collision-bank files and checks existing local source bytes. The old RoughIntroEnv extends Mod4Env and lacks the new D1-D7 chain, so it cannot be executed as the new expert. New work order requires an isolated ChassisPDMod4Env terrain adapter, complete selected-row DR/RNG/reset preservation, actual same-tick ground and reward/termination, complete30q footprint reset and unchanged contact integration/hardware. First geometry remains1–2cm bars,0–1cm roughness,gentle slopes and independent40x40 mesh, yaw0/stand or±0.3m/s; E1 controller/SDK/PPO is not yet deployed. New geometry scope requires its own targeted SDK/native/fullPPO once, with valid clock/DR contracts reused.

S3/S7 explicitly reference MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001. Future spin surfaces exclude dog-tunnel interior and all stair treads/edges/top decks; actual surface/clearance regions are required. The future stair route includes actual part383/BREP424 entry chamfer49.5617556mm rise/run/local45deg before the gentler slope, both-wheel crossing/down/reverse/oblique/stop-start,yaw0; it is not installed as current shallow geometry. Separate~100mm edges do not silently enter the5cm course. No privileged terrain input, changed master SHA, dangerous S8 reset, force-stroke certification or trained MoE gate.

Actual remaining snapshot{v['tail_adjusted_remaining_seconds_snapshot']:.3f}s; repair reserve min(18h,.13B)={s['budget_snapshot']['repair_reserve_seconds']/3600:.3f}h is planning only, not a canonical transaction. Keep expert/gate time available and review completed18 cases and D7 final before the safe unique E1 entry. MainD7 health-v3/fullsave/local15s guardian/save25/<=2h blocks and230h canonical/six old extensions/new0 remain.
'''
(R/'D7_MATCHED_D9_RETENTION_REPORT.md').write_text(note,encoding='utf8')
folder=REPO/'history/evidence/MOD4_D7_MATCHED_D9_RETENTION_20261009';assert not folder.exists();folder.mkdir(parents=True);files=[]
def cp(path,name):
 out=folder/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,out);assert sha(out)==sha(path);files.append(out.relative_to(REPO).as_posix())
for name in ('select_reviewed_d7_block1_once.py','read_retention_actual.py','prepare_e1_ground_work_order_once.py','record_selected_d7_retention_once.py'):
 cp(D/name,'implementation/'+name)
for name in ('D7_BLOCK1_D9_SOURCE_SELECTED.json','SELECTED_D7_BEHAVIOR_SOURCE.json','PUBLISHED.json','D9_RETENTION_CURRENT_ACTUAL.json','NEXT_S3_E1_SHALLOW_TERRAIN_WORK_ORDER.json','D7_MATCHED_D9_RETENTION_REPORT.md'):
 cp(R/name,'reports/'+name)
cp(R/'D7_MATCHED_D9_RETENTION_REPORT.md','EXPERIMENT_NOTE.md')
raw_index=dict(epoch=time.time(),weights_USD_NPZ_large_raw_only_SHA=True,source_checkpoint=v['source']['source'],matched_cases=v['source']['paired_cases'],large_reports_sha256=v['large_evidence_sha256'],terrain_files=[{k:x for k,x in row.items() if k!='text'} for row in s['source_audit']['files']],packages={x['artifacts']['runtime']['sha256']:x['artifacts']['runtime'] for x in p['fifteen_new_cases']})
(R/'D7_D9_RAW_SHA_INDEX.json').write_text(json.dumps(raw_index,indent=2),encoding='utf8');cp(R/'D7_D9_RAW_SHA_INDEX.json','reports/D7_D9_RAW_SHA_INDEX.json')
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','d7-model31903-matched-d9-retention-admitted-and-e1-ground-prepared','--title','D7 model31903 matched retention admitted to parallel D9 and E1 ground scope prepared','--kind','evaluation','--note-file',str(folder/'EXPERIMENT_NOTE.md'),'--files',*files,'--validation','Own completeCPU94 source277 snapshot44 PID1516991 and one previously settled segment;3sameplatform trueCOM-PD15s paired cases complete64world/16pure signed directions improvedstraightcross; returnedJSONbyteSHA; existing CPU publisher naturalexit exactsource15new+3reused=18dev; actual unchanged3060worker and GPUchild; E1 actual9source audit workorder only; RMannotations/masterSHA preserved; no4090source/GPU/PPO/canonical transactions; no repeated45min orPPO; oldrawflags retained','--push']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if r.returncode:
 (R/'D7_D9_GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,do_not_repeat_record=True),indent=2),encoding='utf8');raise RuntimeError(r.stdout+'\n'+r.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=r.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
g=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,master_SHA_unchanged=v['master_SHA_unchanged'],new_budget_seconds=0,weights_large_raw_USD_NPZ_only_SHA=True)
receipt.write_text(json.dumps(g,indent=2),encoding='utf8');print(json.dumps(g))
