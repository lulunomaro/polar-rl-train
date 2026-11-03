"""SOURCE-only passive actuation tap. No native imports, I/O, RNG, or reset hooks.
Hooks existing calls once; copies only already-stored memory / write arguments.
Torch tensors, if present in a future live call, are detached+cloned on their
existing device, never cpu()/tolist() here. That path is NOT live-verified.
"""
from functools import wraps

QUEUE_FIELDS = ("lag_steps", "episode", "pending", "pending_valid", "issued_tick", "due_tick",
                "applied", "applied_valid", "applied_issue_tick", "first_apply_tick",
                "last_submit_tick", "last_apply_tick")
GROUPS = {"legs":4, "wheels":2}
PHYSICS_US = 2500


class CaptureUnknown(ValueError):
    pass


class CaptureViolation(ValueError):
    pass


def unknown(reason):
    return {"status":"UNKNOWN", "reason":reason}


def stored(obj, name):
    """Read an instance dictionary, never evaluate a descriptor/property/getter."""
    try:
        values = object.__getattribute__(obj, "__dict__")
    except (AttributeError, TypeError):
        return unknown("No instance dictionary: " + name)
    return values[name] if isinstance(values, dict) and name in values else unknown("No stored source attribute: " + name)


def is_unknown(value):
    return isinstance(value, dict) and value.get("status") == "UNKNOWN"


def freeze_memory(value):
    """Own a snapshot, not a borrowed alias. Unsupported opaque values stay UNKNOWN."""
    if value is None or type(value) in (bool, int, float, str):
        return value
    if type(value) in (list, tuple):
        return [freeze_memory(v) for v in value]
    if type(value) is dict:
        return {k:freeze_memory(v) for k,v in value.items() if type(k) in (str,int)}
    if type(value).__module__ == "torch" and type(value).__name__ == "Tensor":
        return value.detach().clone()
    return unknown("Opaque memory type: " + type(value).__module__ + "." + type(value).__name__)


def queue_snapshot(queue, group):
    groups = stored(queue, "groups")
    if type(groups) is not dict or group not in groups or type(groups[group]) is not dict:
        return unknown("No stored queue group")
    return {name:freeze_memory(groups[group].get(name, unknown("Missing queue field: " + name))) for name in QUEUE_FIELDS}


def snapshot_static(env):
    """Read configuration/model memory only. Physical readback intentionally UNKNOWN."""
    mild = stored(env, "_mild_dr")
    pd = stored(env, "_explicit_pd")
    out = {"evidence":"STORED_SOURCE_CONFIGURATION_OR_MODEL_MEMORY_NOT_PHYSICAL_READBACK",
           "mild":{name:freeze_memory(stored(mild,name)) for name in ("profile","factor","mu","nominal","reset_count","output")},
           "motors":{}, "components":{},
           "physical_readback":unknown("No additional SDK getter; setter arguments/model values are not physical readback")}
    for group in GROUPS:
        motor = stored(pd, group)
        out["motors"][group] = {name:freeze_memory(stored(motor,name)) for name in ("episode_scale","step_scale")}
    for attr, fields in (("_explicit_pd",("factor","episode")),("_chassis_com",("delta_m","episode")),
                         ("_spring_pressure",("factor","episode")),("_gas_damping",("factor","episode"))):
        comp = stored(stored(env,attr),"component")
        out["components"][attr] = {name:freeze_memory(stored(comp,name)) for name in fields}
    return out


class ActuationTap:
    """Single-thread control-loop tap; attach after original adapter installation.

    Does not wrap env._reset_idx, term.reset, queue.reset, termination, or sensor
    functions. A separate sensor tap may own those hooks. close() restores only
    this tap's still-owned attributes, never overwrites a later wrapper.
    """
    def __init__(self, env, capacity=8192):
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("Positive finite event capacity required")
        self.env, self.capacity = env, capacity
        self.events, self.patches, self.context = [], [], []
        self.observed_calls = {}
        self.sequence = self.dropped = self.observer_errors = 0
        self.missing_hooks, self.errors, self.restore_conflicts = [], [], []
        self.closed = False
        self.adapter = stored(env,"_physics_action_delay")
        self.queue = stored(self.adapter,"queue")
        terms = stored(self.adapter,"terms")
        if is_unknown(self.queue) or type(terms) is not dict or set(terms) != set(GROUPS):
            raise CaptureUnknown("Existing physical action adapter/queue/terms required; no new adapter constructed")
        specs = [(self.queue,"submit","queue_submit",None),(self.queue,"apply","queue_apply",None)]
        seen = set()
        for group,term in terms.items():
            specs += [(term,"process_actions","issue",group),(term,"apply_actions","term_apply",group)]
            asset = stored(term,"_asset")
            name = "set_joint_position_target" if group == "legs" else "set_joint_velocity_target"
            if is_unknown(asset):
                self.missing_hooks.append(group+": no stored _asset; target_write UNKNOWN")
            elif (id(asset),name) not in seen:
                specs.append((asset,name,"target_write",group));seen.add((id(asset),name))
        # Preflight required entries before mutation. Optional SDK write method is
        # an unverified external binding until a natural invocation is observed.
        ready = []
        for owner,name,kind,group in specs:
            try:
                original = getattr(owner,name)
            except AttributeError:
                if kind == "target_write":
                    self.missing_hooks.append(group+": target method absent; target_write UNKNOWN");continue
                raise CaptureUnknown("Required original method absent: " + name)
            if not callable(original) or getattr(original,"_phase1_actuation_tap",False):
                raise CaptureUnknown("Method is not callable or is already tapped: " + name)
            ready.append((owner,name,kind,group,original))
        try:
            for spec in ready:
                self._patch(*spec)
        except BaseException:
            self.close()
            raise

    def _guard(self, fn):
        try:
            return fn()
        except BaseException as exc:
            self.observer_errors += 1
            if len(self.errors)<8:self.errors.append(type(exc).__name__)
            return unknown("Observer capture failed; original call still retained")

    def _keep(self, event):
        key=event["kind"]+":"+str(event["group"])
        self.observed_calls[key]=self.observed_calls.get(key,0)+1
        if len(self.events)<self.capacity:self.events.append(event)
        else:self.dropped += 1

    def _patch(self, owner, name, kind, fixed_group, original):
        values = object.__getattribute__(owner,"__dict__")
        had_own, previous = name in values, values.get(name)
        tap = self
        @wraps(original)
        def wrapped(*args, **kwargs):
            seq = tap.sequence;tap.sequence += 1
            group = fixed_group
            if kind in ("queue_submit","queue_apply"):
                group = args[0] if args else kwargs.get("key")
                tick = args[2 if kind=="queue_submit" else 1] if len(args)>(2 if kind=="queue_submit" else 1) else kwargs.get("tick")
            else:
                counter = stored(tap.env,"_sim_step_counter")
                tick = counter-1 if kind in ("term_apply","target_write") and type(counter) is int else counter
            event = {"seq":seq,"kind":kind,"group":group,"tick":tick,
                     "args":tap._guard(lambda:freeze_memory(args)),"kwargs":tap._guard(lambda:freeze_memory(kwargs)),
                     "pre":tap._guard(lambda:queue_snapshot(tap.queue,group))}
            if kind=="queue_submit":event["static"]=tap._guard(lambda:snapshot_static(tap.env))
            if kind=="target_write":
                event["parent_term_apply_seq"] = tap.context[-1] if tap.context else None
                event["physical_readback"] = unknown("Only original target writer argument observed")
            if kind=="term_apply":tap.context.append(seq)
            try:
                result = original(*args,**kwargs)
            except BaseException as exc:
                event["outcome"]="RAISED";event["exception_type"]=type(exc).__name__;event["exception_identity"]=id(exc)
                event["post"]=tap._guard(lambda:queue_snapshot(tap.queue,group))
                tap._guard(lambda:tap._keep(event))
                raise
            else:
                event["outcome"]="RETURNED"
                event["post"]=tap._guard(lambda:queue_snapshot(tap.queue,group))
                # Only queue.apply output is numeric memory needed for linkage;
                # the original object itself is returned untouched for every hook.
                if kind=="queue_apply":event["selected_target"]=tap._guard(lambda:freeze_memory(result))
                tap._guard(lambda:tap._keep(event))
                return result
            finally:
                if kind=="term_apply":tap.context.pop()
        wrapped._phase1_actuation_tap = True
        setattr(owner,name,wrapped)
        self.patches.append((owner,name,had_own,previous,wrapped))

    def snapshot_static(self):
        return self._guard(lambda:snapshot_static(self.env))

    def drain(self):
        """Outside callback loop. No serialization/disk I/O; snapshots remain owned."""
        out=sorted(self.events,key=lambda row:row["seq"])
        self.events=[]
        return out

    def status(self):
        return {"dropped_events":self.dropped,"observer_errors":self.observer_errors,"errors":list(self.errors),"observed_calls":dict(self.observed_calls),
                "missing_hooks":list(self.missing_hooks),"restore_conflicts":list(self.restore_conflicts),"coverage":"UNKNOWN" if self.dropped or self.observer_errors or self.missing_hooks or self.restore_conflicts else "CAPTURE_ONLY_NOT_ADMISSION",
                "closed":self.closed,"reset_hook":False,"termination_hook":False,"sensor_hook":False,
                "runtime_class_source_binding":"UNKNOWN_UNTIL_LIVE_PIN_AND_BINDING_RECEIPT","actual_sdk_pass":False,"exact":False}

    def close(self):
        conflicts=[]
        if not self.closed:
            for owner,name,had_own,previous,wrapped in reversed(self.patches):
                current=object.__getattribute__(owner,"__dict__").get(name)
                if current is not wrapped:
                    conflicts.append(name);continue
                if had_own:setattr(owner,name,previous)
                else:delattr(owner,name)
            self.closed=True
            self.restore_conflicts.extend(conflicts)
        return {"restored":not self.restore_conflicts,"conflicts":list(self.restore_conflicts),"reset_untouched":True}

    def __enter__(self):return self
    def __exit__(self,*unused):self.close()


def install_actuation_tap(env, capacity=8192):
    return ActuationTap(env,capacity)


def _rows(value, name):
    if type(value) is not list:raise CaptureUnknown("Missing builtin offline snapshot: " + name)
    return value


def validate_apply_window(events, start_tick, expected_episode, status=None):
    """Offline stdlib validation after caller materializes owned tensors outside loop.
    Validates one reset-free 8-tick control window. Cross-reset windows stay UNKNOWN.
    This proves argument/queue linkage, NOT physical actuator readback or Gate1.
    """
    if status and (status["dropped_events"] or status["observer_errors"]):
        raise CaptureUnknown("Capture loss/observer error")
    result={}
    for e in events:
        if e.get("kind")=="queue_apply" and type(e.get("tick")) is not int:raise CaptureUnknown("Missing natural apply tick")
    for group,width in GROUPS.items():
        episodes=_rows(expected_episode.get(group),"expected episode: "+group)
        rows=sorted([e for e in events if e["kind"]=="queue_apply" and e["group"]==group and start_tick<=e["tick"]<start_tick+8],key=lambda e:e["tick"])
        if [e["tick"] for e in rows]!=list(range(start_tick,start_tick+8)):
            raise CaptureUnknown("Need exactly8 natural apply callbacks: " + group)
        metrics=[]
        for e in rows:
            if e["outcome"]!="RETURNED":raise CaptureUnknown("Original callback raised")
            g=e["post"];pre=e["pre"];n=len(episodes)
            if type(g) is not dict or type(pre) is not dict:raise CaptureUnknown("Queue pre/post absent")
            for field in QUEUE_FIELDS:
                if len(_rows(g.get(field),field))!=n or len(_rows(pre.get(field),"pre "+field))!=n:
                    raise CaptureUnknown("Queue environment width missing")
            if g["episode"]!=episodes:raise CaptureUnknown("Reset boundary inside control window")
            if g["last_apply_tick"]!=[e["tick"]]*n:raise CaptureViolation("Last apply clock mismatch")
            target=_rows(e["selected_target"],"selected_target")
            if target!=g["applied"] or any(len(row)!=width for row in target):raise CaptureViolation("Selected delayed target mismatch")
            writes=[w for w in events if w["kind"]=="target_write" and w["group"]==group and w["tick"]==e["tick"]]
            if len(writes)!=1 or writes[0]["outcome"]!="RETURNED":raise CaptureUnknown("Original target-write call absent/ambiguous")
            arg=writes[0]["args"][0] if writes[0]["args"] else writes[0]["kwargs"].get("target")
            if arg!=target:raise CaptureViolation("Original target writer argument differs from queue selection")
            env_metrics=[]
            for i in range(n):
                lag=g["lag_steps"][i]
                if type(lag) is not int or lag not in (0,1,2):raise CaptureViolation("Lag outside original0/1/2physics ticks")
                for field in QUEUE_FIELDS:
                    if field in ("pending","applied"):continue
                    expected_type=bool if field.endswith("valid") else int
                    if type(g[field][i]) is not expected_type:raise CaptureViolation("Queue metadata type differs: "+field)
                if g["issued_tick"][i]!=start_tick or g["last_submit_tick"][i]!=start_tick:
                    raise CaptureUnknown("Control issue tick not linked to this window")
                if g["due_tick"][i]!=g["issued_tick"][i]+lag:raise CaptureViolation("due!=issue+lag")
                if g["pending_valid"][i] != (e["tick"]<g["due_tick"][i]):raise CaptureViolation("Pending valid transition mismatch")
                pre=e["pre"]
                desired=pre["pending"][i] if pre["pending_valid"][i] and pre["due_tick"][i]==e["tick"] else pre["applied"][i]
                if g["applied"][i]!=desired:raise CaptureViolation("Applied target changed outside original due transition")
                if g["pending_valid"][i] and g["due_tick"][i]<=e["tick"]:raise CaptureViolation("Late pending transition")
                valid=g["applied_valid"][i]
                first=(g["first_apply_tick"][i]-g["applied_issue_tick"][i])*PHYSICS_US if valid else None
                age=(e["tick"]-g["applied_issue_tick"][i])*PHYSICS_US if valid else None
                if valid and (first!=lag*PHYSICS_US or age<first):raise CaptureViolation("First latency / held-age contradiction")
                env_metrics.append({"first_transition_latency_us":first,"held_command_age_us":age,"neutral_reset_hold":not valid})
            metrics.append({"tick":e["tick"],"envs":env_metrics})
        result[group]=metrics
    return {"kind":"QUEUE_AND_ORIGINAL_WRITE_ARGUMENT_CONTRACT_ONLY","groups":result,"physical_readback":"UNKNOWN","actual_sdk_pass":False,"exact":False}


def validate_static_snapshot(snapshot):
    """Offline structural/source invariant, never a physical parameter admission."""
    mild=snapshot.get("mild",{})
    n=len(_rows(mild.get("factor"),"mild.factor"))
    if not n:raise CaptureUnknown("No environment rows")
    for field in ("mu","nominal","reset_count"):
        if len(_rows(mild.get(field),field))!=n:raise CaptureUnknown("Missing static environment rows")
    for group,width in GROUPS.items():
        motor=snapshot.get("motors",{}).get(group,{})
        for field in ("episode_scale","step_scale"):
            value=_rows(motor.get(field),group+"."+field)
            if len(value)!=n or any(type(row) is not list or len(row)!=width for row in value):
                raise CaptureUnknown("Missing motor4+2 source memory")
            if field=="step_scale" and any(v!=1 for row in value for v in row):
                raise CaptureViolation("Original white profile requires step_scale==1")
    if not is_unknown(snapshot.get("physical_readback")):
        raise CaptureViolation("Configuration snapshot mislabeled as physical readback")
    return {"stored_source_memory":True,"step_scale_exactly_one":True,"physical_readback":"UNKNOWN","actual_sdk_pass":False,"exact":False}


def validate_reset_edge(previous_post, next_pre):
    """Infer selected episode edge only; does not invent the unobserved reset tick."""
    old=_rows(previous_post.get("episode"),"old episode");new=_rows(next_pre.get("episode"),"new episode")
    if len(old)!=len(new):raise CaptureUnknown("Reset environment count mismatch")
    selected=[]
    for i,(a,b) in enumerate(zip(old,new)):
        if b==a:
            if any(previous_post[f][i]!=next_pre[f][i] for f in QUEUE_FIELDS):raise CaptureViolation("Unselected environment mutated between adjacent captures")
        elif b==a+1:
            selected.append(i)
            if next_pre["pending_valid"][i] or next_pre["applied_valid"][i]:raise CaptureViolation("Reset stale validity retained")
            if any(next_pre[f][i]!=-1 for f in ("issued_tick","due_tick","applied_issue_tick","first_apply_tick","last_submit_tick")):
                raise CaptureViolation("Reset stale issue/apply metadata retained")
            if next_pre["last_apply_tick"][i]!=previous_post["last_apply_tick"][i]:raise CaptureViolation("Partial reset rebased global physics clock")
        else:raise CaptureUnknown("Multiple/unobserved episode transitions")
    return {"selected_env_ids":selected,"unselected_exact":True,"reset_tick":"UNKNOWN_NO_RESET_HOOK","physical_neutral_readback":"UNKNOWN"}
