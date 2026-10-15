"""Command-local Windows TLS backend; resume existing commit only."""
from pathlib import Path
import sys,json,time,subprocess,traceback
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train';R=D/'reports';sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
HEAD='1877c052ae41c667e5b65a9ec799d4178430f05e'
def g(*args):
 p=subprocess.run(['git','-c','http.sslBackend=schannel','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8',timeout=90);assert p.returncode==0,p.stderr;return p.stdout.strip()
def main():
 assert g('rev-parse','HEAD')==HEAD and not g('status','--porcelain');rows=json.loads((REPO/'history/evidence'/D.name/'ordinary_complete15_two_devseeds_tails_and_handoff_v2/REPORT_CAPTURE_INDEX.json').read_bytes())['entries']
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main'] in ('5ea503154cb791259d3c9aadc4b1bc8447e3188f',HEAD)
 old={k:(v,remote.get(k+'^{}',v)) for k,v in remote.items() if k.startswith('refs/tags/') and not k.endswith('^{}')};assert len(old)==1345
 local={}
 for line in g('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  t=line.split();local[t[0]]=(t[1],t[2] if len(t)>2 else t[1])
 assert old==local
 g('push','origin','HEAD');cap.a.gitio.g=g;cap.a.verify(rows,old,HEAD)
 v=dict(epoch=time.time(),existing_commit=HEAD,original_TLS_and_reader_failures_preserved=True,command_local_schannel_certificate_verification_kept_no_global_config_change=True,resumed_existing_objects_only=True,actual_remote_main_all1345_oldtags_and_trackedSHA_verified=True,saved_sources=len(rows),no_record_tag_commit_repeat=True)
 p=R/'COMPLETE15_EXISTING_ORDINARY_PUSH_RESUMED_REMOTE_V3_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('COMPLETE15_PUSH_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_record_tag_commit_GPU_budget_repeat=True),indent=2),encoding='utf8');raise
