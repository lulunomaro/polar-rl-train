from route_fixture_io import *

def main():
    src=PRIOR/'read_second_direction_own_formal_actual.py'
    original=src.read_text(encoding='utf8');text=original
    changes={
      'from wave_direction_second_io import *':'from route_fixture_io import *',
      'supervise_wave50_direction_second_bounded_once':'supervise_wave50_route_fixture_reviewed_once',
      'e1_WAVE50_direction_second_bounded_observation':'e1_WAVE50_route_lifecycle_observation',
      '==104':'==107','==426':'==443',
      'actual_finite_tensor_count=104':'actual_finite_tensor_count=107',
      'actual_source_count=426':'actual_source_count=443',
      'wrapper.INIT_SHA':'wrapper.prior.SOURCE_SHA',
      "'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json'):":"'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json'):",
      "assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and not t['explicitly_new_E1_terrain']":"assert not t['terrain_state_restored_exact'] and t['explicit_G3_to_WAVE50_geometry_transition'] and t['explicitly_new_E1_terrain'] and not t['explicit_G2_to_G3_geometry_transition']",
      "assert e['passed'] and e['same_entry_identity_restored_exact'] and not e['explicit_new_entry_scope']":"assert e['passed'] and not e['same_entry_identity_restored_exact'] and e['explicit_new_entry_scope']",
      "assert direction['passed'] and direction['predecessor_direction_state_restored_exact'] and not direction['explicit_new_episode_direction_scope']":"assert direction['passed'] and not direction['predecessor_direction_state_restored_exact'] and direction['explicit_new_episode_direction_scope']",
      "assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact']":"assert c['old_full_D1_D7_optimizer_global_named_streams_verified'] and c['saved_source_episode_plus_one_verified'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact']\nroute=j(run/'E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json');assert route['passed'] and route['explicit_new_route_lifecycle_scope'] and not route['predecessor_route_state_restored_exact'] and route['actual_CUDA_route_disk_roundtrip_exact'] and route['saved_source_episode_plus_one_verified'] and route['no_new_rng']",
      'E1_WAVE50_direction_second_bounded_saved_review_ready':'E1_WAVE50_route_lifecycle_saved_review_ready',
      'SECOND_DIRECTION_OWN_FORMAL_CPU_ACTUAL_':'ROUTE443_OWN_FORMAL_CPU_ACTUAL_',
      'SECOND_DIRECTION_OWN_CPU_READER_ERROR_':'ROUTE443_OWN_CPU_READER_ERROR_',
      'same50_entry_direction_full_CPU_CUDA_restored_exact=True':'old35_full_CPU_CUDA_then_explicit50_entry_direction_route_identity_verified=True',
      'actual same-scope flags, no legacy transition':'actual initial35-to50-entry-direction-route disclosure, strict new scope',
      'Read own426':'Read own443',
    }
    for old,new in changes.items():
        assert old in text,old
        text=text.replace(old,new)
    target=D/'read_route443_own_formal_actual.py';assert not target.exists()
    compile(text,str(target),'exec');target.write_text(text,encoding='utf8')
    save('ROUTE443_OWN_FORMAL_READER_PREPARED.json',dict(epoch=time.time(),passed=True,template_path=str(src),template_SHA=H(src.read_bytes()),actual_initial_scope_reader=str(target),reader_SHA=H(target.read_bytes()),own107_source443_binding=True,ten_actual_startup_markers=True,compiled_only_not_future_ownfinal_pass=True,old35_strict_source_then_explicit_new_scope_not_samegeometry_disclosed=True,no_GPU_budget_controller_mutation=True))
    print(json.dumps(dict(prepared=True,reader=str(target))))

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE443_OWN_READER_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_GPU_reader_only=True));raise
