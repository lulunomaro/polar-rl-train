"""Parse already-collected original RSL text; no checkpoint, raw trace, remote or GPU access."""
from pathlib import Path
import math,re,statistics
ANSI=re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
ITER=re.compile(r'Learning iteration\s+(\d+)\s*/\s*(\d+)')
COLLECT=re.compile(r'Collection time:\s*([0-9.eE+-]+)s')
LEARN=re.compile(r'Learning time:\s*([0-9.eE+-]+)s')
ITERTIME=re.compile(r'Iteration time:\s*([0-9.eE+-]+)s')

def percentile(values,p):
    a=sorted(values);assert a and 0<=p<=1
    at=(len(a)-1)*p;lo=int(at);hi=min(lo+1,len(a)-1)
    return a[lo]*(hi-at)+a[hi]*(at-lo) if hi!=lo else a[lo]

def summarize(values):
    assert values and all(math.isfinite(x) and x>0 for x in values)
    return dict(n=len(values),median=statistics.median(values),q25=percentile(values,.25),
                q75=percentile(values,.75),minimum=min(values),maximum=max(values))

def read_worker_log(path,expected_updates,warmup=2):
    rows=[];current=None
    with Path(path).open(encoding='utf8',errors='strict') as f:
        for raw in f:
            line=ANSI.sub('',raw)
            if match:=ITER.search(line):
                if current is not None:rows.append(current)
                current=dict(global_iteration=int(match[1]),target_iteration=int(match[2]))
            elif current is not None:
                for pattern,key in [(COLLECT,'collection_seconds'),(LEARN,'PPO_seconds'),(ITERTIME,'iteration_seconds_printed')]:
                    if match:=pattern.search(line):current[key]=float(match[1])
    if current is not None:rows.append(current)
    assert len(rows)==expected_updates,(str(path),len(rows),expected_updates)
    for i,row in enumerate(rows,1):
        assert {'collection_seconds','PPO_seconds'}<=set(row)
        assert row['collection_seconds']>0 and row['PPO_seconds']>0
        row['owned_update']=i;row['environment_transitions']=20000*24
        row['cycle_seconds']=row['collection_seconds']+row['PPO_seconds']
        if 'iteration_seconds_printed' in row:assert abs(row['cycle_seconds']-row['iteration_seconds_printed'])<=.025
        row['collection_envsteps_per_second']=row['environment_transitions']/row['collection_seconds']
        row['cycle_envsteps_per_second']=row['environment_transitions']/row['cycle_seconds']
    measured=rows[warmup:];assert measured
    return dict(path=str(path),all_complete_update_rows=rows,excluded_first_warmup_updates=warmup,
                measured_updates=len(measured),collection_seconds=summarize([x['collection_seconds'] for x in measured]),
                PPO_seconds=summarize([x['PPO_seconds'] for x in measured]),
                cycle_seconds=summarize([x['cycle_seconds'] for x in measured]),
                collection_envsteps_per_second=summarize([x['collection_envsteps_per_second'] for x in measured]),
                cycle_envsteps_per_second=summarize([x['cycle_envsteps_per_second'] for x in measured]),
                weighted_cycle_envsteps_per_second=sum(x['environment_transitions'] for x in measured)/sum(x['cycle_seconds'] for x in measured),
                units='20000 environments x24 control transitions per update; not single-environment Hz or aggregate physics callback rate',
                source='Original RSL printed CPU wall timing; includes implicit GPU synchronization; excludes owner waiting/receipt accounting tail',
                not_fixed_input_causal_benchmark=True)
