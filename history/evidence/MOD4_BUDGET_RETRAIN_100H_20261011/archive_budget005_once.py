"""Record the new approved budget/retraining stage once and verify original Git objects."""
from prepare_authorization_and_dispatch_once import D,R,W,H,save
from pathlib import Path
import sys,subprocess,json,time,traceback

REPO=W/'polar-rl-train'
DEST=REPO/'history/evidence'/D.name
ID='budget-seventh100h-and-unqualified-expert-retraining-approved'


def g(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()


def refs():
 tags={line.split('|')[0]:(line.split('|')[1],line.split('|')[2] or line.split('|')[1])
       for line in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==g('rev-parse','HEAD')
 for name,(obj,peeled) in tags.items():
  assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
 return tags


def capture(dest):
 assert not dest.exists();dest.mkdir(parents=True)
 sys.path.insert(0,str(REPO/'archive_tools'))
 from capture_history import redact
 entries=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=H(raw))
  if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip') or len(raw)>50_000_000:
   row.update(capture='large_actual_original_SHA_index_only',original_retained=True)
  else:
   clean,n=redact(raw.decode('utf8'));out=dest/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True)
   out.write_bytes(clean.encode());gp=out.relative_to(REPO).as_posix();files.append(gp)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',redactions=n,
       Git_path=gp,archived_sha256=H(out.read_bytes()))
  entries.append(row)
 index=dest/'REPORT_CAPTURE_INDEX.json'
 index.write_bytes(json.dumps(dict(epoch=time.time(),entries=entries,all_current_new_saved_reports_sources_errors_monitors_captured=True,
  canonical_not_copied_as_authority=True,all_old_false_raw_cost_preserved=True,credentials_excluded=True,
  later_Git_receipt_and_central_monitor_sync_require_supplement=True),ensure_ascii=False,indent=2).encode())
 files.append(index.relative_to(REPO).as_posix())
 return entries,files


def main():
 assert not (R/'STAGE_GIT_RECORDED.json').exists() and not DEST.exists()
 assert not g('status','--porcelain')
 assert json.loads((R/'BUDGET_APPLIED.json').read_bytes())['applied_once']
 assert json.loads((R/'METADATA_SYNCED.json').read_bytes())['metadata_synced']
 assert json.loads((R/'MONITOR_ACTUAL_VERIFIED.json').read_bytes())['prompt_exact']
 tags=refs();before=g('rev-parse','HEAD')
 assert not g('tag','--list','*'+ID)
 save('ARCHIVE_STARTED.json',dict(epoch=time.time(),unique_trial_id=ID,prior_main=before,old_tag_count=len(tags),
       no_old_record_replay=True,push_failure_continue_existing_objects_only=True))
 note=R/'STAGE_REPORT.md'
 with note.open('xb') as f:f.write('''# 新增100小时与未毕业独立专家复训授权实际完成

人类直接授权“预算再给你100小时，没毕业的可以复训”。新005计划与新独立budget writer仅执行第七次USER_ADD100H_20261011_7TH；读取自身最新完整source40424b PASSED、实际parent/guardian/child退出、原唯一结清段、canonical active为空以及两真实fcntl锁后执行。新授权总1188000秒330小时，剩676797.5426192284秒约188小时快照；charged511202.45738077164秒、184旧段、原六次扩展全部exact不变，不重tail/复制canonical/clearactive或加自动时间。唯一新增360000秒有APPLIED字节回执。

新PLAN_APPROVAL仅改预算上限和005授权引用；执行合同预算与central current同步。原master812a4b、EXECUTION_TRACKS、RM003、004职责与其批准字节保持，不伪改旧批准。新纯预算函数验证合法第七扩展/charged历史保留及active/重复/未批准/错注册total四拒绝；没有GPU/PPO启动。

未毕业专家可以按失败原因独立有界复训。优先CURB20正向入口/方向，再WAVE35完整路线，冻结E0与已接受SLOPE5/8/10范围。新增100小时为可调整规划CURB25/WAVE25/坡15/真台阶10/gate切换15/准入修复10；原S3含已用30小时加新增地形75小时为105小时规划上限，不必须花满或ledgerreserve。新的CURB reset-entry实际footprint/histogram/fullstate/SDK/native/PPO合同仍pending，不借扩预算伪称已启动训练。旧退化weights只审查证据，所有false/raw/cost/prefix保留。新观察/硬件、危险S8reset等权限不扩大。

mod4-10原ACTIVE每2h、targetthread和静默健康pending保持，旧实际138和CURB下一轴证据保留；新prompt明确330小时/七扩展及005复训权限，实际TOML prompt exact验证。所有新source、预算回执、准入证明、同步、monitor与旧prompt字节入Git；以后stageGitreceipt/central同步追加普通supplement，最终工具验证不另造报告。
'''.encode())
 entries,files=capture(DEST)
 run=subprocess.run([sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,
  '--title','Apply explicitly authorized seventh100h budget and bounded expert retraining revision',
  '--kind','repair','--note-file',str(note),'--files',*files,'--validation',
  'Own40424b fullsave PASSED actual exited identities twoOSlocksfree idlecanonical verified. Unique seventh360000s applied; total1188000 charged/completed184/old6 exact. PLAN_APPROVAL ceiling/contract/current synced; mastertracksRM004 unchanged. Pure guard rejects active/replay/unapproved/wrongtotal. Retraining005 scoped independent bounded repair authorized; no newGPU/PPO/S8. Existing mod4-10 ACTIVE2h prompt exact. Allsaved new reports sources receipts monitors captured.','--push'],
  capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:
  save('STAGE_RECORD_ERROR.json',dict(epoch=time.time(),returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,
      may_have_committed_continue_objects_after_inspection=True,no_repeat_record_tag_or_commit=True))
  raise RuntimeError('Record/push refused; inspect original objects')
 tag,head=run.stdout.strip().splitlines()[-1].split();obj=g('rev-parse',tag)
 remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in tags.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 assert not g('status','--porcelain')
 save('STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,
  remote_main_tag_peeled_verified=True,push_pending=False,old_tag_objects_unchanged=True,
  old_tag_count=len(tags),captured_files=len(files),all_saved_stage_reports_captured=True))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,captured_files=len(files),old_tags_preserved=len(tags))))


if __name__=='__main__':
 try:main()
 except BaseException:
  save('ARCHIVE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_repeat_record_without_actual_object_review=True))
  raise
