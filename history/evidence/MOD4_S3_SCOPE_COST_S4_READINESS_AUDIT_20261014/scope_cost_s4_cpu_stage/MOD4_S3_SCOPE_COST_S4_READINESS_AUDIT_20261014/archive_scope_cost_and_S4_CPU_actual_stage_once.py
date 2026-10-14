"""One actual plan/accounting/CPU-interface diagnostic stage, not new training."""
from pathlib import Path
import sys,json,time,subprocess,importlib
from datetime import datetime,timezone,timedelta
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
def main():
 ID='plan005-s3-cost-and-limited-domain-s4-cpu-preparation-reviewed'
 note=A/'S3_SCOPE_005_COST_AND_S4_CPU_PREPARATION_STAGE.md';dest=REPO/'history/evidence'/A.name/'scope_cost_s4_cpu_stage'
 assert not cap.g('status','--porcelain') and not dest.exists() and not cap.g('tag','--list','*'+ID)
 cost=json.loads((R/'S3_E1_CANONICAL_COST_AND_005_105H_PLANNING_ACTUAL_CPU_REVIEW.json').read_bytes());assert cost['passed_read_only_accounting_audit'] and cost['approved005']['both_approved_SHA_exact']
 scope=json.loads((R/'S3_SCOPE_COST_AND_S4_READINESS_GAPS_ACTUAL_CPU_REVIEW.json').read_bytes());assert scope['passed_scope_cost_and_CPU_preparation_review'] and scope['actual_CPU_interface']['optimizer_updates']==0
 old=cap.a.gitio.refs();cap.a.FOLDERS=(A,);rows,files=cap.capture_streaming(dest)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def wrapped(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=wrapped
 sys.argv=['record_experiment.py','--id',ID,'--title','Audit approved105h terrain planning and actual S3 costs, preserve limited experts, verify first S4 CPU interface','--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','Actual original Linux approvals004005 JSON/MD SHA and canonical1188000/7extensions/220unique nonoverlap idle intervals read byteexact without writes. Explicit E1 costs68segments55654.749698877s15.45965h, pending complete localWindows2.61135h plus unknown interrupted512tail kept separate no refund/copy/recharge. Revision005105h terrainplanning corrects isolated30h monitorstatement, gate15h allocation planning and18h repairprotection not ledgertransactions. Frozen observed35Waveb026/20CURB7b/SLOPE24b5_8_10 and E0b109 domains kept narrow, oldstrictfalse/spin regressions and raw kept, no mechanical100percent gate. Two original wholeexpertcheckpoint files twohostSHA; actual9actor tensors35_256_128_64_6ELU compatible,40 actualsaved35vectors CPUcounterfactual only; whole6action hardtop1/clip6/hysteresis and gate-only gradient ownership passed, allfrozen weights/std unchanged, optimizer0/noGPU/no trainedgate. WholeE3 actual20k birthframe logical proposal actualside1420_1400 splits710_710_700_700/sourceallfields/RNGunchanged/selectedreset isolation/14badcases passed; original schema KeyError and independentCPUv2 repair preserved. New Linux native-reset fullstate save restore ABI and firstS4 live route adapter/physics still unadmitted, no newPPO/thirdblindduration/70. All CPUreaders errors/pathsearch rejections/sourceindices/workorders/monitor preserved, largePToriginal indexonly/credentials excluded.','--push']
 rec.main();tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 p=R/'SCOPE_COST_S4_CPU_STAGE_GIT_RECORDED.json';assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,all_oldtags_preserved=len(old),saved_sources=len(rows),later_receipts_require_ordinary_supplement=True),indent=2).encode())
 print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,oldtags_preserved=len(old),saved_sources=len(rows))))
if __name__=='__main__':main()
