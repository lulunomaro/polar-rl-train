"""One-pass saved-cycle numerical acceptance; no filesystem or SDK access."""
import math


class CycleAccumulator:
    def __init__(self):
        self.rows = self.partial = 0
        self.complete = []
        self.seen = set()

    def add(self, row):
        assert row["schema"] == "W35_same_uid_sampled_signed_cycle_v1"
        assert isinstance(row["complete_sampled_span"], bool)
        self.rows += 1
        if not row["complete_sampled_span"]:
            self.partial += 1
            return
        keys = ("env_id", "episode_uid", "command_uid", "profile", "first_control", "last_control")
        identity = tuple(row[key] for key in keys)
        assert identity not in self.seen
        self.seen.add(identity)
        assert row["start_observed"] and row["controls"] > 0
        seconds = row["seconds"]
        progress = row["actual_progress_m_s"]
        reference = row["sampled_BODY_reference_progress_m_s"]
        assert all(math.isfinite(value) for value in (seconds, progress, reference))
        assert math.isclose(seconds, row["controls"] * .02, rel_tol=2e-6, abs_tol=1e-5)
        assert row["sampled_signed_turn_rad"] >= 2 * math.pi
        assert math.isclose(progress * seconds, row["actual_projected_displacement_m"],
                            rel_tol=3e-6, abs_tol=3e-6)
        assert isinstance(row["terminal_non_timeout"], bool) and isinstance(row["terminal_timeout"], bool)
        assert row["nominal_world_progress_m_s"] == .5
        self.complete.append(row)

    def metrics(self, rows):
        if not rows:
            return dict(events=0, values=None)
        count = len(rows)
        seconds = sum(row["seconds"] for row in rows)
        errors = [abs(row["actual_progress_m_s"] - .5) for row in rows]
        ordered = sorted(errors)
        return dict(events=count, unique_env_ids=len({row["env_id"] for row in rows}),
                    population_cycle_seconds=seconds,
                    cycle_progress_event_MAE_m_s=sum(errors) / count,
                    cycle_progress_duration_weighted_MAE_m_s=sum(
                        error * row["seconds"] for error, row in zip(errors, rows)) / seconds,
                    cycle_progress_max_abs_error_m_s=max(errors),
                    cycle_progress_event_median_abs_error_m_s=ordered[count // 2],
                    actual_duration_weighted_progress_m_s=sum(
                        row["actual_projected_displacement_m"] for row in rows) / seconds,
                    along_only_within_original_point05_m_s_events=sum(error <= .05 for error in errors),
                    along_only_outside_original_point05_m_s_events=sum(error > .05 for error in errors),
                    integrated_BODY_reference_event_MAE_m_s=sum(abs(
                        row["actual_progress_m_s"] - row["sampled_BODY_reference_progress_m_s"])
                        for row in rows) / count,
                    includes_terminal_events=sum(row["terminal_non_timeout"] or row["terminal_timeout"]
                                                  for row in rows),
                    strict_world_skill_acceptance="UNKNOWN: cross displacement and commanded signed-yaw error not in this producer")

    def finish(self):
        assert self.rows == len(self.complete) + self.partial
        nonterminal = [row for row in self.complete if not
                       (row["terminal_non_timeout"] or row["terminal_timeout"])]
        return dict(rows=self.rows, partial_cycle_events=self.partial,
                    all_complete=self.metrics(self.complete),
                    nonterminal_complete=self.metrics(nonterminal),
                    by_profile={str(key): self.metrics([row for row in self.complete if row["profile"] == key])
                                for key in sorted({row["profile"] for row in self.complete})},
                    skill_graduated=False, cycle_MAE_is_not_instantaneous_velocity_MAE=True,
                    not_a_new_pass_rate_threshold=True,
                    next_necessary_measurements=["same-cycle world cross displacement", "same-cycle commanded signed-yaw integral/error"],
                    raw_model_SDK_training_or_account_write=False)
