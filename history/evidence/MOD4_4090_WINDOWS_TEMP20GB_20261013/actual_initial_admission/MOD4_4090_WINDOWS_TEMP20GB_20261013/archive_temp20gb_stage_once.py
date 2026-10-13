"""One actual temporary branch stage; later reports remain ordinary supplements."""
from pathlib import Path
import sys,time,json,subprocess,importlib
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
def main():
 ID='windows4090-temp20gb-selected2048-repair-admission-failures-preserved';DEST=REPO/'history/evidence'/D.name/'actual_initial_admission';note=D/'ACTUAL_TEMP20GB_STAGE.md'
 assert not note.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
 old=cap.a.gitio.refs();cap.a.FOLDERS=(*cap.a.FOLDERS,D)
 note.write_text('''Human authorized a separate Windows4090 temporary repair branch within20GB memory, followed later by Linuxlarge-scale training. Original20k fulltarget/resource50GB rejection and every old source remain intact/ungranted. New2048 coherent source selection preserves actorcriticstdAdam, originalglobalnamed/dictprivateRNG and all99 selected perenv tensors from immutabled05c/107finite; same2048 strict identity, no91d128 splice or false20k reconstruction. Geometry40x40/10.3Mtriangles, full30q/entry/direction/route4m-Wave40s/clock2.5msx4/TGS32-4/reward/DR/hardware/query-health tolerances unchanged. Independent targetCPUfixture and agentCPUnegative review are actual CPUevidence only, not GPUcapacity/route qualification. New job wholeprocess-tree commit limit20,000,000,000B (no kill-on-close), train RSS/commit18GB save-stop, actual stage peak25%+512MiB headroom required before formal. Scoped smallbatch capacity fiveallocations disclosed/overflow failure strict, no Linuxequivalence claim.

Every actually failed SDKscope preserved: missingMimic Kitdependency beforephysics0PPO; independentexact5thsource completion, then missingContrib beforephysics0PPO; independentexact6thsource dependencygraph completion. Thirdscope completed300controls physically and independentreadback before selectedreset failed on inference-tensor context. No previous scope relabeledPASSED or replayed. Remote command-length refusal beforeCPU mutation, actual absent roots verified and only unexecuted shortcodefile CPUcontinued, allsource/raw/errors/cost retained. Latest independent reset-contextscope wraps only original selectedreset/write/forward/cache update in torch.inference_mode; no extra calls/step/reset/RNG or tolerance change. ActualnewTask lease/globalmsvcrt OSlock/PIDcreation/sourcefreezes ownreceipts define phase, not futurepass. It automatically sequences missing SDK/native2048/fullrestore120 (0PPO) and, only after actualstrict12CPUCUDA+sourceepisode+1/APIoffset/defaultq/own107-99repairedfullsave, first bounded3600/max256PPO. Approvedleft head/std/Adamrow initializer once only afterfullrestore, formal owns repairedfullsave/sameidentity withoutrepeat. Actualpositive savedactor/Adam delta required to call PPO; allqualification remains pending original3060route/skills review.

LaptopGPU/localPPOpaused, evaluations only3060; oldLinuxmain and retiredRPC/floodTUI not restored. No otherprocesskill/delete/SDK sourcehotpatch/canonical write/secondbudget/refund/extension. NewWindows parentunique realcost pending original1188000/sevenextensioncanonical reconciliation; CPU/SDK/native/fullrestore0PPO excluded. E0/accepted35/CURB/SLOPEfrozen/gateuntrained/S8separate/WASDuntouched. Samehourlymod4-10 updated to temporary20GBscope; no new50GB RAM request/extraSSHmonitor. All current newCPUsource/rejections/failures/partialphysicalraw/deploy/monitor/cost/report/log/independentreview captured; largeoriginals pathsizeSHA only; no credentials. Laterownformal/fulltrace/candidate/Gitreceipt supplemented, no tag/re-record onpushfailure.
''',encoding='utf8')
 rows,files=cap.capture_streaming(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
 def wrapped(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=wrapped;sys.argv=['record_experiment.py','--id',ID,'--title','Admit separate20GB Windows2048 repair branch and retain missing-extension/reset failures','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual CPU107/99 selectedstate storage/RNG/source/schema; oldzeroPPO SDKfailures/partialphysical300 trace preserved; independent exact6-extension graph/resetcontext newscope lease; memory job limit, ownsourcefreeze, no installedcode/budget/physics-threshold mutation. GPU/PPO actualreceipt priority.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 (D/'reports/TEMP20GB_STAGE_GIT_RECORDED.json').write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,oldtags_preserved=len(old),saved_sources=len(rows),later_receipts_supplement_required=True),indent=2),encoding='utf8')
 print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,sources=len(rows))))
if __name__=='__main__':main()
