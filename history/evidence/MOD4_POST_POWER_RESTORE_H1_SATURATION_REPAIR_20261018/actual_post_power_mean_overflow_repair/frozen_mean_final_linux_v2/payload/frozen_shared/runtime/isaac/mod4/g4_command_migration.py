"""Explicit source identity view, then real new assignment; original loader stays strict."""
import copy
from types import SimpleNamespace
from retention_command_state import validate,same

def restore_source_then_bind_WAVE50(term,state,source_assignment_sha):
 validate(state,term.num_envs)
 assert state['assignment_sha256']==source_assignment_sha and len(source_assignment_sha)==64
 current=term._env.scene.terrain.retention_assignment_sha
 assert current!=source_assignment_sha,'New scope must disclose a changed actual assignment'
 # This shallow view shares only the state fields and generator with the live term.
 # It is never installed in a manager, stepped, used as physics, or fed to actor/gate.
 view=copy.copy(term)
 view._env=SimpleNamespace(num_envs=term.num_envs,device=term.device,scene=SimpleNamespace(terrain=SimpleNamespace(retention_assignment_sha=source_assignment_sha)))
 view.load_state_retention(state)  # exact, unmodified original admission under source identity
 restored=view.state_dict_retention();assert same(restored,state)
 rebound=term.state_dict_retention()
 expected=dict(state,assignment_sha256=current)
 assert same(rebound,expected),'Only the disclosed assignment identity may differ before fresh reset'
 assert same(rebound['rng'],state['rng']) and term._env.scene.terrain.retention_assignment_sha==current
 return dict(source_assignment_sha256=source_assignment_sha,new_actual_assignment_sha256=current,
  original_strict_loader_reused_under_source_identity=True,source_command_state_and_private_RNG_exact=True,
  explicit_changed_assignment_binding=True,source_identity_view_not_a_physical_scene=True,
  old_loader_or_named_stream_schema_not_relaxed=True,old_modes_not_claimed_new_support_before_reset=True)
