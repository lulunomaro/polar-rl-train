"""Pure stdlib CPU counterexamples and protocol candidates, NOT SDK patches.
No imports of the SDK, tasks, torch, models, owner or accounting modules.
The fake cache deliberately models one hypothesis; it is not a runtime receipt.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math


def normalize_wxyz(q):
    norm = math.sqrt(sum(v*v for v in q))
    if not math.isfinite(norm) or norm <= 0:
        raise ValueError('invalid quaternion')
    return tuple(v/norm for v in q)


def xyzw_to_wxyz(q):
    x,y,z,w = q
    return w,x,y,z


def matrix_from_wxyz(q):
    w,x,y,z = normalize_wxyz(q)
    return ((1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)),
            (2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)),
            (2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)))


def gravity_from_xyzw(q):
    # Body->world rotation: R.T @ (0,0,-1) = minus the LAST ROW.
    return tuple(-v for v in matrix_from_wxyz(xyzw_to_wxyz(q))[2])


def pitch_xyzw(angle):
    return 0., math.sin(angle/2), 0., math.cos(angle/2)


def yaw_xyzw(angle):
    return 0., 0., math.sin(angle/2), math.cos(angle/2)


def max_error(a,b):
    return max(abs(x-y) for x,y in zip(a,b))


@dataclass
class SyntheticLazyCache:
    """One timestamp-equality mechanism to falsify a speculative zero-dt fix."""
    pose_xyzw: tuple = (0.,0.,0.,1.)
    sim_stamp: float = 0.
    pose_cache_stamp: float = -1.
    gravity_cache_stamp: float = -1.
    pose_cache: tuple | None = None
    gravity_cache: tuple | None = None
    pose_setter_updates_pose_cache: bool = True
    physics_steps: int = 0
    resets: int = 0
    observation_calls: int = 0
    noise_rng_draws: int = 0
    command_rng_draws: int = 0

    def read_pose(self):
        if self.pose_cache_stamp < self.sim_stamp:
            self.pose_cache = self.pose_xyzw
            self.pose_cache_stamp = self.sim_stamp
        return self.pose_cache

    def read_gravity(self):
        if self.gravity_cache_stamp < self.sim_stamp:
            self.gravity_cache = gravity_from_xyzw(self.read_pose())
            self.gravity_cache_stamp = self.sim_stamp
        return self.gravity_cache

    def write_reset_pose(self,q):
        self.resets += 1
        self.pose_xyzw = q
        if self.pose_setter_updates_pose_cache:
            self.pose_cache = q
            self.pose_cache_stamp = self.sim_stamp
        # Deliberately no derived-gravity invalidation: HYPOTHESIS only.

    def update(self,dt):
        self.sim_stamp += dt

    def invalidate_gravity_only(self):
        self.gravity_cache_stamp = -math.inf

    def invalidate_dependency_closure(self):
        self.pose_cache_stamp = self.gravity_cache_stamp = -math.inf

    def compute_original_observation_once(self):
        self.observation_calls += 1
        self.noise_rng_draws += 1
        return dict(gravity=self.read_gravity(), pose=self.read_pose())


# Exact ROOT-DERIVED omissions in the inspected PhysX source; not a blanket
# reset of every cache, not a list to apply to an unknown backend.
PHYSX_ROOT_DERIVED_CACHE_NAMES = (
    '_projected_gravity_b','_heading_w','_root_link_vel_w','_root_com_pose_w',
    '_root_link_lin_vel_b','_root_link_ang_vel_b',
    '_root_com_lin_vel_b','_root_com_ang_vel_b',
)


def invalidate_validated_physx_root_derived_cache(data, *, live_binding_verified=False):
    """SOURCE-ONLY candidate. Never called on a real SDK object by this audit.
    live_binding_verified must come from an independent actual type/MRO/source
    fingerprint receipt, not from a factory/type-check import or this CPU test.
    Validate every field before mutating any. Preserve data arrays, ProxyArray,
    physical state, timestamp clock, observation history, noise and RNG.
    """
    if live_binding_verified is not True:
        raise RuntimeError('actual live binding receipt missing')
    if getattr(data,'__backend_name__',None) != 'physx':
        raise RuntimeError('unexpected backend')
    if not type(data).__module__.startswith('isaaclab_physx.'):
        raise RuntimeError('unexpected data implementation module')
    stamp = getattr(data,'_sim_timestamp',None)
    if not isinstance(stamp,(int,float)) or not math.isfinite(stamp) or stamp < 0:
        raise RuntimeError('unexpected simulation timestamp')
    buffers = []
    for name in PHYSX_ROOT_DERIVED_CACHE_NAMES:
        buf = getattr(data,name,None)
        if buf is None or not hasattr(buf,'timestamp') or not hasattr(buf,'data'):
            raise RuntimeError('expected TimestampedBufferWarp missing: '+name)
        buffers.append((name,buf))
    before = {name:buf.timestamp for name,buf in buffers}
    for name,buf in buffers:
        buf.timestamp = -1.0
    return dict(invalidated=list(PHYSX_ROOT_DERIVED_CACHE_NAMES),before=before,
                simulation_timestamp_unchanged=data._sim_timestamp,
                extra_physics_steps=0,extra_resets=0,extra_observation_computes=0)


def install_root_state_cache_invalidation_candidate(robot, *, live_binding_verified=False):
    """Instance-only adapter candidate after build_env/before the ONE reset.
    It wraps exactly the deprecated full-state writer called by the examined
    six reset implementations. Other write APIs are NOT silently covered.
    The first call validates fields without altering cache/data or clocks.
    """
    if getattr(robot,'_source_review_root_state_hook_installed',False):
        raise RuntimeError('candidate hook already installed')
    data=robot.data
    if live_binding_verified is not True or getattr(data,'__backend_name__',None) != 'physx':
        raise RuntimeError('actual live PhysX binding receipt missing')
    if not type(data).__module__.startswith('isaaclab_physx.'):
        raise RuntimeError('unexpected data implementation module')
    stamp=getattr(data,'_sim_timestamp',None)
    if not isinstance(stamp,(int,float)) or not math.isfinite(stamp) or stamp < 0:
        raise RuntimeError('unexpected simulation timestamp')
    for name in PHYSX_ROOT_DERIVED_CACHE_NAMES:
        buf=getattr(data,name,None)
        if buf is None or not hasattr(buf,'timestamp') or not hasattr(buf,'data'):
            raise RuntimeError('expected TimestampedBufferWarp missing: '+name)
    original=robot.write_root_state_to_sim
    def wrapped(*args,**kwargs):
        result=original(*args,**kwargs)
        invalidate_validated_physx_root_derived_cache(data,live_binding_verified=True)
        return result
    robot.write_root_state_to_sim=wrapped
    robot._source_review_root_state_hook_installed=True
    return original


def primary_exception_with_cleanup_exit_zero():
    """Replicate Python finally masking, without invoking SDK or a process."""
    try:
        raise AssertionError('original gravity guard failure')
    finally:
        raise SystemExit(0)


def normalized_error_rc(exc):
    if isinstance(exc, KeyboardInterrupt):
        return 130
    if isinstance(exc, SystemExit) and isinstance(exc.code, int) and exc.code != 0:
        return exc.code
    return 1


@dataclass
class CleanupOutcome:
    error_rc: int = 0
    primary_error: str | None = None
    cleanup_events: list = field(default_factory=list)


def preserve_primary_and_close(primary_callable, cleanups):
    """Candidate control flow; no process/SDK/files. Return once AFTER cleanup.
    A successful close's SystemExit(0/None) does not erase an earlier failure.
    Real os._exit is not catchable, so owner must independently check receipts.
    """
    out = CleanupOutcome()
    try:
        primary_callable()
    except BaseException as exc:
        out.error_rc = normalized_error_rc(exc)
        out.primary_error = type(exc).__name__+': '+str(exc)
    for name,close in cleanups:
        try:
            close()
            out.cleanup_events.append((name,'returned'))
        except BaseException as exc:
            expected_zero = isinstance(exc,SystemExit) and exc.code in (None,0)
            out.cleanup_events.append((name,'SystemExit0' if expected_zero else type(exc).__name__))
            if not expected_zero and not out.error_rc:
                out.error_rc = normalized_error_rc(exc)
    return out


def terminal_receipt_decision(returncode, final, worker_error, expected_role):
    """Owner-side candidate independent of accounting; preserves raw returncode.
    Partial finite-window saves may pass execution with target_reached=False;
    this says NOTHING about skill success, 90%, or original acceptance.
    """
    reasons = []
    if returncode != 0:
        reasons.append('NONZERO_PROCESS_RC')
    if worker_error is not None:
        reasons.append('WORKER_ERROR_PRESENT')
    if not isinstance(final,dict):
        reasons.append('FINAL_MISSING_OR_INVALID')
    else:
        if final.get('role') != expected_role:
            reasons.append('FINAL_ROLE_MISMATCH')
        if final.get('passed_execution') is not True:
            reasons.append('FINAL_NOT_EXECUTION_PASS')
        steps = final.get('actual_BPTT_policy_steps')
        if isinstance(steps,bool) or not isinstance(steps,int) or steps < 0:
            reasons.append('FINAL_BPTT_COUNT_INVALID')
        cp = final.get('checkpoint')
        if not isinstance(cp,dict) or cp.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved') is not True:
            reasons.append('COMPLETE_SAVE_RECEIPT_MISSING')
    return dict(returncode=returncode, effective_error=bool(reasons),
                block_pending=bool(reasons), reasons=reasons,
                skill_success=None, accounting_rewrite=False)
