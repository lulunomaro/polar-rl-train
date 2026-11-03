"""Pure metadata validation of enabled nominal-candidate evidence, no model IO."""
from pathlib import Path
import math
KIND='NEW_MANUAL_ODOMETRY_AIR_REF_AND_CONTINUOUS_CAPTURE_ANCHOR_TRAIN'
ENTRY='MINIHOP_AIR_PITCH_REF_V1/attempt002/run_manual_air_pitch_ref_v1.py'
CORE='MINIHOP_AIR_PITCH_REF_V1/attempt002/controller.py'

def validate_enabled_nominals(root,protocol,source_rows,flat,rm,flat_manifest,rm_manifest):
    root=Path(root).resolve();configs={c['scene']:c for n,c in protocol['configs']}
    assert len(protocol['configs'])==2 and set(configs)=={'flat','rm'}
    expected={str(Path(z['path']).resolve()):z['SHA']for z in source_rows}
    for scene,result,manifest in(('flat',flat,flat_manifest),('rm',rm,rm_manifest)):
        cfg=result['config'];want=configs[scene]
        assert cfg==want,'actual_nominal_config_differs_from_locked_protocol'
        assert cfg['scene']==scene and cfg['nominal']is True and cfg['hop']['air_pitch_ref_enable']is True
        assert result['kind']==KIND and result['complete']is True
        assert manifest['kind']==KIND and manifest['air_reference_and_continuous_capture_anchor_enabled']is True
        actual={str(Path(z['path']).resolve()):z['SHA']for z in manifest['files']}
        for rel in(ENTRY,CORE):
            key=str((root/rel).resolve())
            assert key in expected and actual.get(key)==expected[key],'actual_nominal_manifest_not_locked_candidate'
    assert flat['proposed_moving_flat_air80_stop_v1']is True
    assert rm['proposed_manual_first_bar_clear_stop_v1']is True
    cross=rm['first_flight_main_rear_crossing_bar_back_s']
    assert type(cross)in(int,float) and math.isfinite(cross)and cross>=0.
    return dict(actual_configs_match_locked_enabled_nominals=True,actual_manifest_core_and_entry_match_locked_candidate=True,
                original_flat_and_local_gates_pass=True,extra_mainfirstflight_condition_pass=True,
                not_dynamic_or_hardware_stability_certificate=True)
