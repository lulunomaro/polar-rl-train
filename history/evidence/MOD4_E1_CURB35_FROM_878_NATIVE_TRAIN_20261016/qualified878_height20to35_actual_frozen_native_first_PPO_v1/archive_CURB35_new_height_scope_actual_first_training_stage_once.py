"""Exactly one real CURB35 annotated stage; later results append ordinarily."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,importlib,importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';BASE='50df871e97105c7a28381be7a3db716e42a4857e';ID='e1-curb35-qualified878-height-native-first-training'
DEST=REPO/'history/evidence'/D.name/'qualified878_height20to35_actual_frozen_native_first_PPO_v1'
s=importlib.util.spec_from_file_location('existing_pure_git_helpers',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list','*'+ID) and not DEST.exists()
 first=json.loads((R/'FIRST_CURB35_REAL_PRODUCTION_SAVE_COMPLETE_LOCAL_CPU_VERIFIED.json').read_bytes());assert first['passed']
 frozen=json.loads((D/'frozen35_3060_v1/reports/CURB35_SOURCE878_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json').read_bytes());assert frozen['passed']
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1352
 idx=REPO/'history/evidence/MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/CURB113_frozen_WAVE52_final_step_hop_review_no_auto_old_PPO_ordinary_v3/REPORT_CAPTURE_INDEX.json';prior=json.loads(idx.read_bytes())['entries'];bysha={x['sha256']:x for x in prior if x.get('Git_path')}
 note=D/'CURB35_ACTUAL_NEW_HEIGHT_FIRST_LEARNING_STAGE_NOTE.txt'
 text='''Human explicitly requested to start training and continue the approved master plan. This is a NEW E1-G2 height35 scope under original master812a4b and RM003, not renewal of oldCURB20/WAVE/SLOPE blocks and not S8 airborne/jump/70/second-gate/new budget. Real center-island outer curb150mm width and finite local inner44/92–94mm versus outer150/200mm samples were explained; this35mm lesson is derived basic geometry, not realRM completion.

The protected qualified CURB878 full181tensor102float source268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1,17Adam660400, was selected after its original20mm full frozen up27/27 anddown27/27. Newindependent113 at20mm up26/27 remains separate and not selected by largeriteration. CPU new35mm mesh preserves10vertices/8triangles,150mmstrip,2verticalfaces,mirrorwinding,XY/resetentry/commands/reward/DR/physics/hardware. Entry AST inverse is exact for declared configure/checkpoint imports. New source20→35 fullstate migration explicitly restores original model/STD/critic/17Adam, all original typed/globalnamed/private CUDA loaders and sourceepisode+1; geometry equality is NOT fabricated.

3060 new unused source878-on35 native120/480callbacks andfull80x1500/15s6000callbacks actually completed/wholetwohostSHA/allphysical-query-contactintegralCOMhardware/source9STD initialfinal/all savedCPUmean/normal35/previousactualclipped6/selectedreset/EXIT0-allparentschildrenlauncherout/sharedmsvcrtfree audited. Query2.384185791015625e-7,CPUvsGPUmean6.866455078125e-5 nonbitexact. New35 originalstrictbefore-after200mm actual ascent8/27 descent27/27,ordinary1,trunc29,raw88be197498bf7fe08f87d1e09e8d0c60843830b2e0947419d625f2b3929a1896. This revealed a concrete ascent gap, not allskills or a new promotion threshold. OriginalmissingEXIT_NATURAL remains missing beside data+EXIT0+cleared closure. Old20 andnew35 evaluations are neverreplayed. Full35 physical loop inverseAST differs only declared geometryimport/height and source20-vs-new35 witness; source20 savedmesh is correctly not called newgeometryfullrestore. Sourcebasename preexecution replacement rejection and independentV2 reader remain preserved.

One newsource210 detachedowner477807/create1792121677.83 holds originaltwofcntl and solecanonical. Fresh activeNone/remaining609223.0147352219/23881MiBfree were read-only snapshots, lateractual precedence. Whole435payloadfiles targetSHA and source17Adam660400 CPU actual checked. Finite chain discarded128x2PPO→own20k strictfullrestore/native24warmup+120timed576callbacks/independentCPU→discarded20kx4PPO→completequalifiedsource restore again→production. Preflightweights not production and model/Adam/DR exposure restored before actualproduction. Alloptimizerprechecks/loadlearnsaveexit charge actual original intervals once; CPU/native0PPO gaps not charged. Original authorized1188000/sevenextensions unchanged. Combined firstnewscope cap2700seconds, exitheadroom240seconds (prepared minimum180 exceeded), no automatic nextblock; actual futureexit/bound not assumed. Exact actual accounting function AST in-memory fixture charges10+24=34, nativegap290 uncharged, duplicate/foreignowner rejected. No realledger fixture writes, copy/refund/clearactive/tail/newbudget.

First production complete model downloaded twohostSHA and independentlocalCPU confirms real one original20minibatch PPOupdate: all17Adam660400→660420, actor9/critic8 changed including retained learnedSTD, allmodel/runtime tensors finite, actualheight35 andsourceSHA. Not merelySTARTED,128/20k discardedproof or futureFINAL/behavioral improvement. Sourcecheckpoint/realrestore/parent actualgo/canonical/creationargv/save/exit remain authoritative. Laptop is not runtime dependency. 72 dual4090 assignment context preserved but no new72 scope dispatched here;3060 frozenonly, LaptopGPU paused. No signals/delete/otherjob/installedSDKdriver/system modification.

Inherited entry run_manifest still uses original CURB20 metadata helper and legacy G3→CURB label. They are explicitly retained/disclosed as legacy metadata, not new35 physical evidence; fullPAYLOAD targetSHA/newTASK/actualnewmesh/source20→35startup proof and checkpointheight35 are the current evidence. No livehotpatch or fabricated repaired originalmanifest. DefaultGBK source-reader failure and explicitUTF8 correction, all other failures/rejections/readers/sources/unused/status/workorders/cost/monitor/index retained. LargePTNPZUSDZIPtarraw only actualpath-size-SHA indexed, originals retained; credentials excluded. Unique annotatedstage once, later receipts/FINAL/frozenresults ordinarysupplement; pushfailure existingobjects only, Git never blocks/changes runtime or budget. Same hourlymod4-10, healthyunchanged quiet, no newmonitor or extraSSHwatcher.'''
 with note.open('x',encoding='utf8') as f:f.write(text)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':raise AssertionError('Explicitly defer incomplete collections before archive')
  h=H(p);size=p.stat().st_size;row=dict(source_path=str(p.resolve()),bytes=size,sha256=h);prior=bysha.get(h)
  if prior:
   assert H(REPO/prior['Git_path'])==prior['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=prior['Git_path'],archived_sha256=prior['archived_sha256'])
  elif size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp'):row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   raw=p.read_bytes()
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_success_false_rejection_schema_source_cost_monitor_at_snapshot_included=True,large_originals_retained=True,credentials_excluded=True,later_reports_require_ordinary_supplement=True),indent=2),encoding='utf8');files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title','Start E1 CURB35 height-only branch from qualified878 after actual new-scope frozen and native admission','--kind','training','--note-file',str(note),'--files',*files,'--validation','Actual3060 new35 source878 baseline up8/27 down27/27 ordinary1 with completephysical-sourceCPU; ownsource20→35 fullstate/native144 and independentCPU; discarded128x2/20kx4; first complete production17Adam660400→660420 CPU verified; originalcanonical/no newbudget.','--push'];rec.main();head=git('rev-parse','HEAD');tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;obj=git('rev-parse',tag);g.n.m.cap.g=git;g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head,tag,obj);print(json.dumps(dict(commit=head,tag=tag,object=obj,actual_remote_main_tag_peeled_all1352oldtags_tracked_SHA_verified=True,sources=len(rows))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('CURB35_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),resume_existing_objects_not_repeat_record_tag_commit=True),indent=2),encoding='utf8');raise
