from route_second_io import *
import review_resource449_postexit_candidate_actual as original
import route443_feedback_reset_schema as schema

def main():
    p=max(R.glob('RESOURCE449_CANDIDATE_COLLECTED_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));c=json.loads(p.read_bytes());assert not c['pending'] and len(c['cases'])==4
    terrain=[(jid,row['probe']) for jid,row in c['cases'].items() if 'full_route_raw' in row['probe']];assert len(terrain)==1
    jid,probe=terrain[0];raw=R/'cases'/jid/probe['full_route_raw']['name'];assert H(raw.read_bytes())==probe['full_route_raw']['sha256'] and raw.stat().st_size==probe['full_route_raw']['bytes']
    assert schema.R!=R and original.R==R
    oldR=schema.R;schema.R=R
    paths=list((schema.R/'cases').glob('*/'+probe['full_route_raw']['name']));assert paths==[raw]
    save('RESOURCE449_153_READER_RAWPATH_BINDING_REVIEW.json',dict(epoch=time.time(),passed=True,original_feedback_schema_module_path=str(Path(schema.__file__)),original_module_SHA=H(Path(schema.__file__).read_bytes()),original_selected_reports=str(oldR),actual_reports=str(R),actual_job=jid,actual_raw_path=str(raw),actual_raw_bytes=raw.stat().st_size,actual_raw_SHA=probe['full_route_raw']['sha256'],only_observer_path_binding_changed=True,no_original_source_or_GPU_data_overwrite=True,all_original_physical_schema_thresholds_and_feedback_formula_unchanged=True,no_GPU_PPO_evaluation_replay=True))
    original.main()

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_153_RAWPATH_REVIEW_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),readonly_no_GPU_or_evaluation_replay=True));raise
