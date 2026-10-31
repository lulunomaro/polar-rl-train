"""One newly declared E0 checkpoint read for the actual teacher-port component."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
from pathlib import Path
import hashlib
import io
import json
import time
import traceback
import torch
from expert_teacher_port189 import (
    ACTION_ORDER, FrozenPPO35Teacher, PairIdentity,
    teacher_clipped_command, teacher_warmstart_loss, validate_measured_pair,
)

B = Path(__file__).resolve().parent
R = B / "reports"
protocol_path = R / "E0_189_NEW_CPU_TEACHER_PORT_READ_ONCE_ADMISSION_FROZEN.json"
protocol_raw = protocol_path.read_bytes()
protocol = json.loads(protocol_raw)
start = time.time()
counts = dict(checkpoint_byte_opens=0, checkpoint_full_forward_byte_passes=0,
              checkpoint_decodes=0, deterministic_source_CPU_probe_rows=0,
              old_raw_NPZ_opens=0, normal86_witness_opens=0,
              SDK_imports=0, remote_connections=0, CUDA=0, optimizer_steps=0)
with (R / "E0_189_CPU_TEACHER_PORT_STARTED_CONSUMED.json").open("x", encoding="utf8") as file:
    json.dump(dict(epoch=start, protocol_SHA=hashlib.sha256(protocol_raw).hexdigest()), file)
result = dict(epoch=start, passed=False, errors=[], groups=[], rejects=[], counts=counts,
              scope="Actual saved E0 teacher CPU inference plus synthetic pair/loss component; not SDK, student training or skill acceptance")

def group(name, details):
    result["groups"].append(dict(name=name, passed=True, details=details))

def refuses(name, call):
    try:
        call()
    except ValueError as error:
        result["rejects"].append(dict(name=name, original_error=str(error)))
    else:
        raise AssertionError("Expected refusal: " + name)

try:
    assert protocol["expert"] == "E0" and counts == {key: 0 for key in counts}
    assert not torch.cuda.is_initialized()
    torch.set_num_threads(2)
    rng = torch.random.get_rng_state().clone()
    source = protocol["source"]
    with Path(source["path"]).open("rb") as file:
        counts["checkpoint_byte_opens"] += 1
        raw = file.read()
        counts["checkpoint_full_forward_byte_passes"] += 1
    assert len(raw) == source["bytes"] and hashlib.sha256(raw).hexdigest() == source["SHA"]
    checkpoint = torch.load(io.BytesIO(raw), map_location="cpu", weights_only=False)
    counts["checkpoint_decodes"] += 1
    del raw
    receipt = json.loads(Path(protocol["original_whole_CPU_receipt"]).read_text("utf-8-sig"))
    actor = checkpoint["actor_state_dict"]
    before = {key: value.clone() for key, value in actor.items()}
    for fingerprint in receipt["review"]["new_final_tensor_fingerprints"]:
        prefix = "/actor_state_dict/"
        if fingerprint["path"].startswith(prefix):
            value = actor[fingerprint["path"][len(prefix):]]
            data = value.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()
            assert list(value.shape) == fingerprint["shape"]
            assert str(value.dtype) == fingerprint["dtype"]
            assert hashlib.sha256(data).hexdigest() == fingerprint["SHA"]
    teacher = FrozenPPO35Teacher(actor)
    assert {int(row["step"]) for row in checkpoint["optimizer_state_dict"]["state"].values()} == {641200}
    group("actual_frozen_E0_identity_and_original35_ELU_layers",
          dict(SHA=source["SHA"], actor35=True, savedSTD6=True, original_Adam=641200))

    # Deterministic scaled-coordinate probes; these are not physical MOD4 states.
    # Zero + +/- each of 35 input coordinates + one finite mixed input = 72 rows.
    obs = torch.cat((torch.zeros(1, 35), torch.eye(35) * 0.1,
                     -torch.eye(35) * 0.1, torch.linspace(-0.1, 0.1, 35)[None]), 0)
    mean = teacher.mean(obs)
    counts["deterministic_source_CPU_probe_rows"] = len(obs)
    assert mean.shape == (72, 6) and torch.isfinite(mean).all() and not mean.requires_grad
    labels = teacher_clipped_command(mean)
    assert torch.equal(labels, mean.clamp(-6, 6))
    assert torch.equal(teacher.saved_std, actor["distribution.std_param"])
    group("actual_teacher_deterministic_CPU_labels",
          dict(rows=72, wrapper="original clip6 only", observation_reconstruction=False,
               source_CPU_GPU_parity_not_yet_proved=True, physical_domain_claim=False))

    same = labels.clone().requires_grad_()
    loss = teacher_warmstart_loss(same, mean)
    assert float(loss) == 0
    loss.backward()
    assert torch.equal(same.grad, torch.zeros_like(same))
    shifted = (labels + 0.3).requires_grad_()
    teacher_warmstart_loss(shifted, mean).backward()
    assert torch.isfinite(shifted.grad).all() and (shifted.grad > 0).all()
    assert all(not value.requires_grad for pair in teacher.layers for value in pair)
    group("student_supervision_gradient_and_teacher_frozen",
          dict(exact_label_loss=0, gradient_only_student=True, optimizer_steps=0))

    outside = torch.tensor([[8., -8., 9., -9., 7., -7.]], requires_grad=True)
    target = torch.zeros_like(outside, requires_grad=True)
    teacher_warmstart_loss(outside, target).backward()
    assert (outside.grad.abs() > 0).all() and target.grad is None
    assert torch.equal(outside.grad.sign(), outside.sign())
    group("outside_clip_student_gradient_preserved",
          dict(no_clipped_student_zero_gradient=True, teacher_gradient_absent=True))

    batch = 3
    times = torch.tensor([0, 20000, 60000], dtype=torch.int64)
    before_pair = dict(state127=torch.arange(batch * 127, dtype=torch.float32).reshape(batch, 127) / 100,
                       xi31=torch.zeros(batch, 31), policy35=obs[:batch].clone(),
                       teacher_raw6=mean[:batch].clone(), issued6=labels[:batch].clone(),
                       previous_issued6=torch.zeros(batch, 6),
                       episode_id=torch.tensor([5, 11, 7]), policy_control=torch.tensor([0, 1, 3]),
                       time_us=times)
    terminal = dict(state127_pre_reset=before_pair["state127"] + 0.1,
                    episode_id_for_terminal=before_pair["episode_id"].clone(),
                    policy_control=before_pair["policy_control"] + 1,
                    time_us=times + 20000, done=torch.tensor([False, True, False]),
                    physics_time_us8=times[:, None] + torch.arange(1, 9) * 2500,
                    feedback_time_us2=times[:, None] + torch.arange(1, 3) * 10000,
                    processed_targets6_at8_callbacks=torch.zeros(batch, 8, 6))
    identity = PairIdentity("SYNTHETIC_SOURCE_UNIT_NOT_A_REAL_RUN", "E0", source["SHA"],
                            "1" * 64, ACTION_ORDER, tuple("joint_" + str(i) for i in range(30)))
    native = validate_measured_pair(identity, before_pair, terminal)
    assert native["s1"] is terminal["state127_pre_reset"] and native["done"][1]
    assert native["teacher_policy35"] is before_pair["policy35"]
    group("50Hz_native_pair_terminal_queue_clock_contract",
          dict(policy_us=20000, physics_us=2500, callbacks=8, feedback_samples=2,
               native127_plus_xi31=True, real_runtime_collector_pending=True))

    def bad_terminal(key, value):
        return validate_measured_pair(identity, before_pair, dict(terminal, **{key: value}))
    refuses("old100Hz_endpoint_not50Hz", lambda: bad_terminal("time_us", times + 10000))
    refuses("postreset_episode_mixing", lambda: bad_terminal("episode_id_for_terminal", before_pair["episode_id"] + 1))
    refuses("missing_callback", lambda: bad_terminal("physics_time_us8", terminal["physics_time_us8"][:, :7]))
    refuses("missing_feedback", lambda: bad_terminal("feedback_time_us2", terminal["feedback_time_us2"][:, :1]))
    refuses("missing_real_queue_targets", lambda: validate_measured_pair(identity, before_pair,
             {key: value for key, value in terminal.items() if key != "processed_targets6_at8_callbacks"}))
    refuses("changed_action_order", lambda: validate_measured_pair(
        PairIdentity(identity.run_id, "E0", identity.teacher_SHA, identity.runtime_SHA,
                     ACTION_ORDER[::-1], identity.joint_names30), before_pair, terminal))
    refuses("unclipped_teacher_issue", lambda: validate_measured_pair(identity,
             dict(before_pair, issued6=labels[:batch] + 1), terminal))
    refuses("guessed_policy_from_state", lambda: teacher.mean(torch.zeros(1, 127)))
    refuses("nonfinite_policy", lambda: teacher.mean(torch.full((1, 35), float("nan"))))
    refuses("wrong_actor_keys", lambda: FrozenPPO35Teacher(dict(actor, made_up=torch.zeros(1))))
    group("necessary_negative_data_and_teacher_input_tests", dict(rejects=len(result["rejects"])))

    assert all(torch.equal(actor[key], value) for key, value in before.items())
    assert torch.equal(rng, torch.random.get_rng_state())
    assert not torch.cuda.is_initialized() and counts == protocol["allowed"]
    group("original_teacher_STD_RNG_and_read_counts_unchanged", dict(RNG_unchanged=True,
          CUDA_uninitialized=True, source_actor_unchanged=True, counted_reads=counts.copy()))
    result["passed"] = True
except BaseException:
    result["errors"].append(traceback.format_exc())
finally:
    result["returned_epoch"] = time.time()
    result["wall_seconds"] = time.time() - start
    result["new_expert_learning_started"] = False
    result["physical_skill_accepted"] = False
    result["complete_SuperMimic_conversion"] = False
    path = R / "ROOT189_E0_NEW_CPU_TEACHER_PORT_RETURNED_ACTUAL.json"
    with path.open("x", encoding="utf8") as file:
        json.dump(result, file, indent=2)
    print(json.dumps(dict(passed=result["passed"], groups=len(result["groups"]),
                         rejects=len(result["rejects"]), counts=counts, report=str(path),
                         errors=result["errors"])))
raise SystemExit(0 if result["passed"] else 1)
