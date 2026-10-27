"""Only already-recorded own PID/create probes; never enumerate unknown peers."""
import math
ROLES=('owner','h1_node','h1_worker','recovery_node','recovery_worker')
def validate_rows(rows):
    if not isinstance(rows,list) or [r.get('role') for r in rows]!=list(ROLES):
        raise ValueError('exact five recorded original own process identities required')
    if len({r['pid'] for r in rows})!=5:raise ValueError('duplicate original own PID')
    for r in rows:
        if set(r)!={'role','pid','creation'} or type(r['pid']) is not int or r['pid']<=0:
            raise ValueError('bad own PID row')
        if type(r['creation']) not in (float,int) or not math.isfinite(r['creation']) or r['creation']<=0:
            raise ValueError('bad original creation time')
    return rows
def records_from_evidence(values):
    detached=values['detached'];first=values['first_identity']
    if detached['run_id']!=first['run_id']:raise ValueError('identity run mismatch')
    owner=detached['owner_identity'];rows=[dict(role='owner',pid=owner['pid'],creation=owner['creation'])]
    for key in ('h1','recovery'):
        t=first['targets'][key]
        if not t['passed_live_identity'] or not t['node_identity']['passed'] or not t['worker_identity']['passed']:
            raise ValueError('actual original own identity proof absent')
        for kind,x in [('node',t['node_identity']['actual']),('worker',t['worker_identity']['actual'])]:
            rows.append(dict(role=key+'_'+kind,pid=x['pid'],creation=x['creation']))
    return validate_rows(rows)
def assert_recorded_own_out(rows,process_factory,no_such_process,*,execution_backend):
    validate_rows(rows);observed=[]
    if execution_backend not in ('target72','source210'):raise ValueError('exact selected execution backend required')
    for r in rows:
        row_backend='source210' if r['role'].startswith('h1_') else 'target72'
        if row_backend!=execution_backend:continue
        try:p=process_factory(r['pid']);creation=p.create_time()
        except no_such_process:
            observed.append(dict(role=r['role'],actual_original_process_out=True));continue
        if creation==r['creation']:
            raise ValueError('original owned process still present: '+r['role'])
        # Recycled PID is not ours. No exe/name/cwd/argv/status query.
        observed.append(dict(role=r['role'],original_process_out_PID_recycled=True,
                             foreign_argv_or_identity_not_queried=True))
    return dict(passed=True,records=observed,no_process_enumeration=True,no_cmdline_query=True)

