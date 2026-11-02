"""Stdlib, in-memory semantic helpers and explicit-denominator aggregation.
SOURCE_ONLY: no I/O, no Torch/SDK, no CLI, no training, no graduation verdict.
Scalar helper results are semantic fixtures, not measured skill evidence.
Callers must bind real source booleans/UIDs/predicate SHA in a future adapter.
"""
import math

ROLES = ('E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')
PREDICATE_GAPS = {'E0','SLOPE_INDEPENDENT50'}
STATUSES = ('source_true','source_false','incomplete','unknown')

class EvidenceError(ValueError):
    pass

def need(value, message):
    if not value:
        raise EvidenceError(message)

def finite(value):
    return type(value) in (float,int) and math.isfinite(value)

def strict_bool(value, name):
    need(type(value) is bool, 'Boolean required: '+name)
    return value

def ratio(success, denominator):
    need(type(success) is int and type(denominator) is int and 0 <= success <= denominator, 'Invalid ratio counts')
    return success / denominator if denominator else None

def wilson95(success, denominator):
    p = ratio(success, denominator)
    if p is None:
        return None
    z = 1.959963984540054
    d = 1 + z*z / denominator
    center = (p + z*z/(2*denominator)) / d
    radius = z * math.sqrt(p*(1-p)/denominator + z*z/(4*denominator*denominator)) / d
    return [max(0.,center-radius), min(1.,center+radius)]

def e2_scalar_fact(*, seconds, along_distance, cross_distance, turn, commanded_yaw_integral, sign, complete, terminated=False, truncated=False, identity_continuous=True, eight_substeps=True):
    """Literal E2Cycles213.emit semantics plus explicit caller identity checks.
    Float64 CPU fixture only; numerical boundary equivalence to source float32
    is not asserted. Prefer source-written accepted booleans in real adapters.
    """
    for name,x in locals().copy().items():
        if name in ('seconds','along_distance','cross_distance','turn','commanded_yaw_integral','sign'):
            need(finite(x),'Nonfinite E2 scalar: '+name)
    for name,value in (('complete',complete),('terminated',terminated),('truncated',truncated),('identity_continuous',identity_continuous),('eight_substeps',eight_substeps)):
        strict_bool(value,name)
    need(identity_continuous and eight_substeps,'Broken source UID/episode/direction/sign or physics continuity')
    need(sign in (-1,1),'Signed moving cycle only')
    need(not complete or turn*sign >= 2*math.pi,'Complete flag contradicts sampled2pi')
    safe = seconds if seconds > 0 else 1.
    along, cross, yaw = along_distance/safe, cross_distance/safe, (turn-commanded_yaw_integral)/safe
    kin = abs(along-.5)<=.05 and abs(cross)<=.05 and abs(yaw)<=.2
    valid = seconds>0 and complete and not terminated and not truncated
    return {'original_kinematic_bounds_met':kin, 'valid_original_complete_skill_sample':valid, 'original_complete_cycle_fact':valid and kin, 'source_complete_denominator_member':complete}

class RecoveryCreditFixture:
    """RecoveryPhase literal public100Hz counters; synthetic only."""
    def __init__(self,recipe):
        need(type(recipe) is int and 0 <= recipe < 13,'Original13 recipes only')
        self.recipe=recipe
        self.age=self.stable=0
        self.credited=False
    def control(self,gravity_z,root_speed,angular_speed):
        need(all(finite(x) for x in (gravity_z,root_speed,angular_speed)),'Nonfinite recovery fixture')
        request=self.recipe!=12 and self.age<300
        good=gravity_z<-.984807753 and root_speed<.03 and angular_speed<.2 and request
        self.stable=self.stable+2 if good else 0
        event=self.stable>=50 and not self.credited
        self.credited|=event
        self.age+=2
        return {'request':request,'event':event,'credited':self.credited,'age100Hz':self.age,'stable100Hz':self.stable}

def first_episode_credit(credit_live_term_trunc):
    """Credit is read before the first reset; later reset credit is not stitched."""
    live=True
    first_credit=False
    first_terminated=False
    for credited,terminated,truncated in credit_live_term_trunc:
        for k,v in (('credited',credited),('terminated',terminated),('truncated',truncated)):
            strict_bool(v,k)
        first_credit |= credited and live
        first_terminated |= terminated and live
        live &= not (terminated or truncated)
    return {'credited':first_credit,'first_episode_terminated':first_terminated}

def support_from_eight(force_z):
    need(len(force_z)==8 and all(finite(v) for v in force_z),'All8 physical Fz callbacks required')
    return sum(max(0.,v) for v in force_z)*.0025/.02 > 1.

def endpoint_scalar_fact(role, group, rows):
    """Ordered same-episode BOTH wheel supported endpoints before first failure.
    Input rows are already pre-reset canonical two-link coordinates, NOT COM.
    """
    need(role in ('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135'),'No source endpoint rule joined for this role')
    need(group in ('ascending','descending','stand'),'Original route group only')
    edge=1.2 if role=='SLOPE135' else .275
    if group=='stand':
        return {'crossing_required':False,'contact_confirmed':False}
    episodes={}
    previous=-1
    for row in rows:
        control=row['control']
        need(type(control) is int and control>previous,'Strict ordered observation controls required')
        previous=control
        if strict_bool(row['terminated'],'terminated'):
            break
        u=row['wheel_u']
        need(len(u)==2 and all(finite(v) for v in u),'Two canonical wheel-link coordinates required')
        s=row['support']
        need(len(s)==2 and all(type(v) is bool for v in s),'Two original support booleans required')
        seg=episodes.setdefault(row['episode'],{'before':[],'after':[]})
        before=max(u)<-edge if group=='ascending' else min(u)>edge
        after=min(u)>edge if group=='ascending' else max(u)<-edge
        if before and all(s):seg['before'].append(control)
        if after and all(s):seg['after'].append(control)
    fact=any(v['before'] and v['after'] and min(v['before'])<max(v['after']) for v in episodes.values())
    return {'crossing_required':True,'contact_confirmed':bool(fact)}

def w35_source_row_group(row):
    """Read original standing/complete/accepted Boolean fields; no proxy math."""
    need(row['record_type']=='same_UID_original_RM70_command','Original RM70 command row expected')
    for k in ('standing','natural_complete_nonterminal_interval','complete_interval_bounds_fact'):
        strict_bool(row[k],k)
    complete=row['natural_complete_nonterminal_interval']
    accepted=row['complete_interval_bounds_fact']
    need(not accepted or complete,'Source accepted must imply source complete')
    return {'group':'standing_complete' if row['standing'] else 'moving_complete','status':('source_true' if accepted else 'source_false') if complete else 'incomplete'}

def summarize_group_ledger(*, role, seed, rows, required_groups, planned_counts, unit_kind, evidence_scope_verified=False, attempt_ledger_preregistered=False, excluded_groups=()):
    """One role/seed, explicit unique units, no survivor-only denominator surgery.
    unit_kind: initial_cohort or source_event. For source_event, incomplete rows
    remain OUTSIDE the source conditional denominator. The all-started lower
    credit is separately named, and exposed only for a preregistered attempt
    ledger; source partial segments alone are not a preregistered attempt unit.
    No method in this module emits a goal/pass/graduation verdict.
    """
    need(role in ROLES,'Exactly eight roles excludingH1')
    need(type(seed) is int,'Seed integer required')
    strict_bool(evidence_scope_verified,'evidence_scope_verified')
    strict_bool(attempt_ledger_preregistered,'attempt_ledger_preregistered')
    need(unit_kind in ('initial_cohort','source_event'),'Explicit source unit kind required')
    need(len(required_groups)==len(set(required_groups)) and bool(required_groups),'Distinct required groups')
    need(set(required_groups)==set(planned_counts),'All planned group counts required')
    need(set(required_groups).isdisjoint(excluded_groups),'Excluded group is not a scored group')
    if role=='E3':
        need(set(excluded_groups)<= {'normal12'},'Only normal12 is excluded from E3 rescue')
        need('normal12' not in required_groups,'Normal recipe excluded from rescue denominator')
    else:
        need(not excluded_groups,'No extra undocumented group exclusions')
    for k,n in planned_counts.items():
        need(type(n) is int and n>=0,'Nonnegative planned group count: '+k)
    counts={g:{status:0 for status in STATUSES} for g in required_groups}
    excluded={g:0 for g in excluded_groups}
    seen=set()
    for row in rows:
        need(row['role']==role and row['seed']==seed,'No cross-role/seed pooling')
        key=row['unit_id']
        need(type(key) is str and key and key not in seen,'Duplicate or empty source unit identity')
        seen.add(key)
        group=row['group']
        if group in excluded:
            excluded[group]+=1
            continue
        need(group in counts,'Unexpected group; do not silently discard')
        need(row['status'] in STATUSES,'Mutually exclusive source status required')
        counts[group][row['status']]+=1
    out={}
    measurable=evidence_scope_verified and role not in PREDICATE_GAPS
    for group,c in counts.items():
        total=sum(c.values())
        need(total==planned_counts[group],'Missing or duplicate planned unit coverage: '+group)
        source_n=total if unit_kind=='initial_cohort' else c['source_true']+c['source_false']
        source_rate=ratio(c['source_true'],source_n) if measurable else None
        out[group]={**c,'planned_units':total,'source_denominator':source_n,'source_native_rate':source_rate,'source_native_wilson95':wilson95(c['source_true'],source_n) if measurable else None,'source_outside_complete_denominator':0 if unit_kind=='initial_cohort' else c['incomplete']+c['unknown'],'separately_labelled_preregistered_all_started_credit':ratio(c['source_true'],total) if measurable and attempt_ledger_preregistered else None,'scope_status':'SOURCE_COUNTS_ONLY' if not measurable else 'SOURCE_UNIT_ESTIMATES_NOT_GRADUATION'}
    return {'kind':'IN_MEMORY_SOURCE_DENOMINATOR_SUMMARY_NO_VERDICT','role':role,'seed':seed,'groups':out,'excluded_groups':excluded,'source_binary_predicate_gap':role in PREDICATE_GAPS,'evidence_scope_verified':evidence_scope_verified,'full_skill_graduation':None,'user_target_achievement':None,'event_correlation_warning':'Repeated events share env/seed; Wilson is descriptive, not an independent-env reliability proof.'}
