"""Independent stdlib/proc-only reader; original psutil reader/error preserved."""
import json
import read_left_second_sameidentity_current_compact_actual as original
from remote_session import execute
def main():
 code=original.CODE.replace('import json,hashlib,time,fcntl,psutil','import json,hashlib,time,fcntl')
 begin=code.index('for pid in sorted(ids):');end=code.index('locks=[]',begin)
 code=code[:begin]+'''for pid in sorted(ids):
 p=Path('/proc',str(pid))
 try:
  actual.append(dict(pid=pid,start_ticks=int((p/'stat').read_text().split(') ',1)[1].split()[19]),argv=(p/'cmdline').read_bytes().replace(b'\\0',b' ').decode(errors='replace'),cwd=str((p/'cwd').resolve()),child_pids=(p/'task'/str(pid)/'children').read_text().split()))
 except FileNotFoundError:pass
'''+code[end:]
 v,p=execute('ROOT='+repr(original.R)+'\n'+code,'LEFT_SECOND_SAMEIDENTITY_CURRENT_PROC_COMPACT_ACTUAL',45)
 f=v['files'];print(json.dumps(dict(report=str(p),parent_error=f['LEFT_SECOND_FORMAL_PARENT_ERROR.json'],ownfinal=bool(f['LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json']),phase=(f['CURRENT_STAGE.json'] or {}).get('phase'),latest_complete=f.get('latest_complete'),startup_count=len(f.get('startup_markers',[])),health=f.get('health_compact'),worker=f.get('worker_log'),actual_processes=v['actual_processes'],locks=v['actual_fcntl_locks'],canonical=v['canonical_snapshot'])))
if __name__=='__main__':main()
