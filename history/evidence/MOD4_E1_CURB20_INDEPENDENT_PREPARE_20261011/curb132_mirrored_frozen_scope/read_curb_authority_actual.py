"""Reusable read-only authority snapshot before genuinely new CURB scope."""
from curb_io import *
import traceback
def main():
    n,w=connect_both()
    try:
        v=boundary(n)
        with n.open_sftp() as nf:
            reports={}
            for name in ('E1_WAVE_G3_131_COMPLETE_SCOPE_DECISION.json','E1_WAVE_G3_131_COMPLETE_METADATA_SYNCED.json','NEXT_E1_CURB20_INDEPENDENT_WORK_ORDER.md','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json'):
                raw=nf.open(E+'/reports/'+name).read()
                reports[name]=dict(bytes=len(raw),sha256=H(raw),content=json.loads(raw) if name.endswith('.json') else raw.decode())
            decision=reports['E1_WAVE_G3_131_COMPLETE_SCOPE_DECISION.json']['content']
            assert decision['selected_next_warmstart_source_SHA']==SHA and not decision['qualified_wave_expert']
            v['central_reports']=reports
        p=save('CURB_AUTHORITY_ACTUAL_'+str(int(time.time()))+'.json',v)
        print(json.dumps(dict(report=str(p),phase=v['phase'],remaining=v['remaining_seconds'],two_OS_locks_free=True,revision004_approved=True,next_source_SHA=SHA)))
    finally:cleanup(n,w)
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB_AUTHORITY_READ_ERROR_'+str(int(time.time()))+'.json',dict(epoch=time.time(),error=traceback.format_exc(),read_only=True));raise
