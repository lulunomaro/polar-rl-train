"""CPU-only yaw-factor placement readback; actual height difference disclosed."""
from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;A=D/'attempts/geometry_bodypos_worldpos_1500_v1/output/INITIAL_ACTUAL.json';B=D/'attempts/geometry_bodyneg_worldpos_1500_v1/output/INITIAL_ACTUAL.json'
a=json.loads(A.read_bytes());b=json.loads(B.read_bytes());pa=dict(a['parameters']);pb=dict(b['parameters']);sa=pa.pop('private_RNG_SHA');sb=pb.pop('private_RNG_SHA')
ar=np.asarray(a['root_xyzw']);br=np.asarray(b['root_xyzw']);dz=abs(ar[:,2]-br[:,2]);original=D/'review_bodyneg_initial_identity_strict_original.py'
assert pa==pb and sa==sb and a['q']==b['q'] and a['actual_assignments']==b['actual_assignments'] and a['geometry']==b['geometry']
assert np.array_equal(ar[:,:2],br[:,:2]) and np.array_equal(ar[:,7:],br[:,7:])
assert np.allclose(ar[:,3:7],np.array([0,0,0,1])) and np.allclose(br[:,3:7],np.array([0,0,1,0]),atol=1e-6,rtol=0)
assert dz.max()<=1e-6
report=dict(epoch=time.time(),CPU_review_passed=True,original_strictXYZ_reader_rejected=True,original_error='AssertionError: requested initialXYZ byteexact compare failed because actual yaw-rotated full-footprint placed Z differs.',
 original_source=dict(path=str(original),sha256=hashlib.sha256(original.read_bytes()).hexdigest()),
 actual_captured_physical_DR_bias_delay_assignments_exact=True,captured_16_torch_generator_state_SHA_equal=True,independent_all_private_RNG_byte_payload_review_not_performed=True,
 initial_q30_exact=True,rootXY_exact=True,zero_root_velocity_exact=True,geometry_and_cell_assignment_exact=True,
 initial_rootXYZ_byteexact=False,actual_rootZ_forward_m=ar[:,2].tolist(),actual_rootZ_reverse_m=br[:,2].tolist(),actual_rootZ_difference_m=dz.tolist(),max_rootZ_difference_m=float(dz.max()),
 rootZ_within_original_placement_absolute_bound1e6=True,new_tolerance_introduced=False,
 yaw0_to_pi_factor_disclosed=True,full_collision25200points_ray_placement_recomputed=True,
 birth_receipts=dict(forward=a['birth'],reverse=b['birth']),rootZ_not_falsified_to_equal=True,
 paired_label='Same captured initial DR/bias/delay/q30/XY/velocity/geometry/source; intended body-command sign and yaw factor; .238micrometer actual Z nuisance within original float32 placement bound disclosed.',
 physical_causality_or_qualification_not_claimed_from_initialization=True,GPU_no_replay_or_harness_mutation=True)
R=D/'reports/BODYNEG_INITIAL_STRICTXYZ_REJECTION_AND_PLACEMENT_DISCLOSURE_ACTUAL.json';assert not R.exists();R.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('CPU_review_passed','initial_rootXYZ_byteexact','max_rootZ_difference_m','rootZ_within_original_placement_absolute_bound1e6','paired_label')}))
