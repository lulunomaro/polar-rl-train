from repair_io import *
def main():
 n,w=connect_both()
 try:
  a=boundary(n);save('ENTRY_AUTHORITY_ACTUAL.json',a)
  folder=D/'inherited_source';folder.mkdir()
  selected=('retention_flat_runtime_named_owned.py','retention_flat_runtime.py','retention_flat_command.py','retention_command_state.py','e1_terrain_checkpoint.py','e1_full_pose_reset.py','curb20_current_state.py','train_curb20_environment_view_resume_ppo.py','train_curb20_fresh_preflight_ppo.py','curb20_fullsave_cpu.py','probe_curb20_fresh_process_full_resume.py','plan_budget_contract.py','supervise_e1_command_retention_episode_reviewed_once.py','supervise_curb20_formal_dispatch_reviewed_once.py','supervise_curb20_fullstate_once.py')
  files=[]
  with n.open_sftp() as f:
   for name,h in a['oldsource']['sha256'].items():
    if Path(name).name not in selected:continue
    raw=f.open(OLD+'/'+name).read();assert H(raw)==h
    p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);files.append(dict(path=name,sha256=h,bytes=len(raw)))
   for name in ('SOURCE_SELECTED.json','CURB_FOUR_CASE_TEMPLATES.json'):
    raw=f.open(OLD+'/reports/'+name).read();p=folder/'reports'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
  save('SOURCE_READ_ACTUAL.json',dict(files=files,source_count=len(a['oldsource']['sha256']),no_GPU=True))
  print(json.dumps(dict(authority_checked=True,source_count=len(a['oldsource']['sha256']),captured=[x['path'] for x in files],remaining_seconds=a['remaining_seconds'])))
 finally:cleanup(n,w)
if __name__=='__main__':main()
