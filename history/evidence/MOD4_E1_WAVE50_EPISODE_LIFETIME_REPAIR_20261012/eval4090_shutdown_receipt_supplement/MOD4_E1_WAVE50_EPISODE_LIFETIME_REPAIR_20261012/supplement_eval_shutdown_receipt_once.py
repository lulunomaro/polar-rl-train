from pathlib import Path
import json,subprocess
import archive_eval4090_human_pause_stage_once as stage
archive=stage.archive;D=stage.D;REPO=stage.REPO
DEST=REPO/'history/evidence'/D.name/'eval4090_shutdown_receipt_supplement'

def main():
 assert not DEST.exists() and not archive.gitio.g('status','--porcelain')
 receipt=json.loads((D/'reports/EVAL4090_SHUTDOWN_STAGE_GIT_RECORDED.json').read_bytes());assert receipt['remote_main_tag_peeled_verified']
 old=archive.gitio.refs();archive.FOLDERS=(D,);rows,files=archive.capture(DEST)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+bytes([0]) for p in files),capture_output=True,check=True)
 archive.gitio.g('commit','-m','Archive shutdown pause stage receipt and complete backup report references')
 archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
 assert not archive.gitio.g('status','--porcelain')
 print(json.dumps(dict(passed=True,ordinary_supplement=head,remote_main_verified=True,all_old_tags_preserved=len(old),all_latest_saved_reports_and_stage_receipt_tracked_exact=True,backup_originals_retained=True)))

if __name__=='__main__':main()
