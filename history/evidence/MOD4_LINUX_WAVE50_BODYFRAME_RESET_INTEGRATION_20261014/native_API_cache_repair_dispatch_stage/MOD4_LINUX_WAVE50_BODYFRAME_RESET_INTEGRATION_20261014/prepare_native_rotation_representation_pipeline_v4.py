"""Respect native quaternion normalization/double cover, keep strict XYZ/query."""
from pathlib import Path
import hashlib,json,time
import numpy as np
from scipy.spatial.transform import Rotation

B=Path(__file__).resolve().parent;P=B/'payload_v1'
q=np.asarray([-8.928701333843492e-09,3.822725469504462e-11,.9999999403953552,-9.129352829262416e-11],np.float32)
unit=q/np.linalg.norm(q)
assert not np.array_equal(q,unit)
assert np.max(np.abs(Rotation.from_quat(q).as_matrix()-Rotation.from_quat(unit).as_matrix()))<1e-12
assert np.max(np.abs(Rotation.from_quat(q).as_matrix()-Rotation.from_quat(-unit).as_matrix()))<1e-12
adapter=P/'birth_bodyframe_reset_adapter_v5.py';assert not adapter.exists()
src=(P/'birth_bodyframe_reset_adapter_v4.py').read_text(encoding='utf8')
anchor="    assert proof['data_vs_native_root_getter_exact'] is True"
assert src.count(anchor)==1
src=src.replace(anchor,"    assert proof['data_native_XYZ_exact'] is True\n    assert proof['data_native_rotation_matches_normalized_sign_invariant'] is True")
adapter.write_text(src,encoding='utf8')
ck=P/'birth_bodyframe_full_checkpoint_v4.py';assert not ck.exists()
src=(P/'birth_bodyframe_full_checkpoint_v3.py').read_text(encoding='utf8').replace('from birth_bodyframe_reset_adapter_v4 import','from birth_bodyframe_reset_adapter_v5 import')
anchor="    assert native.shape == (N, 7) and torch.equal(native, data), 'Native/data root convention mismatch'"
replace="""    assert native.shape == (N, 7)
    exact_bits = torch.equal(native, data)
    xyz_exact = torch.equal(native[:, :3], data[:, :3])
    nq = native[:, 3:7]; dq = data[:, 3:7]
    assert torch.isfinite(nq).all() and torch.isfinite(dq).all()
    assert torch.allclose(nq.square().sum(-1), torch.ones(N, device=env.device), atol=1e-6, rtol=0)
    nn = nq / nq.norm(dim=-1, keepdim=True); dn = dq / dq.norm(dim=-1, keepdim=True)
    rotation_error = torch.minimum((nn-dn).norm(dim=-1), (nn+dn).norm(dim=-1))
    witness_index = getattr(env, '_bodyframe_native_getter_witness_count', 0)
    env._bodyframe_native_getter_witness_count = witness_index + 1
    witness = Path(manifest['actual_target_root']) / ('NATIVE_ROOT_GETTER_DATA_WITNESS_'+str(witness_index)+'.pt')
    torch.save(dict(native=native.cpu(), data=data.cpu(), rotation_error=rotation_error.cpu(),
                    raw_bits_exact=exact_bits, XYZ_exact=xyz_exact,
                    quaternion_normalization_and_sign_equivalence_only=True), witness)
    assert xyz_exact, 'Native/data root XYZ differs; no spatial tolerance relaxation'
    assert (rotation_error <= 1e-6).all(), 'Native/data quaternion rotation differs beyond unit-rotation representation bound'"""
assert src.count(anchor)==1;src=src.replace(anchor,replace)
anchor="                data_vs_native_root_getter_exact=True, native_setter_readback_required=True,"
replace="                data_vs_native_root_getter_exact=exact_bits, data_native_XYZ_exact=xyz_exact,\n                data_native_rotation_matches_normalized_sign_invariant=True,\n                quaternion_rotation_error_max=float(rotation_error.max()),\n                native_getter_witness=str(witness), native_getter_witness_SHA=sha(witness),\n                native_setter_readback_required=True,"
assert src.count(anchor)==1;src=src.replace(anchor,replace);ck.write_text(src,encoding='utf8')
for old,new in [('bodyframe_native_worker_v5.py','bodyframe_native_worker_v6.py'),('bodyframe_formal_worker_v3.py','bodyframe_formal_worker_v4.py')]:
    dst=P/new;assert not dst.exists();dst.write_bytes((P/old).read_bytes().replace(b'from birth_bodyframe_full_checkpoint_v3 import',b'from birth_bodyframe_full_checkpoint_v4 import'))
parent=P/'bodyframe_finite_pipeline_parent_v4.py';assert not parent.exists()
parent.write_bytes((P/'bodyframe_finite_pipeline_parent_v3.py').read_bytes().replace(b'bodyframe_native_worker_v5.py',b'bodyframe_native_worker_v6.py').replace(b'bodyframe_formal_worker_v3.py',b'bodyframe_formal_worker_v4.py'))
mat=B/'bodyframe_target_materialize_CPU_v3.py';assert not mat.exists();mat.write_bytes((B/'bodyframe_target_materialize_CPU_v2.py').read_bytes().replace(b'from birth_bodyframe_full_checkpoint_v3 import',b'from birth_bodyframe_full_checkpoint_v4 import'))
transport=B/'transport_bodyframe_pipeline_v4.py';assert not transport.exists();transport.write_text("from transport_bodyframe_root_owned import *\nROOT=BASE+'/bodyframe20k_repair_pipeline_v4_native_rotation_repr_20261014'\n",encoding='utf8')
src=(B/'materialize_and_dispatch_bodyframe_pipeline_v3_once.py').read_text(encoding='utf8')
for before,after in [('transport_bodyframe_pipeline_v3','transport_bodyframe_pipeline_v4'),('birth_bodyframe_reset_adapter_v4.py','birth_bodyframe_reset_adapter_v5.py'),('birth_bodyframe_full_checkpoint_v3.py','birth_bodyframe_full_checkpoint_v4.py'),('bodyframe_native_worker_v5.py','bodyframe_native_worker_v6.py'),('bodyframe_formal_worker_v3.py','bodyframe_formal_worker_v4.py'),('bodyframe_finite_pipeline_parent_v3.py','bodyframe_finite_pipeline_parent_v4.py'),('bodyframe_target_materialize_CPU_v2.py','bodyframe_target_materialize_CPU_v3.py'),('unique_upload_v3_articulation_api','unique_upload_v4_native_rotation_repr'),('PIPELINE_V3_MATERIALIZE','PIPELINE_V4_MATERIALIZE')]:src=src.replace(before,after)
dispatch=B/'materialize_and_dispatch_bodyframe_pipeline_v4_once.py';assert not dispatch.exists();dispatch.write_text(src,encoding='utf8')
collector=B/'collect_bodyframe_finite_pipeline_v4_actual.py';assert not collector.exists();collector.write_text((B/'collect_bodyframe_finite_pipeline_v3_actual.py').read_text(encoding='utf8').replace('transport_bodyframe_pipeline_v3','transport_bodyframe_pipeline_v4'),encoding='utf8')
for path in (adapter,ck,P/'bodyframe_native_worker_v6.py',P/'bodyframe_formal_worker_v4.py',parent,mat,dispatch,collector):compile(path.read_bytes(),str(path),'exec')
out=B/'reports/NATIVE_QUATERNION_UNIT_ROTATION_REPRESENTATION_V4_CPU_ACTUAL.json';assert not out.exists()
out.write_text(json.dumps(dict(epoch=time.time(),actual_retained_quat=q.tolist(),norm_square_error=float(abs((q*q).sum()-1)),
    normalized_raw_bits_differ=True,SciPy_placement_already_normalizes_input_quaternions=True,
    normalized_and_signed_quat_represent_same_rotation_CPU_passed=True,
    original_v3_postsetter_bitexact_false_preserved=True,
    new_audit='Persist both complete native/data pose arrays. Keep strict XYZ equality and original1e-6 query; compare unit quaternions modulo sign under original quaternion normalization bound1e-6. Do not claim raw bitexact when native renormalizes.',
    no_physical_command_reward_DR_parameter_or_threshold_change=True,
    no_old_once_replay_or_hotpatch=True,actual_live_pass_not_yet_claimed=True),indent=2),encoding='utf8')
print(json.dumps(dict(rotation_representation_CPU_proved=True,strict_XYZ_and_query_unchanged=True,new_sources_compile=True)))
