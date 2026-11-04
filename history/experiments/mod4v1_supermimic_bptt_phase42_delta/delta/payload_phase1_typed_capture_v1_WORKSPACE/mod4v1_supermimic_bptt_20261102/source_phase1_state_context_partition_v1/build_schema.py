"""Build a SOURCE-only named-field audit; never imports the native task.
Reads a fixed allowlist of source and published STARTUP metadata. Writes here only.
No torch/SDK, model, replay, JSONL, native execution, RNG, budget or lock access.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ROLES = ("E3", "W35", "CURB_INDEPENDENT113", "CURB_PROTECTED878", "SLOPE135", "SLOPE_INDEPENDENT50", "E0", "E2")
BASE = "discovery/reward_command_audit_v1"
BRIDGE = "source_runtime/native_supermimic_bridge.py"
WORKER = "source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py"
CANDIDATE = "source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/command_tracking_torch_candidate_v1.py"
ADMISSION = "reports/ACTUAL_A1_NATIVE_V6_ADMISSION2_20261102_232709/CLOSED_RESULT.json"
ENTRIES = {"E3":"train_mod4v1_e3.py", "W35":"train_mod4v1_w35.py", "E0":"train_mod4v1_e0.py", "E2":"train_mod4v1_e2.py", "CURB_INDEPENDENT113":"train_independent_owned_axis_v1.py", "CURB_PROTECTED878":"train_host72_backend_admission_v1.py", "SLOPE135":"train_slope5_snapshot_reviewed_resume_ppo.py", "SLOPE_INDEPENDENT50":"train_independent_owned_axis_v1.py"}
CHAINS = {
 "E0":["chassis_pd_training_env"],
 "E2":["e2_h1_flat_environment_v1", "chassis_pd_training_env"],
 "E3":["e3_recovery_runtime_v1", "chassis_pd_training_env"],
 "W35":["learning208_v3", "evidence208_v3", "base_learning208_v3", "terrain208_v3", "chassis_pd_training_env"],
}
for role in ("CURB_INDEPENDENT113", "CURB_PROTECTED878", "SLOPE135", "SLOPE_INDEPENDENT50"):
    CHAINS[role] = ["retention_learning_env", "e1_reset_evidence_training_env", "e1_terrain_training_env", "e1_terrain_runtime", "chassis_pd_training_env"]
TAIL = ["gas_damping_training_env", "spring_pressure_training_env", "action_delay_training_env", "feedback_delay_runtime", "mod4_env"]
COMMON = ["mod4_task", "feedback_delay_mild", "sensor_a0_runtime", "sensor_mild_math", "action_delay_physics_queue", "action_delay_sdk_adapter", "spring_pressure_component", "gas_damping_factor", "chassis_com_component", "explicit_pd_component", "mild_dr", "contact_capture", "physics_clock"]
CLASSIFICATIONS = ["STATIC_DR", "DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE", "SENSOR_CLEAN", "SENSOR_NOISE", "SENSOR_DELAY_QUEUE", "EXOGENOUS_COMMAND_CLOCK", "TASK_PHASE", "ACTOR_VISIBLE", "UNKNOWN"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_allowlisted(path: str) -> bytes:
    p = ROOT / path
    if p.suffix not in (".py", ".json", ".md"):
        raise RuntimeError("Source extension outside allowlist")
    if p.suffix == ".json" and path != ADMISSION and not path.endswith("E1_CANONICAL_SOURCE_METADATA.json"):
        raise RuntimeError("JSON outside published STARTUP/source metadata allowlist")
    return p.read_bytes()


def save_new(name: str, value) -> None:
    target = HERE / name
    text = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != text:
            raise RuntimeError("Frozen output differs: " + name)
        return
    target.write_text(text, encoding="utf-8")


def original(role: str, file: str, lines: str = "") -> str:
    return f"{BASE}/{role}/runtime/isaac/mod4/{file}" + (":" + lines if lines else "")


def build() -> dict:
    sources = {}
    def include(path):
        blob = read_allowlisted(path)
        sources[path] = {"sha256": digest(blob), "bytes": len(blob)}
        return blob
    include(BRIDGE)
    include(WORKER)
    include(CANDIDATE)
    if not sources[BRIDGE]["sha256"].startswith("8211"):
        raise RuntimeError("Pinned bridge prefix differs")
    if not sources[WORKER]["sha256"].startswith("7c4298"):
        raise RuntimeError("Pinned worker prefix differs")
    if sources[CANDIDATE]["sha256"] != "bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223":
        raise RuntimeError("Raw35 wrapper source identity differs")
    admission = json.loads(include(ADMISSION))
    startup = {row["role"]: row for row in admission["rows"]}
    bindings = {}
    for role in ROLES:
        mods = [ENTRIES[role].removesuffix(".py")] + CHAINS[role] + TAIL
        checked = []
        for i, mod in enumerate(mods):
            path = original(role, mod + ".py")
            blob = include(path)
            tree = ast.parse(blob, filename=path)
            imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
            if i + 1 < len(mods) and mods[i + 1] not in imports:
                raise RuntimeError(f"Active source import edge missing: {role}:{mod}->{mods[i+1]}")
            checked.append({"module":mod, "path":path, "sha256":sources[path]["sha256"], "next_import_edge_verified": i + 1 < len(mods)})
        for mod in COMMON:
            include(original(role, mod + ".py"))
        extras = {"E3":["e3_public_recovery_phase_v1", "h1_external_operator_command_v1", "e2_directional_spin_runtime_v1"], "E2":["e2_directional_spin_runtime_v1"], "E0":["directional_spin_runtime"], "W35":["retention_flat_runtime", "retained_flat_command_math", "config_mod4v1_w35"]}.get(role, ["retention_flat_runtime"])
        for mod in extras:
            include(original(role, mod + ".py"))
        if role not in ("E3", "W35", "E0", "E2"):
            meta_path = f"{BASE}/{role}/E1_CANONICAL_SOURCE_METADATA.json"
            meta = json.loads(include(meta_path))
            if Path(meta["entry"]).name != ENTRIES[role]:
                raise RuntimeError("E1 entry metadata identity differs: " + role)
        bindings[role] = {"tier":"SOURCE_ENTRY_IMPORT_TRACE", "chain":checked, "observed_runtime_binding":"NAMED_STARTUP_LAYOUT_ONLY; full live class/function identity still Gate1", "sys_modules_override": {"E2":"directional_spin_runtime=e2_directional_spin_runtime_v1; entry83-85", "E3":"directional_spin_runtime=h1_external_operator_command_v1; entry82-84"}.get(role, None)}
    def src(file, lines):
        return {"per_role_template":f"{BASE}/{{ROLE}}/runtime/isaac/mod4/{file}:{lines}", "evidence":"SOURCE_ONLY_SEMANTICS; per-role source hashes in source_manifest.json"}
    def f(name, unit, scale, clock, classes, source, **kw):
        return dict(name=name, native_unit=unit, stored_scale=scale, time_semantics=clock, classes=classes, source=source, **kw)
    defs = [
      f("actor35_original", "heterogeneous; see raw35_fields", 1, "50Hz post-observation actor output; five sensor groups are original100Hz sampled/noisy/delayed", ["ACTOR_VISIBLE","SENSOR_NOISE","SENSOR_DELAY_QUEUE","EXOGENOUS_COMMAND_CLOCK","TASK_PHASE"], BRIDGE+":98-110", clean=False),
      f("contact_history", "N; 3 bins x left/right wheels x world xyz; newest bin first", .01, "fixed5ms mean-force history; history is not a clean current sensor or a noise term", ["DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], src("contact_capture.py","36-47,91-143")),
      f("applied_torque", "N*m for rotational joints; N for prismatic joints; source data.applied_torque is approximate computed effort, not measured force", .02, "current articulation computed applied effort; exact last-substep timestamp is Gate1", ["DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], BRIDGE+":111"),
      f("mild_factor", "dimensionless shared mass/inertia scale", 1, "per-environment episode constant, sampled only selected resets", ["STATIC_DR"], src("mild_dr.py","57-88")),
      f("delay_legs_lag_steps", "physics tick (2500us); stored values 0/.5/1", .5, "per-episode configuration, not pending queue state", ["STATIC_DR"], src("action_delay_physics_queue.py","34-46")),
      f("delay_legs_pending", "rad; four processed CAD-coherent leg position targets", 1, "latest submitted target retained even after pending_valid is false; valid/timing omitted by bridge", ["DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], src("action_delay_physics_queue.py","48-71")),
      f("delay_legs_applied", "rad; four processed leg position targets", 1, "current held actuator targets; applied validity and issue/first-apply timestamp omitted", ["DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], src("action_delay_physics_queue.py","60-78")),
      f("delay_wheels_lag_steps", "physics tick (2500us); stored values 0/.5/1", .5, "per-episode configuration", ["STATIC_DR"], src("action_delay_physics_queue.py","34-46")),
      f("delay_wheels_pending", "rad/s; two processed wheel velocity targets", 1, "latest submitted target, not a complete queue", ["DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], src("action_delay_physics_queue.py","48-71")),
      f("delay_wheels_applied", "rad/s; two processed wheel velocity targets", 1, "current held wheel targets; not torque", ["DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], src("action_delay_physics_queue.py","60-78")),
      f("feedback_delay", "100Hz sample tick (10000us), native0/1", 1, "per-episode delay choice; not FIFO/cache", ["STATIC_DR","SENSOR_DELAY_QUEUE"], src("feedback_delay_mild.py","8-15")),
      f("SpringPressure_factor", "dimensionless; 2000N/m nominal times independent factor", 1, "two independent episode stiffness factors [.9,1.1]", ["STATIC_DR"], src("spring_pressure_training_env.py","40-49")),
      f("GasDamping_factor", "dimensionless; 3Ns/m nominal times independent factor", 1, "two independent episode damping factors [.9,1.1]", ["STATIC_DR"], src("gas_damping_factor.py","9-26")),
      f("ChassisCOM_delta_m", "m in chassis link-local xyz; stored=200*meters", 200, "per-episode xyz COM translation [-.005,.005]m", ["STATIC_DR"], src("chassis_com_component.py","9-25")),
      f("PD_leg_kp", "dimensionless coefficient factor; actual kp=60*factor N*m/rad", 1, "per-episode gain parameter, not dynamic torque", ["STATIC_DR"], src("explicit_pd_component.py","8-25")),
      f("PD_leg_kd", "dimensionless coefficient factor; actual kd=2*factor N*m*s/rad", 1, "per-episode gain parameter", ["STATIC_DR"], src("explicit_pd_component.py","8-25")),
      f("PD_wheel_kd", "dimensionless coefficient factor; actual kd=.6*factor N*m*s/rad", 1, "per-episode gain parameter; wheel kp remains zero", ["STATIC_DR"], src("explicit_pd_component.py","8-25")),
      f("command_direction", "rad; retained world-direction command", 1, "exogenous sampled command; not a mass/gain DR and not generally held forever", ["EXOGENOUS_COMMAND_CLOCK"], src("retention_flat_runtime.py","66-108")),
      f("command__command_heading", "rad; actual heading used for last BODY projection", 1, "dynamic post-command-write snapshot; role update ordering must be witnessed", ["EXOGENOUS_COMMAND_CLOCK","DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], src("retention_flat_runtime.py","95-104")),
      f("command_time_left", "s native; stored=.01*seconds (seconds/100), NOT100Hz tick", .01, "command manager resampling countdown; inherited SDK clock live readback still Gate1", ["EXOGENOUS_COMMAND_CLOCK"], [BRIDGE+":122-123", CANDIDATE+":98-100"]),
      f("recovery_age", "centisecond ticks native; stored seconds", .01, "E3 increments2 per50Hzcontrol; 300 native ticks=3s", ["TASK_PHASE","EXOGENOUS_COMMAND_CLOCK"], src("e3_public_recovery_phase_v1.py","5-13")),
      f("recovery_recipe", "integer id0..12;12 normal,0..11 fixed falls", 1, "declared task recipe, not DR gain; request and reset timing matter", ["TASK_PHASE"], src("e3_public_recovery_phase_v1.py","5-13")),
      f("recovery_request", "boolean stored float", 1, "request latched by begin before physics; may differ from mode at age boundary", ["TASK_PHASE"], src("e3_public_recovery_phase_v1.py","6-10")),
      f("recovery_credited", "boolean stored float", 1, "event credited latch", ["TASK_PHASE"], src("e3_public_recovery_phase_v1.py","9-10")),
      f("recovery_stable", "centisecond ticks native; stored seconds", .01, "good adds2, otherwise0; >=50native=.5s credits; not held static", ["TASK_PHASE","DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"], src("e3_public_recovery_phase_v1.py","9-13")),
    ]
    for d in defs:
        d["canonical_unit"] = d["native_unit"]
        d["legacy_stored_unit"] = "native_unit times stored_scale; model scaling is not a physical unit"
        d["legacy_to_canonical_multiplier"] = 1 / d["stored_scale"]
    for d in defs:
        if d["name"] in ("delay_legs_lag_steps", "delay_wheels_lag_steps"):
            d.update(canonical_unit="requested_delay_us", legacy_stored_unit="0/.5/1", legacy_to_canonical_multiplier=5000)
        elif d["name"] == "feedback_delay":
            d.update(canonical_unit="requested_delay_us", legacy_stored_unit="0/1 original100Hz ticks", legacy_to_canonical_multiplier=10000)
        elif d["name"] in ("recovery_age", "recovery_stable"):
            d.update(canonical_unit="s", legacy_stored_unit="s (.01*native centisecond ticks)", legacy_to_canonical_multiplier=1)
        elif d["name"] == "command_time_left":
            d.update(canonical_unit="s", legacy_stored_unit="actual_seconds*.01", legacy_to_canonical_multiplier=100)
    byname = {d["name"]:d for d in defs}
    layouts = {}
    for role in ROLES:
        row = startup[role]
        offset = 0
        fields = []
        for name, width in row["startup"]["context_layout"]:
            spec = byname[name].copy()
            spec.update(offset=offset, width=width, end_exclusive=offset+width, audience="ACTOR" if name=="actor35_original" else "PRIVILEGED_WM_CRITIC_AUX_ONLY", observation_evidence="OBSERVED_STARTUP_NAMED_LAYOUT", value_semantics_evidence="SOURCE_ONLY; no new runtime value capture")
            fields.append(spec)
            offset += width
        if offset != row["startup"]["context_dim"]:
            raise RuntimeError("Published context width differs")
        layouts[role] = {"context_dim":offset,"actor_dim":35,"actual_BPTT_policy_steps":row["actual_BPTT_policy_steps"],"observed_tier":"OBSERVED_TRAINED_STARTUP_LAYOUT" if role in ("E3","W35") else "OBSERVED_ACTUAL0_CAPTURE_STARTUP_LAYOUT_NOT_TRAINING", "fields":fields,"source_binding":bindings[role]}
    raw = []
    for name,offset,width,unit,scale,classes,clock in [
      ("commands",0,3,"BODY vx,vy m/s; signed yaw rad/s",1,["ACTOR_VISIBLE","EXOGENOUS_COMMAND_CLOCK"],"command-manager observation clock, not delayed sensor"),
      ("height_command",3,1,"m",5,["ACTOR_VISIBLE","EXOGENOUS_COMMAND_CLOCK"],"height command, not actual base height; not delayed"),
      ("base_ang_vel",4,3,"rad/s in SAMPLE BODY frame",.5,["ACTOR_VISIBLE","SENSOR_NOISE","SENSOR_DELAY_QUEUE"],"100Hz before scale; sample BODY components not re-rotated at apply"),
      ("projected_gravity",7,3,"dimensionless",1,["ACTOR_VISIBLE","SENSOR_NOISE","SENSOR_DELAY_QUEUE"],"100Hz before scale"),
      ("leg_pos",10,4,"rad relative to default joint positions",1,["ACTOR_VISIBLE","SENSOR_NOISE","SENSOR_DELAY_QUEUE"],"100Hz clean+noise+episode encoder bias before queue"),
      ("wheel_pos_slots",14,2,"structural zero (not wheel measurement)",1,["ACTOR_VISIBLE"],"always zero original slots"),
      ("leg_vel",16,4,"rad/s relative joint velocities",.1,["ACTOR_VISIBLE","SENSOR_NOISE","SENSOR_DELAY_QUEUE"],"100Hz before scale"),
      ("wheel_vel",20,2,"rad/s relative joint velocities",.1,["ACTOR_VISIBLE","SENSOR_NOISE","SENSOR_DELAY_QUEUE"],"100Hz before scale"),
      ("last_action",22,6,"policy action coordinate; NOT delayed processed targets",1,["ACTOR_VISIBLE","DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"],"current action-manager last_action at50Hz observation"),
      ("mode_onehot",28,7,"seven boolean categories",1,["ACTOR_VISIBLE","TASK_PHASE"],"public mode observation clock"),
    ]:
        raw.append(dict(name=name,offset=offset,width=width,end_exclusive=offset+width,native_unit=unit,stored_scale=scale,classes=classes,time_semantics=clock,source=src("mod4_task.py","1206-1245"),clean=False))
    channels = {}
    for name,width,bound,unit,scale in [("base_ang_vel",3,.125,"rad/s",.5),("projected_gravity",3,.025,"dimensionless",1),("leg_pos",4,.005,"rad",1),("leg_vel",4,.25,"rad/s",.1),("wheel_vel",2,.5,"rad/s",.1)]:
        channels[name] = {"width":width,"unit":unit,"noise_uniform_bound":bound,"manager_scale":scale,"episode_bias_bound":.0075 if name=="leg_pos" else 0,"profile":"noise_bias_mild_v1","runtime_profile_binding":"SOURCE_EXPECTED_NOT_LIVE_VERIFIED_GATE1","source":src("sensor_mild_math.py","5-51")}
    missing = []
    def missing_field(name,width,unit,classes,clock,source,why):
        missing.append(dict(name=name,offset=None,width=width,native_unit=unit,classes=classes,time_semantics=clock,source=source,evidence="SOURCE_ONLY_NOT_IN_OBSERVED_CONTEXT; actual per-transition receipts UNKNOWN",gap=why))
    for name,width,unit in [("mild_motor_episode_scale_legs",4,"dimensionless"),("mild_motor_episode_scale_wheels",2,"dimensionless"),("wheel_mu",1,"dimensionless"),("mild_nominal",1,"boolean")]:
        missing_field(name,width,unit,["STATIC_DR"],"per episode",src("mild_dr.py","57-93"),"mild_factor captures mass/inertia only; bridge optional gain_factor absent")
    missing_field("sensor_leg_encoder_bias",4,"rad",["STATIC_DR","SENSOR_NOISE"],"sampled per selected episode reset",src("sensor_mild_math.py","14-26"),"no bias tensor in xi")
    qfields={"lag_steps":1,"episode":1,"pending":None,"pending_valid":1,"issued_tick":1,"due_tick":1,"applied":None,"applied_valid":1,"applied_issue_tick":1,"first_apply_tick":1,"last_submit_tick":1,"last_apply_tick":1}
    for group,width in (("legs",4),("wheels",2)):
        for field,n in qfields.items():
            if field in ("lag_steps","pending","applied"):continue
            missing_field("action_queue."+group+"."+field,n,"boolean" if field.endswith("valid") else "episode id" if field=="episode" else "global physics tick2500us",["DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"],"submit before first apply; adapter actual apply tick=sim_counter-1",src("action_delay_physics_queue.py","10-78"),"xi has only lag,pending,applied; missing validity/timing/episode")
    for name,channel in channels.items():
        w=channel["width"]
        for kind,classes in [("clean_at_sample",["SENSOR_CLEAN"]),("noise_used",["SENSOR_NOISE"]),("noisy_before_queue",["SENSOR_NOISE"]),("queue_cur",["SENSOR_DELAY_QUEUE"]),("queue_out",["SENSOR_DELAY_QUEUE"])]:
            missing_field(name+"."+kind,w,channel["unit"],classes,"original100Hz MID and END samples at physics ticks start+4,+8",src("feedback_delay_runtime.py","24-27,74-86"),"no captured clean MID/END and noise-used/queue receipts;50Hzendpoint not substitute")
        for key in ("last","sample_tick","ready","episode","draw_count"):
            missing_field(name+"."+key,1,"boolean" if key=="ready" else "100Hz tick or integer counter",["SENSOR_DELAY_QUEUE"] if key!="draw_count" else ["SENSOR_NOISE"],"before/after each original sample; including reset warmup",src("feedback_delay_mild.py","8-36"),"delay scalar does not prove selected sample age or cache identity")
    for name in ("peak","delta"):
        missing_field("recovery_"+name,1,"dimensionless upright progress / event increment",["TASK_PHASE","DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE"],"E3 termination hook pre-reset; begin clears delta",src("e3_public_recovery_phase_v1.py","7-14"),"age/stable alone insufficient for task reward phase state")
    missing_field("command_phase_elapsed_and_resample_receipts",None,"s,flags,role-specific command state",["EXOGENOUS_COMMAND_CLOCK","TASK_PHASE","UNKNOWN"],"pre-control,command compute/post observation,next-write; E2 phase_elapsed advances after write",src("e2_directional_spin_runtime_v1.py","100-104"),"not in observed xi; role-specific class/function/clock receipt required")
    schema = {
      "schema_version":"phase1_state_context_partition_v1", "status":"SOURCE_CONTRACT_ONLY_GATE1_UNKNOWN", "classifications":CLASSIFICATIONS,
      "root":str(ROOT), "read_scope":"fixed source + published STARTUP metadata; no model/replay/rawJSONL",
      "clocks":{"physics_us":2500,"control_us":20000,"feedback_sample_us":10000,"physics_callbacks_per_control":8,"samples_per_control":2,"sample_offsets_physics_ticks":[4,8],"bridge_f_unit":"50Hz control step;seconds=f*.02; separate from100Hz sample tick and global physics tick","contact_bin_us":5000},
      "actor_boundary":{"width":35,"legacy_actual_source":"Raw35ActorMDP.obs=context[..., :35] identity", "new_contract_input":"named actor35_original only; no old vector split/slicing/migration", "actor_clean_substitution":False,"privileged_fields_visible":False,"sensor_noise_redraws":0,"source":CANDIDATE+":190-225"},
      "preserved":{"plant":"physics400-k2000-d3", "physics_dt":.0025,"control_hz":50,"feedback_hz":100,"D0_D7":"unchanged","H1":"unchanged","mothers":"unchanged","original_acceptance":"unchanged","legacy_checkpoints":"read/migration/slicing absent","stage2_trainer":"absent"},
      "layouts":layouts,"raw35_fields":raw,"sensor_channels":channels,"required_extended_fields":missing,
      "action_queue_fields":qfields,"action_groups":{"legs":4,"wheels":2},
      "source_definitions_not_observed_fields":{"mild_mass_factor":"optional bridge hook only; absent in all8 layouts","mild_inertia_factor":"optional bridge hook only; absent in all8 layouts","mild_gain_factor":"optional bridge hook only; absent in all8 layouts","command_sign_heading_age_mode_key":"optional hook; absent in all8 observed layouts; no fabricated offsets"},
      "gate1":{"admitted":False,"reason":"No independently verified original100Hz cleanMID/END+noise-used+queue/clock/reset receipts in reviewed evidence", "must_passively_capture":["live entry/import/class/function identities and source hashes for all8 roles","two original samples/control at start+4,+8 physics ticks, not reconstructed50Hzendpoint","per sample clean pre-noise input,actual cached noise_used,episode bias,draw count,RNG digest before/after natural calls","feedback cache cur,out,last,sample_tick,ready,episode,selected age0/10000us and reset warmup","both complete action queue groups,processed target and actual articulation target at each of8 physical apply ticks","static DR/gain/COM/bias readback tied to episode ids; unchanged between nonreset controls","command snapshot precontrol/postcompute/nextwrite,actual resample/reset/boundary events; E2 phase and E3 phase inclpeak/delta","pre-reset s1 and done flags; postreset episode/cache identity; no mixed terminal-to-reset target","passive observer effect counters:extra resets/physics/action/model operations/noise draws all0,private RNG unchanged by probe","actor35 equals original named raw fields,only actor35 visible;WM/critic privileged may use separate schema","source gate and synthetic contracts remain separate from actual SDK Gate1 admission"], "validatable_conditions":["exact named dimensions and units/scales","100Hz sample continuity and2500us/10000us/20000us clock consistency","noisy=clean+noise_used+episode_bias before delay and manager scale","out=current or immediately previous sample per configured delay,initialwarmup=current fresh episode","action due=issue+lag,first_apply latency0/2500/5000us;held sample age not mistaken for first-transition latency","same episode static values identical;partial reset unrelated environments unchanged","no RNG redraw by observer/no train/evaluation/model mutations","unknown field/clock/source identity hard Unknown; no hold/zero/sample fabrication" ]},
      "evidence_limits":{"named_layout":"observed all8;E3/W35 additionally published saved-report layout agrees","field_semantics":"source-only plus named-layout evidence; not live per-field readback","actual_sdk_pass":False,"paper_ready":False,"exact":False},
    }
    manifest = {"version":1,"root":str(ROOT),"sources":dict(sorted(sources.items())),"read_scope":schema["read_scope"],"hash_method":"SHA256 bytes;source data only, never imports/executes originals"}
    save_new("source_manifest.json",manifest)
    schema["source_manifest_sha256"] = digest((HERE/"source_manifest.json").read_bytes())
    save_new("partition_schema_v1.json", schema)
    return {"roles":len(layouts),"legacy_named_fields":sum(len(x["fields"]) for x in layouts.values()),"source_files":len(sources),"extended_missing_fields":len(missing),"actual_sdk_pass":False,"exact":False}

if __name__ == "__main__":
    print(json.dumps(build(),ensure_ascii=False))
