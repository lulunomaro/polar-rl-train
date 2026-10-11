from slope_io import *
def main():
 n,w=connect_both()
 try:
  actual=boundary(n);p=save('CONTEXT_ACTUAL_'+str(time.time_ns())+'.json',actual)
  with n.open_sftp() as f:
   for name in ('curb20_current_state.py','supervise_e1_command_retention_episode_reviewed_once.py'):
    remote=OLD+('/isaac/mod4/' if name=='curb20_current_state.py' else '/')+name
    raw=f.open(remote).read();local=D/'inherited_source'/name;local.parent.mkdir(exist_ok=True);assert not local.exists();local.write_bytes(raw)
  print(json.dumps(dict(report=str(p),own389_closed=True,remaining_seconds=actual['remaining_seconds'],two_OS_locks_free=True,revision004_active_next='E1_SLOPE',source_count=len(actual['source_freeze']['sha256']))))
 finally:cleanup(n,w)
if __name__=='__main__':main()
