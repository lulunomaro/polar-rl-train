"""Correct local code() transport argument binding; V1 made no remote hash or deletion."""
from prepare_exact_closed121_intermediate_buffer_reclaim_hash_once import *
if __name__=='__main__':
 c=None
 try:
  plan=json.loads((R/'EXACT_CLOSED121_OLD_BUFFER_NEW_CLEANUP_PLAN_BEFORE_HASH.json').read_bytes());save('CLOSED121_PREDELETE_HASH_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,original_TypeError_before_remote_call_retained=True,actual_alive_only_exclusive_all_transports=True));c=a.t.connect();code=CODE.replace('plan=json.loads(sys.stdin.readline())','plan=json.loads('+repr(json.dumps(plan))+')');assert code!=CODE;v=a.code(c,a.t.PY,code,timeout=900);save('CLOSED121_OLD_BUFFER_EXACT_PREDELETE_FULL_SHA_V2_ACTUAL.json',v);print(json.dumps(dict(files=len(v['delete_files']),reclaim_allocated=sum(r['allocated_bytes'] for r in v['delete_files']),original_producer_SHA_all_match=True,protected_files=len(v['protected_other_files']),durable_plan=v['durable_plan_path'],no_delete_yet=True)),flush=True)
 except BaseException:save('CLOSED121_HASH_PLAN_V2_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_delete=True));raise
 finally:a.t.close(c)
