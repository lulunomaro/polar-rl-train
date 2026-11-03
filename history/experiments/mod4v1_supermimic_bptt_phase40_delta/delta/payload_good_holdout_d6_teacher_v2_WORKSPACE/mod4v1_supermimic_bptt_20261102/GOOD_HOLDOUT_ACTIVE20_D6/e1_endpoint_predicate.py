"""Originaltwo-wheel orderedcontactendpoints, cohort80. No populationgate."""
class EndpointPredicate:
    def __init__(self,edge,n=80):
        assert n==80 and edge in (.275,1.2);self.edge=edge;self.first_failure=[None]*n;self.segments=[{} for _ in range(n)]
    def observe(self,control,episodes,wheel_u,support,terminated):
        assert len(episodes)==len(wheel_u)==len(support)==len(terminated)==80
        for i in range(80):
            if terminated[i] and self.first_failure[i] is None:self.first_failure[i]=control
            if self.first_failure[i] is not None or i%3==2:continue
            s=self.segments[i].setdefault(int(episodes[i]),dict(first=control,last=control,before=[],after=[],contact_before=[],contact_after=[]));s['last']=control
            b=max(wheel_u[i]) < -self.edge if i%3==0 else min(wheel_u[i])>self.edge
            a=min(wheel_u[i]) > self.edge if i%3==0 else max(wheel_u[i])< -self.edge
            if b:s['before'].append(control)
            if a:s['after'].append(control)
            if b and all(support[i]):s['contact_before'].append(control)
            if a and all(support[i]):s['contact_after'].append(control)
    def finish(self):
        rows=[]
        for i in range(80):
            ep=[]
            for number,s in self.segments[i].items():
                ok=bool(s['before'] and s['after'] and min(s['before'])<max(s['after']))
                contact=bool(ok and s['contact_before'] and s['contact_after'] and min(s['contact_before'])<max(s['contact_after']))
                ep.append(dict(episode=number,first_control=s['first'],last_control=s['last'],full_route_complete=ok,original1N_contact_confirmed=contact))
            rows.append(dict(env=i,group=('ascending','descending','stand')[i%3],crossing_required=i%3!=2,first_ordinary_failure_control=self.first_failure[i],complete=any(x['full_route_complete'] for x in ep),contact_confirmed=any(x['original1N_contact_confirmed'] for x in ep),segments=ep))
        return dict(groups={g:dict(environments=sum(x['group']==g for x in rows),complete_envs=sum(x['group']==g and x['complete'] for x in rows),contact_confirmed_envs=sum(x['group']==g and x['contact_confirmed'] for x in rows)) for g in ('ascending','descending','stand')},rows=rows,standing_not_required_to_cross=True,all_valid_failed_incomplete_prefixes_retained=True,no_new_aggregate_graduation_rate=True)


def support_from_8(force_z):
    assert len(force_z)==8
    return sum(max(0.,float(x)) for x in force_z)*.0025/.02>1.
