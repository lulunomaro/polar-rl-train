"""Bind already validated read-only full50 protocols to actual own426/151 outputs."""
from wave_direction_second_io import *

def main():
    override="""from wave_direction_io import *
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'
def save(name,value):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
"""
    files={
      'collect_second_direction_candidate_actual.py':(PRIOR/'collect_direction_candidate_actual.py',{}),
      'second_direction_feedback_reset_schema.py':(PRIOR/'direction_feedback_reset_schema_reviewed.py',{}),
      'review_second_direction_candidate_actual.py':(PRIOR/'review_direction_candidate_feedback_namespace_reviewed_actual.py',{'from direction_feedback_reset_schema_reviewed import recipe_manager':'from second_direction_feedback_reset_schema import recipe_manager',"cpu['actual_source_count']==424":"cpu['actual_source_count']==426"})}
    rows=[]
    for name,(p,changes) in files.items():
        raw=p.read_bytes();s=raw.decode('utf8');assert s.count('from wave_direction_io import *')==1;s=s.replace('from wave_direction_io import *',override)
        for a,b in changes.items():assert s.count(a)==1;s=s.replace(a,b)
        s=s.replace('e1_WAVE50_direction_observation_PASSED.json','e1_WAVE50_direction_second_bounded_observation_PASSED.json').replace('DIRECTION_CANDIDATE_','SECOND_DIRECTION_CANDIDATE_').replace('DIRECTION_OWN_FORMAL_CPU_ACTUAL_','SECOND_DIRECTION_OWN_FORMAL_CPU_ACTUAL_').replace('DIRECTION_FINAL_FEEDBACK_','SECOND_DIRECTION_FINAL_FEEDBACK_')
        s="import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012'))\n"+s
        out=D/name;compile(s,str(out),'exec');assert not out.exists();out.write_text(s,encoding='utf8');rows.append(dict(original_path=str(p),original_SHA=H(raw),new_path=str(out),new_SHA=H(out.read_bytes())))
    save('SECOND_DIRECTION_CANDIDATE_READERS_PREPARED.json',dict(epoch=time.time(),passed=True,files=rows,own_actual_source426_CPU104_fullsave_bound=True,original50_query_contact_hardware_feedback_recipes_and_115129_tolerances_unchanged=True,preparation_is_not_future_candidate_pass=True,no_GPU_budget_or_task_write=True))
    print(json.dumps(dict(prepared=True,readers=len(rows))))

if __name__=='__main__':
    try:main()
    except BaseException:save('SECOND_DIRECTION_READER_BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
