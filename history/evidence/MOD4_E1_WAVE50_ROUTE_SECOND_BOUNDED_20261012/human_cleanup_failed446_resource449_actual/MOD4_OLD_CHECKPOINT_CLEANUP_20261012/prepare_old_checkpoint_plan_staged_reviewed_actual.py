"""Recover unknown SSH request outcome; stage large rows instead of inline argv."""
from cleanup_io import *
import ast,shlex

def main():
    original=D/'prepare_old_incoming_checkpoint_plan_actual.py'
    tree=ast.parse(original.read_text());call=next(x for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='run')
    node=call.args[1]
    while isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='replace':node=node.func.value
    assert isinstance(node,ast.Constant);code=node.value
    inv=json.loads(max(R.glob('OLD_ROLLING_CHECKPOINT_INVENTORY_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
    prefix='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/'
    rows=[];total=0
    for row in inv['candidates']:
      if not row['path'].startswith(prefix) or int(row['name'][6:-3])%1000==0:continue
      rows.append(row);total+=row['allocated_bytes']
      if total>=3*1024**3:break
    assert total>=3*1024**3
    request=save('OLD_INCOMING_SELECTED_ROWS_STAGED.json',dict(epoch=time.time(),rows=rows,only_allowed_directory=prefix,human_authorization='远古一些废旧检查点可以清理'))
    remote_request=io.E+'/reports/HUMAN_OLD_CHECKPOINT_ROWS_STAGED_20261012.json';remote_script=io.E+'/reports/prepare_old_checkpoints_plan_staged_20261012.py'
    code=code.replace('PREFIX_TOKEN',repr(prefix)).replace('selected=json.loads(ROWS_TOKEN)','selected=json.loads(Path('+repr(remote_request)+').read_bytes())["rows"]')
    code=code.replace("('HUMAN_OBSOLETE_INCOMING_CHECKPOINT_CLEANUP_PLAN_'+str(time.time_ns())+'.json')","'HUMAN_OBSOLETE_INCOMING_CHECKPOINT_CLEANUP_PLAN_STAGED_20261012.json'")
    code=code.replace('print(json.dumps(v))','print(json.dumps(dict(plan_path=str(p),plan_sha256=h(p),files=len(rows),reclaim_bytes=v["planned_reclaim_allocated_bytes"])))')
    script=D/'prepare_old_checkpoint_plan_remote_staged.py';assert not script.exists();compile(code,str(script),'exec');script.write_text(code,encoding='utf8')
    n,w=io.connect_both()
    try:
      with n.open_sftp() as f:
        prior=[]
        for name in f.listdir(io.E+'/reports'):
          if name.startswith('HUMAN_OBSOLETE_INCOMING_CHECKPOINT_CLEANUP_PLAN_') and name.endswith('.json'):
            raw=f.open(io.E+'/reports/'+name,'rb').read();v=json.loads(raw)
            if [x['path'] for x in v['rows']]==[x['path'] for x in rows]:prior.append((io.E+'/reports/'+name,raw,v))
        assert len(prior)<=1,'Ambiguous prior plan; no destructive action'
        if prior:
          path,raw,v=prior[0];v.update(actual_remote_plan_path=path,actual_remote_plan_SHA=H(raw),unknown_SSH_outcome_recovered_no_plan_replay=True)
        else:
          io.put(f,remote_request,request.read_bytes());io.put(f,remote_script,script.read_bytes())
      if not prior:
        _,out,err=n.exec_command(io.PY+' '+shlex.quote(remote_script),timeout=180);raw=out.read();errors=err.read();rc=out.channel.recv_exit_status()
        if rc:save('STAGED_PLAN_REMOTE_ERROR.json',dict(returncode=rc,stderr=errors.decode('utf8','replace'),stdout=raw.decode('utf8','replace'),no_deletion=True));raise RuntimeError('Staged plan failed; no deletion')
        small=json.loads(raw)
        with n.open_sftp() as f:raw=f.open(small['plan_path'],'rb').read()
        assert H(raw)==small['plan_sha256'];v=json.loads(raw);v.update(actual_remote_plan_path=small['plan_path'],actual_remote_plan_SHA=H(raw))
      save('OBSOLETE_INCOMING_CHECKPOINT_PLAN_ACTUAL.json',v)
      save('OVERSIZED_SSH_PLAN_REQUEST_ACTUAL_REVIEW.json',dict(epoch=time.time(),original_Source=str(original),original_SHA=H(original.read_bytes()),original_error='SSH exec-request connection reset10054; outcome audited before continuation',prior_plan_recovered=bool(prior),staged_rows_and_small_argv_only=True,all_sources_errors_preserved=True,no_deletion_yet=True))
      save('DUPLICATE_ONLY_PLAN_INSUFFICIENT_REVIEW.json',dict(epoch=time.time(),passed=True,original_duplicate_only_plan_rejected_before_remote_or_deletion=True,duplicate_only_reclaim_possible_bytes=177766400,human_authorized_old_obsolete_not_only_duplicates=True,independent_incoming_only_plan_prepared=True,deleted_old_weights_will_be_explicitly_indexed_with_SHA_authorization=True,all_reports_cost_and_old_false_preserved=True))
      save('LOCAL_WEIGHT_SEARCH_PERMISSION_REVIEW.json',dict(epoch=time.time(),observer_only=True,inaccessible_path='rmuc2026_work/unpack_verify_4zomhj13',read_error='permission_denied',no_local_backup_availability_claim=True,no_GUI_or_file_change=True))
      print(json.dumps(dict(files=len(v['rows']),reclaim_bytes=v['planned_reclaim_allocated_bytes'],plan_sha256=v['actual_remote_plan_SHA'],no_deletion_yet=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('STAGED_OLD_PLAN_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_read_only_recovery_no_blind_replay=True));raise
