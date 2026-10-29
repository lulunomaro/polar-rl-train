"""Prepare a new source-only candidate. Never reads model/raw/SDK or starts a job."""
from pathlib import Path
import hashlib, json, time, ast

T=Path(__file__).resolve().parent.parent
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
B=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27'
D=L/'native114_WM_fixed_world_heading_visibility_source_v1'
D.mkdir(exist_ok=False)
(D/'reports').mkdir()
old=B/'source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py'
old_bytes=old.read_bytes(); text=old_bytes.decode('utf-8')
before='''        return torch.cat((invariant_features(state[:6]), state[6],
                          action, normalized_context, self.terrain_relative(state)), -1)'''
after='''        features = invariant_features(state[:6]).clone()
        # Fixed-world terrain needs world heading as well as body-frame velocity.
        # Bounded continuous cues use two yaw-normalized orientation slots.
        # Input width, parameters, norms, integration and original targets stay unchanged.
        R = state[1]
        forward_x, forward_y = R[..., 0, 0], R[..., 1, 0]
        radius = torch.sqrt(forward_x.square()+forward_y.square()+1e-12)
        features[..., 1] += .005*(forward_x/radius-1.)
        features[..., 3] += .005*forward_y/radius
        return torch.cat((features, state[6],
                          action, normalized_context, self.terrain_relative(state)), -1)'''
assert text.count(before)==1
new=text.replace(before,after)
assert new.replace(after,before)==text
ast.parse(new)
(D/'ORIGINAL_augmented_wheel_leg_world_model_v1.py').write_bytes(old_bytes)
(D/'augmented_wheel_leg_world_model_candidate114_v1.py').write_bytes(new.encode('utf-8'))
report=dict(schema='mod4.source114.WM_heading_visibility.preparation.v1',epoch=time.time(),
 source_payload=str(B),source_path=str(old),source_SHA=hashlib.sha256(old_bytes).hexdigest(),
 candidate_SHA=hashlib.sha256(new.encode('utf-8')).hexdigest(),exact_inverse=True,
 scope='ONLY source WM.inputs fixed-world heading visibility. No runtime admission, model read, training or success claim.',
 unchanged='Reward111/actor/critic/WM weights and norm tensors/optimizers/shapes/WM.step/targets/state_error/20s/clock/physics/actions all unchanged; new source only.',
 initial_status='SOURCE_PREPARED_PROOF_PENDING',preserved_original_bytes=True)
(D/'SOURCE114_PREPARATION_AND_EXACT_INVERSE_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(directory=str(D),**report),ensure_ascii=False))
