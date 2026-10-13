from pathlib import Path
import sys,json,subprocess,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
sys.path.insert(0,str(D.parent/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'));import archive_actual_reference_stage_once as archive
archive.FOLDERS=(D,);DEST=REPO/'history/evidence'/D.name/'sameidentity_second7200_receipt_supplement'
def main():
 assert not archive.gitio.g('status','--porcelain') and not DEST.exists()
 stage=json.loads((R/'LOCAL_CONTINUE_STAGE_GIT_RECORDED.json').read_bytes());assert stage['passed'];old=archive.gitio.refs();rows,files=archive.capture(DEST)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+bytes([0]) for v in files),capture_output=True,check=True)
 archive.gitio.g('commit','-m','Append local128 continuation actual archive receipt and current saved snapshots');archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
 remote={x.split()[1]:x.split()[0] for x in archive.gitio.g('ls-remote','origin','refs/heads/main','refs/tags/'+stage['tag'],'refs/tags/'+stage['tag']+'^{}').splitlines()};assert remote['refs/tags/'+stage['tag']]==stage['tagobject'] and remote['refs/tags/'+stage['tag']+'^{}']==stage['commit']
 print(json.dumps(dict(passed=True,commit=head,remote_main_and_originaltag_peeled_verified=True,old_tags_preserved=len(old),sources=len(rows),future_formal_final_reports_require_append=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('LOCAL_CONTINUE_SUPPLEMENT_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),inspectexistingobjects_continuepush_only_no_recommit=True)),encoding='utf8');raise
