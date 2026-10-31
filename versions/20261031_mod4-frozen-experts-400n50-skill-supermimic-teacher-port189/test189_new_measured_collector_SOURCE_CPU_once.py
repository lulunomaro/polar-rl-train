"""Separate new collector source purpose; never reopens the teacher model."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
from pathlib import Path
import json
import time
import traceback
import torch
from expert_teacher_port189 import ACTION_ORDER, PairIdentity
from measured_teacher_collector189 import MeasuredTeacherCollector

B = Path(__file__).resolve().parent
R = B / "reports"
with (R / "COLLECTOR189_SOURCE_CPU_STARTED_CONSUMED.json").open("x", encoding="utf8") as file:
    json.dump(dict(epoch=time.time(), purpose="new collector boundaries, source fixtures only",
                   models=0, raw=0, SDK=0, CUDA=0, remote=0), file)
report = dict(passed=False, groups=[], rejects=[], errors=[], models_opened=0,
              raw_opened=0, SDK_imports=0, actual_physical_rollout=False)
try:
    rng = torch.random.get_rng_state().clone()
    identity = PairIdentity("SYNTHETIC_NOT_RUNTIME", "E0", "a" * 64, "b" * 64,
                            ACTION_ORDER, tuple(str(i) for i in range(30)))
    before = dict(state127=torch.ones(2, 127), xi31=torch.ones(2, 31),
                  policy35=torch.ones(2, 35), teacher_raw6=torch.zeros(2, 6),
                  issued6=torch.zeros(2, 6), previous_issued6=torch.zeros(2, 6),
                  episode_id=torch.tensor([4, 5]), policy_control=torch.zeros(2, dtype=torch.long),
                  time_us=torch.zeros(2, dtype=torch.long))
    terminal = dict(state127_pre_reset=torch.ones(2, 127) * 2,
                    episode_id_for_terminal=torch.tensor([4, 5]),
                    policy_control=torch.ones(2, dtype=torch.long),
                    time_us=torch.full((2,), 20000, dtype=torch.long),
                    done=torch.tensor([True, False]),
                    physics_time_us8=(torch.arange(1, 9) * 2500)[None].expand(2, -1).clone(),
                    feedback_time_us2=(torch.arange(1, 3) * 10000)[None].expand(2, -1).clone(),
                    processed_targets6_at8_callbacks=torch.ones(2, 8, 6))
    collector = MeasuredTeacherCollector(identity, maximum_pairs=1)
    collector.begin_original_decision(before)
    before["state127"].zero_()  # Natural runtime reuses its buffers.
    collector.complete_before_reset(terminal)
    terminal["state127_pre_reset"].zero_()
    assert collector.completed() == 1
    pair = collector.finish()[0]
    assert (pair["native"]["s"] == 1).all() and (pair["native"]["s1"] == 2).all()
    assert pair["native"]["done"].tolist() == [True, False]
    report["groups"].append("copies_original_buffers_and_keeps_terminal_pre_reset")

    def reject(name, call):
        try:
            call()
        except ValueError as error:
            report["rejects"].append(dict(name=name, error=str(error)))
        else:
            raise AssertionError(name)
    empty = MeasuredTeacherCollector(identity, maximum_pairs=1)
    reject("finish_without_transitions", empty.finish)
    reject("terminal_without_decision", lambda: empty.complete_before_reset(terminal))
    empty.begin_original_decision(before)
    reject("second_decision_before_terminal", lambda: empty.begin_original_decision(before))
    reject("unfinished_decision_is_not_dataset", empty.finish)
    wrong = dict(terminal, episode_id_for_terminal=torch.tensor([5, 6]))
    reject("autoreset_endpoint_rejected", lambda: empty.complete_before_reset(wrong))
    assert empty.completed() == 0
    # Original pending decision is retained after refusal, never silently consumed.
    reject("refused_pair_stays_pending", empty.finish)
    empty.complete_before_reset(terminal)
    reject("declared_bound_cannot_extend", lambda: empty.begin_original_decision(before))
    report["groups"].append("refusals_preserve_pair_identity_and_declared_bounds")
    assert torch.equal(rng, torch.random.get_rng_state()) and not torch.cuda.is_initialized()
    report["RNG_unchanged"] = True
    report["passed"] = True
except BaseException:
    report["errors"].append(traceback.format_exc())
finally:
    report["epoch"] = time.time()
    with (R / "ROOT189_MEASURED_COLLECTOR_SOURCE_CPU_RETURNED_ACTUAL.json").open("x", encoding="utf8") as file:
        json.dump(report, file, indent=2)
    print(json.dumps(report))
raise SystemExit(0 if report["passed"] else 1)
