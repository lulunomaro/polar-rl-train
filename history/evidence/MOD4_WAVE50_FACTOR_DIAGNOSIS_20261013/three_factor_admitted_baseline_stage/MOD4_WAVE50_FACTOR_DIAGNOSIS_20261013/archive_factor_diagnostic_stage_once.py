from pathlib import Path
import sys,json,time,subprocess,importlib,hashlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train';L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as a
a.FOLDERS=(D,L)
ID='wave50-three-factor-cpu-diagnosis-sharedgpu-baseline-started'
DEST=REPO/'history/evidence'/D.name/'three_factor_admitted_baseline_stage'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not a.gitio.g('status','--porcelain') and not a.gitio.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((D/'reports/TRAINING_HANDOFF_FULLSAVE_CPU_ACTUAL.json').read_bytes())['passed']
 assert (D/'leases/geometry_bodypos_worldpos_120_v1_CLOSED_ACTUAL.json').exists()
 assert (D/'geometry_pose/attempts/geometry_bodypos_worldpos_1500_v1/DISPATCH_RECEIPT.json').exists()
 old=a.gitio.refs()
 note=D/'THREE_FACTOR_ACTUAL_STAGE.md';assert not note.exists()
 note.write_text('''# Shared local GPU factor diagnosis actually admitted and started

Human explicitly requested subagents sharing the local GPU, independent factor tests, causes and repair. Three CPU agents inspect geometry/body-world direction, policy reward/action saturation, and I/O/DR. GPU remains serial with root-issued immutable leases and original native msvcrt lock, one independent process/output/source snapshot per case. No remote trainer/evaluator resumed; no canonical budget write, kill, deletion, installed SDK hotpatch, or WASD input.

Current local128 training was intentionally handed off at next complete update via STOP_AFTER_SAVE. Own model32396 SHA91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4/1418935B/107float,92updates2208controls282624steps8832callbacks; actor9changed/optimizerdelta1840. All46 full NPZ and194 resets/finite/health/coverage, actual parent-child exit/native lockfree reviewed. Unique parent4035.527886867523s includes full load-learn-save-exit; worker4025.8690350055695s separate, not added. Source checkpoints retained. Original7200s window interrupted safely for this new user diagnosis, not failure/exhaustion or training graduation.

Frozen8env120control admission actually passed ground1e-6/rewardformula/contact integral/clock/closure/finite/clip6/data contract. Parent EXIT0 and actual process absence/lockfree; EXIT_NATURAL absent because Kit close did not return to writer, original false kept. Latest91d leftcrank raw approximately-110, clip6 all moving controls and guarded target lowerlimit all controls; right target varies. Short1.2s prefix is not fullroute/contact causality or qualification. Full1500control15s baseline genuinely dispatched; future completion not presumed. Old153 sign interpretation/heading mirror/clip protocol and other rejected hypotheses preserved with independent corrections. I/O AST/source exact; actor A0 is35input feedforward without selected history/absolute heading. Body-speed reward has heading/world route ambiguity, CPU proof not unique physical cause. DR correlations from unmatched old groups not causal.

Single-column action and current-noisy-feedback intervention components have CPU proofs only, no production promotion or clean-truth input. Baseline and factor GPU results need exact actual initial DR/private RNG/geometry/source pairing before inference; no combined factors. Old fullraw source153 referenced by actual path-size-SHA. E0/accepted35/CURB/SLOPE frozen;50mm not qualified/70 no advancement, gate untrained. Physical/query/contactCOMhardware tolerances and production commandDRrewardclock remain. No artificial27/27 or90/95/100 graduation line.

Same mod4-10 hourly heartbeat updated to this new lease-coordinated diagnostic scope, prior prompt preserved with SHA, native TOML exact verified. CPU/source/errors/unused preparation/rejections/receipts/allfalse/costs captured; largeweightsNPZUSDZIP indices only, originals retained. New meaningful stage is unique annotated record_experiment; future tests/results/monitor/Gitreceipt ordinary supplements. Git is not GPU/learning dependency; failed push continues original objects without rerecording. Local unique costs pending originalcanonical reconciliation, no second budget. Work must continue through evidence-supported repair and actual training, not merely work order or blind third duration block.
''',encoding='utf8')
 rows,files=a.capture(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),check=True,capture_output=True);return r.stdout.decode().strip()
  return original(*args)
 rec.git=short_git;sys.argv=['record_experiment.py','--id',ID,'--title','Admit three isolated Wave50 factors and start shared GPU full baseline','--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','Latest own128 fullsave/exits/lockfree and46NPZ actual reviewed. Frozen120control admission pass, original missing appclose receipt retained. Full15s baseline actually launched. Three CPU factor audits and original errors retained; no PPO/remote/budget mutation for tests.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=a.gitio.g('rev-parse','HEAD');obj=a.gitio.g('rev-parse',tag);a.verify(rows,old,head,tag,obj)
 r=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,old_tags_preserved=len(old),saved_sources=len(rows),later_receipt_and_new_case_results_require_supplement=True)
 (D/'reports/FACTOR_STAGE_GIT_RECORDED.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('FACTOR_STAGE_GIT_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_replay_record_tag_commit=True)),encoding='utf8');raise
