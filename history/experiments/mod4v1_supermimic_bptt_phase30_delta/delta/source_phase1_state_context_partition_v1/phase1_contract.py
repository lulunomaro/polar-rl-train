"""SOURCE-only, stdlib contracts. No sampler, native imports, trainer or migration.
Inputs are named passive-capture records, never a checkpoint/context-vector split.
Synthetic arithmetic success is intentionally insufficient for actual Gate1 admission.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

VERSION = "phase1_state_context_partition_v1"
ROLES = {"E3":122, "W35":119, "CURB_INDEPENDENT113":119, "CURB_PROTECTED878":119,
         "SLOPE135":119, "SLOPE_INDEPENDENT50":119, "E0":117, "E2":117}
QUEUE_FIELDS = {"lag_steps", "episode", "pending", "pending_valid", "issued_tick", "due_tick",
                "applied", "applied_valid", "applied_issue_tick", "first_apply_tick",
                "last_submit_tick", "last_apply_tick"}


class ContractUnknown(ValueError):
    """Required evidence absent/unknown. No zero, hold or reconstructed substitute."""


class ContractViolation(ValueError):
    """Observed values contradict this version's source contract."""


def need(obj, key):
    if not isinstance(obj, dict) or key not in obj or obj[key] is None:
        raise ContractUnknown("UNKNOWN required field: " + str(key))
    value = obj[key]
    if isinstance(value,str) and value.upper() in {"UNKNOWN","MISSING","PENDING"}:
        raise ContractUnknown("UNKNOWN required field: " + str(key))
    return value


def check(condition, message):
    if not condition:
        raise ContractViolation(message)


def exact_keys(obj, expected, name):
    check(isinstance(obj,dict), name + " must be a named mapping")
    missing = set(expected)-set(obj)
    if missing: raise ContractUnknown("UNKNOWN " + name + ": " + ",".join(sorted(missing)))
    check(set(obj) == set(expected), name + " unexpected fields")


def integer(value, name):
    check(type(value) is int, name + " must be an integer, not bool/float")
    return value


def vector(value, width, name):
    check(isinstance(value, (list, tuple)) and len(value) == width, name + " exact width")
    check(all(type(x) in (int, float) and math.isfinite(x) for x in value), name + " finite numeric vector")
    return tuple(value)


def equal_vec(a, b, name, tolerance=1e-6):
    check(len(a) == len(b) and all(abs(x-y) <= tolerance for x, y in zip(a, b)), name + " differs")


def load_schema(path=None):
    p = Path(path) if path else Path(__file__).with_name("partition_schema_v1.json")
    schema = json.loads(p.read_text(encoding="utf-8"))
    validate_schema(schema)
    return schema


def validate_schema(schema):
    check(need(schema, "schema_version") == VERSION, "schema version mismatch")
    check(set(need(schema, "layouts")) == set(ROLES), "exact eight roles required")
    check(need(schema, "clocks") == {"physics_us":2500, "control_us":20000,
          "feedback_sample_us":10000, "physics_callbacks_per_control":8,
          "samples_per_control":2, "sample_offsets_physics_ticks":[4,8],
          "bridge_f_unit":"50Hz control step;seconds=f*.02; separate from100Hz sample tick and global physics tick",
          "contact_bin_us":5000}, "fixed clocks changed")
    classes = set(need(schema, "classifications"))
    for role, dimension in ROLES.items():
        layout = schema["layouts"][role]
        check(need(layout, "context_dim") == dimension and need(layout, "actor_dim") == 35, "legacy dimension changed")
        offset, seen = 0, set()
        for field in need(layout, "fields"):
            name = need(field, "name")
            width = integer(need(field, "width"), name)
            check(name not in seen and width > 0, "duplicate/empty named field")
            seen.add(name)
            check(need(field, "offset") == offset and need(field, "end_exclusive") == offset+width, "offset gap/overlap")
            offset += width
            check(set(need(field, "classes")) <= classes, "unrecognized class")
            for key in ("native_unit", "canonical_unit", "legacy_stored_unit", "source", "time_semantics"):
                need(field, key)
            check((name == "actor35_original") == (need(field, "audience") == "ACTOR"), "actor/privileged leak")
            check(not ("STATIC_DR" in field["classes"] and name in ("applied_torque", "recovery_age", "recovery_stable", "command_time_left")), "dynamic value called static")
        check(offset == dimension, "layout total width")
        actor = layout["fields"][0]
        check(actor["name"] == "actor35_original" and actor["width"] == 35 and actor.get("clean") is False, "raw35 is not clean")
    offset = 0
    for field in need(schema, "raw35_fields"):
        check(field["offset"] == offset and field["clean"] is False, "raw35 schema changed")
        offset += field["width"]
        check(field["end_exclusive"] == offset, "raw35 offset mismatch")
    check(offset == 35, "raw35 width")
    missing = {f["name"]: f for f in need(schema, "required_extended_fields")}
    for name in ("mild_motor_episode_scale_legs", "mild_motor_episode_scale_wheels", "wheel_mu", "sensor_leg_encoder_bias",
                 "action_queue.legs.issued_tick", "action_queue.wheels.pending_valid", "leg_pos.clean_at_sample", "leg_pos.noise_used"):
        check(name in missing and missing[name]["offset"] is None, "missing field assigned fake legacy offset")
    check(schema["gate1"]["admitted"] is False and schema["evidence_limits"]["exact"] is False, "SOURCE artifact cannot self-admit")
    return {"schema_valid":True, "actual_sdk_pass":False, "exact":False}


def validate_named_context(role, named, schema):
    """Validate already-named legacy capture; no vector slicing/conversion/repacking."""
    if role not in schema["layouts"]:
        raise ContractUnknown("UNKNOWN role: " + str(role))
    fields = schema["layouts"][role]["fields"]
    check(isinstance(named, dict), "named mapping required; old flat vector not accepted")
    expected = {f["name"] for f in fields}
    missing = expected - set(named)
    if missing:
        raise ContractUnknown("UNKNOWN named fields: " + ",".join(sorted(missing)))
    check(set(named) == expected, "unexpected named context field")
    values = {f["name"]:vector(need(named, f["name"]), f["width"], f["name"]) for f in fields}
    actor = values.pop("actor35_original")
    return {"actor":actor, "privileged_only":values, "actual_sdk_pass":False, "exact":False}


def validate_actor_view(raw_named, original_actor35, schema):
    """Only concatenate original named actor terms; never consumes privileged state."""
    expected = {f["name"] for f in schema["raw35_fields"]}
    check(isinstance(raw_named, dict) and set(raw_named) == expected, "actor named terms exact")
    terms = {f["name"]:vector(need(raw_named, f["name"]), f["width"], f["name"]) for f in schema["raw35_fields"]}
    check(all(x == 0 for x in terms["wheel_pos_slots"]), "wheel positions are structural zero")
    mode = terms["mode_onehot"]
    check(all(x in (0,1) for x in mode) and sum(mode) == 1, "mode onehot")
    actor = tuple(x for f in schema["raw35_fields"] for x in terms[f["name"]])
    equal_vec(actor, vector(original_actor35, 35, "original_actor35"), "original actor35", tolerance=0)
    return actor


def validate_sensor_pair(samples, start_physics_tick, episode, schema, previous=None):
    """Validate captured MID/END only. Does not derive any clean/noise sample."""
    integer(start_physics_tick, "start_physics_tick"); integer(episode, "episode")
    check(start_physics_tick >= 0 and start_physics_tick % 4 == 0, "sample-clock alignment")
    if isinstance(samples,list) and len(samples) < 2:
        raise ContractUnknown("UNKNOWN missing original100Hz MID/END sample")
    check(isinstance(samples, list) and len(samples) == 2, "both original100Hz MID/END required")
    prior = previous
    for sample, offset in zip(samples, (4,8)):
        tick = (start_physics_tick + offset)//4
        check(need(sample,"physics_tick") == start_physics_tick+offset and need(sample,"sample_tick") == tick, "100Hz physics/sample clock")
        check(need(sample,"episode") == episode, "sample episode mismatch")
        channels = need(sample,"channels")
        exact_keys(channels,schema["sensor_channels"],"five original sensor groups")
        for name, spec in schema["sensor_channels"].items():
            c = channels[name]; width = spec["width"]
            check(need(c,"profile") == spec["profile"], "source sensor profile mismatch")
            clean = vector(need(c,"clean_at_sample"),width,name+" clean")
            noise = vector(need(c,"noise_used"),width,name+" actual noise-used")
            bias = vector(need(c,"episode_bias"),width,name+" episode bias")
            for x in noise: check(abs(x) <= spec["noise_uniform_bound"]+1e-8, "actual noise exceeds source profile")
            for x in bias: check(abs(x) <= spec["episode_bias_bound"]+1e-8, "actual bias exceeds source profile")
            noisy = vector(need(c,"noisy_before_queue"),width,name+" noisy")
            equal_vec(noisy,tuple(x+n+b for x,n,b in zip(clean,noise,bias)),name+" clean+noise+bias")
            equal_vec(vector(need(c,"cur"),width,name+" cur"),noisy,name+" current cache")
            old = integer(need(c,"previous_last"),name+" previous_last")
            initial = old < 0
            check(need(c,"last") == tick and (initial or old == tick-1), "Skipped/reversed feedback sample clock")
            check(type(need(c,"ready")) is bool and c["ready"] is (not initial), "feedback warmup flag")
            delay = integer(need(c,"delay_steps"),name+" delay")
            check(delay in (0,1), "original100Hz delay must be0/1")
            prev_cur = vector(need(c,"previous_cur"),width,name+" previous_cur")
            if not initial:
                if prior is None: raise ContractUnknown("UNKNOWN prior100Hz sample; no endpoint reconstruction")
                check(need(prior,"episode") == episode and need(prior,"sample_tick") == old, "previous sample episode/tick")
                pc = need(need(prior,"channels"),name)
                equal_vec(prev_cur,vector(need(pc,"cur"),width,name+" prior cur"),name+" queue linkage",tolerance=0)
                equal_vec(bias,vector(need(pc,"episode_bias"),width,name+" prior bias"),name+" episode bias stability",tolerance=0)
                check(need(pc,"delay_steps") == delay, "episode delay changed")
            selected = prev_cur if delay == 1 and not initial else noisy
            out = vector(need(c,"out"),width,name+" out")
            equal_vec(out,selected,name+" queued output")
            selected_tick = old if delay == 1 and not initial else tick
            check(need(c,"selected_sample_tick") == selected_tick and need(c,"actual_age_us") == (tick-selected_tick)*10000, "feedback selected age")
            equal_vec(vector(need(c,"actor_stored"),width,name+" scaled out"),tuple(x*spec["manager_scale"] for x in out),name+" manager scaling")
            before = integer(need(c,"draw_count_before"),name+" draw before")
            after = integer(need(c,"draw_count_after"),name+" draw after")
            due = integer(need(c,"due_environment_count"),name+" due environment count")
            check(before >= 0 and due >= 1 and after-before == due, "natural sample draw-count mismatch")
            check(need(c,"noise_cache_last_after") == tick, "actual noise cache not for this sample")
            check(need(c,"probe_rng_before") == need(c,"probe_rng_after"), "observer altered private RNG")
        prior = sample
    return {"two_samples_valid":True,"actual_sdk_pass":False,"exact":False}


def validate_action_trace(capture, start_physics_tick, episode, schema):
    """Check eight captured apply ticks for both groups; no actuator execution."""
    integer(start_physics_tick,"start_physics_tick"); integer(episode,"episode")
    exact_keys(capture,schema["action_groups"],"both action groups")
    for group,width in schema["action_groups"].items():
        item = capture[group]; before = need(item,"before_submit")
        target = vector(need(item,"submitted_target"),width,group+" submitted")
        frames = need(item,"apply_frames")
        check(isinstance(frames,list) and len(frames) == 8, "eight physical apply receipts required")
        exact_keys(before,QUEUE_FIELDS,"full before-submit queue state")
        lag = integer(need(before,"lag_steps"),"lag_steps")
        check(lag in (0,1,2) and need(before,"episode") == episode, "action episode/lag")
        check(need(before,"last_submit_tick") in (-1,start_physics_tick-8), "policy submit spacing")
        check(need(before,"pending_valid") is False, "unresolved previous pending command")
        check(need(before,"last_apply_tick") in (-1,start_physics_tick-1), "physical pre-submit clock")
        prior = before
        for i,frame in enumerate(frames):
            tick = start_physics_tick+i; q = need(frame,"queue")
            exact_keys(q,QUEUE_FIELDS,"full action queue state")
            for k in QUEUE_FIELDS - {"pending","applied","pending_valid","applied_valid"}:
                integer(need(q,k),group+"."+k)
            check(q["lag_steps"] == lag and q["episode"] == episode, "action static reset identity")
            check(q["issued_tick"] == start_physics_tick and q["due_tick"] == start_physics_tick+lag and q["last_submit_tick"] == start_physics_tick, "action issue/due/submit")
            check(q["last_apply_tick"] == tick, "physical callback clock")
            equal_vec(vector(q["pending"],width,"pending"),target,"submitted pending",tolerance=0)
            fresh = i >= lag
            check(type(q["pending_valid"]) is bool and q["pending_valid"] is (not fresh), "pending validity transition")
            check(type(q["applied_valid"]) is bool, "applied_valid boolean")
            expected = target if fresh else vector(prior["applied"],width,"prior applied")
            equal_vec(vector(q["applied"],width,"applied"),expected,"held/applied target",tolerance=0)
            if fresh:
                check(q["applied_valid"] is True and q["applied_issue_tick"] == start_physics_tick and q["first_apply_tick"] == start_physics_tick+lag, "first-transition provenance")
            else:
                check(all(q[k] == prior[k] for k in ("applied_valid","applied_issue_tick","first_apply_tick")), "pre-due previous target changed")
            latency = (q["first_apply_tick"]-q["applied_issue_tick"])*2500 if q["applied_valid"] else -1
            age = (tick-q["applied_issue_tick"])*2500 if q["applied_valid"] else -1
            check(need(frame,"first_transition_delay_us") == latency and need(frame,"held_command_sample_age_us") == age, "first latency vs held age")
            equal_vec(vector(need(frame,"articulation_target_readback"),width,"target readback"),expected,"actual articulation target")
            prior = q
    return {"eight_apply_ticks_valid":True,"actual_sdk_pass":False,"exact":False}


def validate_static_episode(before, after, schema, role):
    names = {f["name"] for f in schema["layouts"][role]["fields"] if "STATIC_DR" in f["classes"]}
    names |= {"mild_motor_episode_scale_legs","mild_motor_episode_scale_wheels","wheel_mu","mild_nominal","sensor_leg_encoder_bias"}
    check(need(before,"episode") == need(after,"episode"), "same-episode comparison required; reset has separate receipt")
    for name in names:
        if need(before,name) != need(after,name): raise ContractViolation("episode static changed: "+name)
    return True


def exact_gate(schema, receipt=None):
    """Hard evidence gate. V1 validates source/synthetic only and never self-admits SDK.
A future live verifier must separately establish provenance/role coverage, not set a bool.
"""
    validate_schema(schema)
    if receipt is None: raise ContractUnknown("UNKNOWN Gate1 passive capture receipt")
    if need(receipt,"evidence_kind") != "ACTUAL_ORIGINAL100HZ_PASSIVE_CAPTURE":
        raise ContractUnknown("UNKNOWN actualSDK: SOURCE/synthetic evidence is not live capture")
    raise ContractUnknown("UNKNOWN Gate1: independent live provenance verifier not installed in SOURCE v1")


def verify_local_schema_manifest(directory=None):
    here = Path(directory) if directory else Path(__file__).resolve().parent
    schema = load_schema(here/"partition_schema_v1.json")
    blob = (here/"source_manifest.json").read_bytes()
    check(hashlib.sha256(blob).hexdigest() == need(schema,"source_manifest_sha256"), "source manifest digest mismatch")
    manifest = json.loads(blob)
    return {"source_count":len(need(manifest,"sources")),"schema_sha256":hashlib.sha256((here/"partition_schema_v1.json").read_bytes()).hexdigest(),"manifest_sha256":hashlib.sha256(blob).hexdigest(),"actual_sdk_pass":False,"exact":False}
