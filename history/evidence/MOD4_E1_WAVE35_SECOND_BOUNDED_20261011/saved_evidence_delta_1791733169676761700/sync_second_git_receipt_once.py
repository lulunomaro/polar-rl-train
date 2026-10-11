from second_io import *
def main():
 p=R/'SECOND_STAGE_GIT_RECORDED.json';v=json.loads(p.read_bytes());assert v['remote_main_tag_peeled_verified'] and not v['push_pending']
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_WAVE35_SECOND_BOUNDED_STAGE_GIT_RECORDED.json',p.read_bytes())
  z=run(n,r'''from pathlib import Path
import json,time,os
R=Path(CENTRAL_TOKEN)/'reports';j=lambda p:json.loads(p.read_bytes());p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);s=c['terrain_subexpert_revision004']['wave35_second_bounded_scope']
assert s['root']==ROOT_TOKEN and s['source_count']==369
v=j(R/'E1_WAVE35_SECOND_BOUNDED_STAGE_GIT_RECORDED.json');assert v['remote_main_tag_peeled_verified'] and not v['push_pending']
s.update(actual_stage_git_report=str(R/'E1_WAVE35_SECOND_BOUNDED_STAGE_GIT_RECORDED.json'),actual_stage_git_commit=v['commit'],actual_stage_git_tag=v['tag'],later_saved_reports_require_ordinary_supplement=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SECONDGIT-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
z=dict(epoch=time.time(),metadata_synced=True,stage_commit=v['commit'],stage_tag=v['tag'],canonical_not_written=True,no_GPU_or_old_once_replay=True)
p=R/'E1_WAVE35_SECOND_BOUNDED_STAGE_GIT_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(z,indent=2));print(json.dumps(z))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('ROOT_TOKEN',repr(ROOT)))
  save('SECOND_STAGE_GIT_METADATA_SYNCED.json',z);print(json.dumps(z))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
