"""Serialize already-read, actually named native poses even when a cached buffer is not exposed."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;s=(D/'worker_e0_mimic_native_diagnostic_v1.py').read_text(encoding='utf8');out=D/'worker_e0_mimic_native_diagnostic_v2.py';assert not out.exists()
a="""                row['pairs'][a] = pair
                continue
"""
b="""                bn = orders['bodies']['names']
                if bn is not None and len(bn) == poses.shape[1] and a in bn and b in bn:
                    na = poses[:, bn.index(a), 3:7][:, [3,0,1,2]]
                    nb = poses[:, bn.index(b), 3:7][:, [3,0,1,2]]
                    qa = torch.tensor(contract['bodies'][a]['neutral_quat_wxyz'], device=env.device, dtype=na.dtype)
                    qb = torch.tensor(contract['bodies'][b]['neutral_quat_wxyz'], device=env.device, dtype=na.dtype)
                    authored = 2 * torch.acos((qa*qb).sum().abs().clamp(max=1.))
                    neutral = mul(conjugate(qb), qa)
                    nr = mul(conjugate(nb), na)
                    ne = (2*torch.acos((na*nb).sum(-1).abs().clamp(max=1.)) - authored).abs()
                    pair.update(status='named_native_observed_cached_unknown',
                        native_original_scalar_error_max_rad=maximum(ne),
                        native_original_scalar_first_episode_max_rad=maximum(ne, live),
                        native_relative_to_neutral_max_rad=maximum(angular(nr, neutral)),
                        native_body_quaternion_norm_deviation_max=maximum(torch.stack((na.norm(dim=-1)-1,nb.norm(dim=-1)-1)).abs()))
                    pair_samples[a] = dict(native_body_a_wxyz=plain(na[:2]),native_body_b_wxyz=plain(nb[:2]),
                        native_relative_wxyz=plain(nr[:2]),neutral_relative_wxyz=plain(neutral),
                        native_original_scalar_error_rad=plain(ne[:2]),cached_comparison='unknown_not_zero')
                else:
                    pair['native_status'] = 'unknown actual native body order; no index guess'
                row['pairs'][a] = pair
                continue
"""
assert s.count(a)==1;s=s.replace(a,b);ast.parse(s);compile(s,str(out),'exec');out.write_text(s,encoding='utf8',newline='\n');print('One native-only serialization branch; same existing getter tensors/control/term/reset/physics/RNG; cached unknown remains explicit')
