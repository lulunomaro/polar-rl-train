from route_second_io import *
A=W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012'
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'
def write(name,text):
    p=D/name;assert not p.exists();compile(text,str(p),'exec');p.write_text(text,encoding='utf8');return dict(path=str(p),sha256=H(p.read_bytes()))

def main():
    rows=[]
    text=(A/'read_route443_own_formal_actual.py').read_text()
    text=text.replace('from route_fixture_io import *',"from route_second_io import *\nROOT="+repr(NEWROOT))
    for a,b in {
        'supervise_wave50_route_fixture_reviewed_once':'supervise_wave50_route_startup_resource_reviewed_once',
        'e1_WAVE50_route_lifecycle_observation':'e1_WAVE50_route_startup_resource_reviewed_observation',
        '==443':'==449','actual_source_count=443':'actual_source_count=449',
        'wrapper.prior.SOURCE_SHA':'wrapper.INIT_SHA',
        "assert not t['terrain_state_restored_exact'] and t['explicit_G3_to_WAVE50_geometry_transition'] and t['explicitly_new_E1_terrain']":"assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and not t['explicitly_new_E1_terrain']",
        "not e['same_entry_identity_restored_exact'] and e['explicit_new_entry_scope']":"e['same_entry_identity_restored_exact'] and not e['explicit_new_entry_scope']",
        "not direction['predecessor_direction_state_restored_exact'] and direction['explicit_new_episode_direction_scope']":"direction['predecessor_direction_state_restored_exact'] and not direction['explicit_new_episode_direction_scope']",
        "route['explicit_new_route_lifecycle_scope'] and not route['predecessor_route_state_restored_exact']":"not route['explicit_new_route_lifecycle_scope'] and route['predecessor_route_state_restored_exact']",
        'E1_WAVE50_route_lifecycle_saved_review_ready':'E1_WAVE50_route_startup_resource_reviewed_saved_review_ready',
        'ROUTE443_OWN_FORMAL_CPU_ACTUAL_':'RESOURCE449_OWN_FORMAL_CPU_ACTUAL_',
        'ROUTE443_OWN_CPU_READER_ERROR_':'RESOURCE449_OWN_FORMAL_READER_ERROR_',
        'old35_full_CPU_CUDA_then_explicit50_entry_direction_route_identity_verified=True':'same50_entry_direction_route_full_CPU_CUDA_restored_exact=True'} .items():
        assert a in text,a;text=text.replace(a,b)
    rows.append(write('read_resource449_own_formal_actual.py',text))
    for source,target in (('collect_route443_candidate_actual.py','collect_resource449_candidate_actual.py'),('review_route443_candidate_actual.py','review_resource449_candidate_actual.py'),('review_route443_complete_dynamic_family_trace_actual.py','review_resource449_complete_dynamic_family_trace_actual.py')):
        text=(A/source).read_text()
        text="import sys\nfrom pathlib import Path\nsys.path.insert(0,"+repr(str(A))+')\n'+text
        text=text.replace('from route_fixture_io import *','from route_second_io import *').replace('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012',NEWROOT).replace('e1_WAVE50_route_lifecycle_observation','e1_WAVE50_route_startup_resource_reviewed_observation')
        for a,b in (('ROUTE443_CANDIDATE','RESOURCE449_CANDIDATE'),('ROUTE443_OWN_FORMAL','RESOURCE449_OWN_FORMAL'),('ROUTE443_FULL_TRAINING_TRACE','RESOURCE449_FULL_TRAINING_TRACE'),('==443','==449')):text=text.replace(a,b)
        rows.append(write(target,text))
    text=(A/'review_route443_direct151_prefix_actual.py').read_text().replace('from route_fixture_io import *','from route_second_io import *')
    text=text.replace("latest(PRIOR/'reports'", "latest(W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012'/'reports'")
    text=text.replace('SECOND_DIRECTION_CANDIDATE_COLLECTED','ROUTE443_CANDIDATE_COLLECTED').replace('SECOND_DIRECTION_CANDIDATE_ACTUAL_REVIEW','ROUTE443_CANDIDATE_ACTUAL_REVIEW')
    text=text.replace("latest(R,'ROUTE443_CANDIDATE", "latest(R,'RESOURCE449_CANDIDATE")
    text=text.replace('ROUTE443_DIRECT151','RESOURCE449_DIRECT152').replace('source151','source152').replace('direct151_actual','direct152_actual')
    rows.append(write('review_resource449_direct152_prefix_actual.py',text))
    save('RESOURCE449_FUTURE_READERS_PREPARED.json',dict(epoch=time.time(),passed=True,readers=rows,compiled_only_not_future_formal_or_candidate_pass=True,own_source449_CPU107_ten_same_identity_markers=True,same50_original_query_contact_COMhardware_sensor_feedback_protocol_unchanged=True,direct152_actual_not151=True,no_GPU_queue_budget_write=True))
    print(json.dumps(dict(prepared=True,count=len(rows),no_future_pass_claim=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_FUTURE_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_GPU_pre_future_report=True));raise
