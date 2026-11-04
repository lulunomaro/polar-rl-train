"""Bounded scalar traceback locator. Caller supplies decoded dict AND exact pure module.
No file/target import, getter, source retrieval, rewriting, retry or admission.
"""
import hashlib
import json
import types

PURE_SHA256 = '2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979'
API_LINES = {'require':44, 'field':47, 'integer':54, 'number':58, 'vector':62,
             'matrix':69, 'typed_equal':74, 'queue_state':357, 'actuation_component':365}
QUEUE = ('lag_steps','episode','pending','pending_valid','issued_tick','due_tick',
         'applied','applied_valid','applied_issue_tick','first_apply_tick','last_submit_tick','last_apply_tick')


def _canonical(value):
    # Reject non-decoded objects without inspecting attributes/calling their getters.
    pending = [value]
    while pending:
        x = pending.pop(); t = type(x)
        if t is dict:
            if any(type(k) is not str for k in x): raise TypeError('decoded string keys required')
            pending.extend(x.values())
        elif t is list: pending.extend(x)
        elif t not in (str,int,float,bool,type(None)): raise TypeError('decoded builtins only')
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def _small(x):
    t = type(x); out = {'python_type':t.__name__}
    if t in (int,float,bool,type(None)): out['value'] = x
    elif t is str:
        out['value'] = x[:128]
        if len(x)>128: out.update(value_truncated=True,length=len(x))
    elif t is dict:
        out['metadata'] = {k:_small(x[k]) for k in ('status','reason') if k in x and type(x[k]) in (str,int,float,bool,type(None))}
    elif t in (list,tuple): out['length'] = len(x)
    return out


def _api(module):
    if type(module) is not types.ModuleType: raise TypeError('caller must pass exact pure module object')
    d = vars(module); codes = set(); filename = None
    for name,line in API_LINES.items():
        f = d.get(name)
        if type(f) is not types.FunctionType or f.__globals__ is not d or f.__code__.co_name!=name or f.__code__.co_firstlineno!=line:
            raise ValueError('passed pure API shape differs: '+name)
        filename = f.__code__.co_filename if filename is None else filename
        if f.__code__.co_filename!=filename: raise ValueError('mixed pure source code')
        pending = [f.__code__]
        while pending:
            c = pending.pop(); codes.add(c)
            pending.extend(x for x in c.co_consts if type(x) is types.CodeType)
    m = d.get('Missing')
    if type(m) is not type or not issubclass(m,ValueError) or m.__name__!='Missing': raise ValueError('Missing API differs')
    if d.get('QUEUE')!=QUEUE or d.get('GROUPS')!={'legs':4,'wheels':2}: raise ValueError('queue API differs')
    return d,codes


def _event(e):
    if type(e) is not dict: return None
    return {k:_small(e[k]) for k in ('seq','kind','group','tick') if k in e}


def _frame(tb,codes):
    frame = tb.tb_frame; name = frame.f_code.co_name; loc = frame.f_locals; line = tb.tb_lineno
    out = {'function':name,'line':line}
    if name=='integer': out['integer'] = {k:_small(loc[k]) for k in ('x','low') if k in loc}
    if name=='number' and 'x' in loc: out['number_x'] = _small(loc['x'])
    if name=='field':
        key = loc.get('key'); obj = loc.get('obj'); out['field_key'] = _small(key)
        if type(obj) is dict and type(key) is str and key in obj: out['field_value'] = _small(obj[key])
    if name=='queue_state':
        if 'k' in loc: out['queue_state_current_loop_field'] = _small(loc['k'])
        if 'width' in loc: out['width'] = _small(loc['width'])
    if name=='vector':
        out['vector'] = {k:_small(loc[k]) for k in ('n','v') if k in loc}
        x = loc.get('x')
        if type(x) is list and 'v' in loc:
            out['vector']['index'] = next((i for i,a in enumerate(x) if a is loc['v']),None)
            out['vector']['index_basis'] = 'first identity match; original loop stops at first invalid scalar'
    if name=='matrix' and type(loc.get('x')) is list and 'row' in loc:
        out['matrix_row_index'] = next((i for i,a in enumerate(loc['x']) if a is loc['row']),None)
    if name=='actuation_component':
        w = loc.get('w')
        if type(w) is dict and 'control_index' in w: out['window_control_index'] = _small(w['control_index'])
        if 'idx' in loc: out['local_idx_may_precede_current_w'] = _small(loc['idx'])
        if 'group' in loc: out['group_loop'] = _small(loc['group'])
        # Frozen-source callsites, not a guess from stale locals of earlier loops.
        event_name = (None if line<=378 else 'e' if line<=381 else 'issue' if line==387 else 'sub' if line<=396 else
                      'wr' if 411<=line<=413 else 'a' if line<=425 else None)
        if event_name in loc:
            out['event_local'] = event_name; out['event'] = _event(loc[event_name])
        # Python 3.14 may restore the inlined comprehension's e while unwinding.
        # Recover only a scalar witness by ORIGINAL field.obj / integer.x identity.
        if line==378 and not out.get('event') and type(loc.get('events')) is list:
            inner=tb.tb_next; witness=None
            while inner is not None:
                fr=inner.tb_frame
                if fr.f_globals is frame.f_globals and fr.f_code in codes:
                    ls=fr.f_locals
                    if fr.f_code.co_name=='field' and ls.get('key')=='seq' and type(ls.get('obj')) is dict:
                        witness=ls['obj']; break
                    if fr.f_code.co_name=='integer' and 'x' in ls:
                        witness=next((e for e in loc['events'] if type(e) is dict and 'seq' in e and e['seq'] is ls['x']),None); break
                inner=inner.tb_next
            if witness is not None:
                out.update(event=_event(witness),event_local='recovered_seq_identity_witness',
                           event_context_basis='original field.obj or first integer.x identity; no predicate rerun')
        paths = {367:['actuation.status.dropped_events','actuation.status.observer_errors'],
                 369:['bounded_trace.actuation.control_windows_seen','bounded_trace.actuation.retained_window_bound'],
                 372:['window.control_index'],378:['event.seq'],381:['event.tick']}
        if line in paths: out['integer_callsite_fields'] = paths[line]
    elif name=='<listcomp>' and 'e' in loc:
        out['event'] = _event(loc['e'])
    return out


def locate_queue_failure(worker_final, pure_module):
    """Call unchanged actuation_component ONCE; return scalar-only original frames.
    Caller owns exact source-byte qualification. API-shape check is not authentication.
    Input must be acyclic decoded JSON builtins. No overall application status is edited.
    """
    if type(worker_final) is not dict: raise TypeError('decoded worker_final dict required')
    d,codes = _api(pure_module); before = _canonical(worker_final)
    out = {'kind':'PHASE1_QUEUE_FAILURE_SCALAR_LOCATOR_V1','status':'NO_EXCEPTION',
           'expected_pure_SHA256':PURE_SHA256,'source_binding':'CALLER_QUALIFIED_NOT_OPENED_BY_LOCATOR',
           'original_validator_called_once':False,'frames':[], 'gate1':'UNKNOWN','exact':False,'stage2_GO':False,
           'existing_application_status':'UNCHANGED_NOT_WRITTEN'}
    try:
        out['original_validator_called_once'] = True
        d['actuation_component'](worker_final)
        out['validator_status'] = 'RETURNED_NOT_ADMISSION'
    except Exception as exc:
        out['status'] = 'ORIGINAL_VALIDATOR_RAISED'
        out['validator_status'] = 'UNKNOWN' if isinstance(exc,d['Missing']) else 'CONTRADICTED' if isinstance(exc,ValueError) else 'ERROR'
        args = exc.args
        simple = all(type(x) in (str,int,float,bool,type(None)) for x in args)
        out['exception'] = {'python_type':type(exc).__name__,'args':[_small(x) for x in args[:3]]}
        if simple:
            text = str(exc); out['exception']['message'] = text[:256]
            if len(text)>256: out['exception']['message_truncated'] = True
        else: out['exception']['message'] = 'NONSCALAR_EXCEPTION_ARGS_NOT_EXPORTED'
        tb = exc.__traceback__; matched = 0
        while tb is not None:
            if tb.tb_frame.f_globals is d and tb.tb_frame.f_code in codes:
                matched += 1
                if len(out['frames'])<12: out['frames'].append(_frame(tb,codes))
            tb = tb.tb_next
        out['pure_frames_omitted'] = max(0,matched-len(out['frames']))
    finally:
        after = _canonical(worker_final)
        out.update(canonical_before_SHA256=before,canonical_after_SHA256=after,input_unchanged=before==after)
        if before!=after: out['status'] = 'INPUT_CHANGED_NO_REPAIR'
    return out
