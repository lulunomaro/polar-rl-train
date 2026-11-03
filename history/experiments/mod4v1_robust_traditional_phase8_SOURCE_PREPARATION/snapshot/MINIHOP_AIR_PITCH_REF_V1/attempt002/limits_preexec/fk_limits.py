"""Pure inspected public FK AST and authoritative XML limits, no model import."""
from pathlib import Path
import ast,hashlib,json,math,sys,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parent.parent;O=R.parent/'traditional_control_20261101'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class PublicFK:
    def __init__(self):
        p=O/'kinematics.py';tree=ast.parse(p.read_text(encoding='utf-8'))
        names={'rotate','angle','intersect','leg_configuration'}
        selected=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
        assert {n.name for n in selected}==names
        self.ast_SHA=hashlib.sha256(ast.dump(ast.Module(body=selected,type_ignores=[]),include_attributes=False).encode()).hexdigest()
        manifest=json.loads((O/'reports/model_manifest.json').read_bytes())
        pins={s:{k:np.array(v,float)for k,v in p.items()}for s,p in manifest['neutral_skeleton_xz_m'].items()}
        env={'np':np,'PINS':pins}
        exec(compile(ast.Module(body=selected,type_ignores=[]),str(p),'exec'),env)
        self.leg=env['leg_configuration'];self.rotate=env['rotate'];self.pins=pins
        self.params=json.loads((O/'model_parameters.json').read_bytes())
        xml=ET.fromstring((R/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml').read_bytes())
        self.limits={j.get('name'):tuple(map(float,j.get('range').split()))for j in xml.find('worldbody').iter('joint')if j.get('limited')=='true'}
    def check(self,q4):
        q=np.asarray(q4,float);assert q.shape==(4,)and np.isfinite(q).all()
        violations=[];minmargin={};cfg={};points={}
        for j,side in enumerate(('left','right')):
            hip=float(q[2*j]);delta=float(q[2*j+1]-hip)
            lo,hi=self.params['limits'][side]['input_difference_rad'];margin=min(delta-lo,hi-delta)
            minmargin[side+'_input_difference']=margin
            if margin<0:violations.append(dict(joint=side+'_input_difference',value=delta,lo=lo,hi=hi,excess=-margin))
            values,pp=self.leg(hip,delta,side=side)
            assert all(math.isfinite(float(x))for x in values.values())
            assert all(np.isfinite(x).all()for x in pp.values())
            cfg[side]=values;points[side]=pp
            for name,value in values.items():
                full=side+'_'+name
                if full in self.limits:
                    lo,hi=self.limits[full];margin=min(float(value)-lo,hi-float(value));minmargin[full]=margin
                    if margin<0:violations.append(dict(joint=full,value=float(value),lo=lo,hi=hi,excess=-margin))
        return dict(violations=violations,minmargin=minmargin,config=cfg,points=points)
    def offset_grid(self,low,high,count=51):
        g=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch'];z=g['q']
        q0=np.array([z[3],z[3]+z[4],z[5],z[5]+z[6]])
        baseline=self.check(q0);rows=[];margins={};maxrot=0.;maxdelta=0.;maxsym=0.;failures=0
        for h in np.linspace(low,high,count):
            q=q0+float(h)*np.ones(4);item=dict(h=float(h),q4=q.tolist())
            try:
                x=self.check(q)
                de=max(abs(float(q[1]-q[0])-float(q0[1]-q0[0])),abs(float(q[3]-q[2])-float(q0[3]-q0[2])))
                re=max(float(np.max(np.abs(pp-self.rotate(baseline['points'][side][name],h))))for side in ('left','right')for name,pp in x['points'][side].items())
                sy=float(np.max(np.abs(q[:2]-q[2:])))
                maxrot=max(maxrot,re);maxdelta=max(maxdelta,de);maxsym=max(maxsym,sy)
                for n,v in x['minmargin'].items():margins[n]=min(margins.get(n,math.inf),v)
                item.update(FK_finite=True,delta_error_rad=de,common_rotation_error_m=re,L_R_reference_difference_rad=sy,violations=x['violations'],within_limits=not x['violations'])
            except (ValueError,AssertionError,FloatingPointError)as error:
                failures+=1;item.update(FK_finite=False,within_limits=False,violations=None,FK_error=repr(error))
            rows.append(item)
        bad=[r for r in rows if not r['within_limits']]
        mathpass=failures==0 and maxrot<=1e-11 and maxdelta<=1e-12 and maxsym==0.
        return dict(kind='PURE_PUBLIC_FK_AND_UNRELAXED_AUTHORITATIVE_LIMIT_GATE',interval=[low,high],offsets=count,rows=rows,
            violating_offset_count=len(bad),FK_failures=failures,math_gate_pass=mathpass,limits_gate_pass=not bad,
            minimum_joint_margins=margins,max_common_rotation_error_m=maxrot,max_delta_error_rad=maxdelta,max_L_R_reference_difference_rad=maxsym,
            FK_selected_function_AST_SHA=self.ast_SHA,source_limits_not_modified=True,model_boots=0,forward_calls=0,integrator_calls=0,
            physics_module_imported='mujoco'in sys.modules,raw_reads=0,PH7_pending=True)
