"""Resume one existing committed supplement after TLS failure; never recommit."""
from pathlib import Path
import sys,json,time
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train';R=D/'reports';sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
HEAD='1877c052ae41c667e5b65a9ec799d4178430f05e'
def main():
 assert cap.g('rev-parse','HEAD')==HEAD and not cap.g('status','--porcelain')
 rows=json.loads((REPO/'history/evidence'/D.name/'ordinary_complete15_two_devseeds_tails_and_handoff_v2/REPORT_CAPTURE_INDEX.json').read_bytes())['entries'];remote={x.split()[1]:x.split()[0] for x in cap.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']=='5ea503154cb791259d3c9aadc4b1bc8447e3188f'
 old={k:(v,remote.get(k+'^{}',v)) for k,v in remote.items() if k.startswith('refs/tags/') and not k.endswith('^{}')};assert len(old)==1345
 for name,(obj,peeled) in old.items():assert cap.g('rev-parse',name)==obj and cap.g('rev-parse',name+'^{}')==peeled
 cap.g('push','origin','HEAD');cap.a.verify(rows,old,HEAD)
 v=dict(epoch=time.time(),existing_commit=HEAD,original_TLS_failure_preserved=True,resumed_existing_objects_only=True,actual_remote_main_and_all1345_oldtag_objects_peeled_verified=True,actual_tracked_SHA_verified=True,saved_sources=len(rows),no_record_tag_or_commit_repeated=True)
 p=R/'COMPLETE15_EXISTING_ORDINARY_PUSH_RESUMED_REMOTE_V2_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
if __name__=='__main__':main()
