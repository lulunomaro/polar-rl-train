from pathlib import Path
import sys,json,time,subprocess,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as archive
archive.FOLDERS=(D,)
DEST=REPO/'history/evidence'/D.name/'local128_temp_receipt_supplement'
def main():
 assert not archive.gitio.g('status','--porcelain') and not DEST.exists()
 stage=json.loads((R/'LOCAL_TEMP_STAGE_GIT_RECORDED.json').read_bytes());assert stage['passed']
 old=archive.gitio.refs();rows,files=archive.capture(DEST)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+bytes([0]) for v in files),capture_output=True,check=True)
 archive.gitio.g('commit','-m','Append actual local temporary training archive receipt and current snapshots')
 archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
 remote={line.split()[1]:line.split()[0] for line in archive.gitio.g('ls-remote','origin','refs/heads/main','refs/tags/'+stage['tag'],'refs/tags/'+stage['tag']+'^{}').splitlines()}
 assert remote['refs/tags/'+stage['tag']]==stage['tagobject'] and remote['refs/tags/'+stage['tag']+'^{}']==stage['commit']
 print(json.dumps(dict(passed=True,supplement_commit=head,remote_main_verified=True,original_stage_tag_and_peeled_preserved=True,old_tags_preserved=len(old),sources=len(rows),future_actualfinal_cost_reports_must_append=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('LOCAL_TEMP_SUPPLEMENT_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),continue_existingobjects_no_recommit=True)),encoding='utf8');raise
