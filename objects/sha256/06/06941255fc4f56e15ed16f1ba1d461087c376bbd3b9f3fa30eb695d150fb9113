"""MOD4 geometry measured from this STEP, in metres, never the older assembly."""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).parent
PARTS=json.loads((ROOT/'reports/cad_parts.json').read_text(encoding='utf8'))
ROT=np.array([[0.,0.,-1.],[-1.,0.,0.],[0.,1.,0.]])

def cylinder(i,r,near=None):
    cs=[c for c in PARTS[i]['cylinders'] if abs(c['r']-r)<1e-4 and abs(c['axis'][0])>.99999]
    if near is not None:cs.sort(key=lambda c:np.linalg.norm(np.array(c['p'])[1:]-np.array(near)[1:]))
    assert cs,(i,r)
    return np.array(cs[0]['p'])

O=cylinder(144,24.55)
O[0]=.5*(PARTS[144]['com_mm'][0]+PARTS[235]['com_mm'][0])
PINS={}
for side,offset,wheel in [('right',0,183),('left',91,276)]:
    ids=dict(thigh=144+offset,shin=134+offset,input=119+offset,coupler=120+offset,
             rocker=124+offset,distal=129+offset,gas_inner=148+offset,gas_barrel=149+offset,wheel=wheel)
    p={'O':cylinder(ids['thigh'],24.55),'K':cylinder(ids['thigh'],23.525),
       'P':cylinder(ids['thigh'],5.5),'A':cylinder(ids['input'],6.05),
       'D':cylinder(ids['shin'],6.05),'W':cylinder(wheel,62.5),
       'S':cylinder(ids['gas_inner'],4),'T':cylinder(ids['gas_barrel'],5.5)}
    p['B']=cylinder(ids['coupler'],5.025,max([np.array(c['p']) for c in PARTS[ids['coupler']]['cylinders'] if abs(c['r']-5.025)<1e-4],key=lambda t:np.linalg.norm(t-p['A'])))
    p['C']=max([np.array(c['p']) for c in PARTS[ids['rocker']]['cylinders'] if abs(c['r']-6.05)<1e-4],key=lambda t:min(np.linalg.norm(t-p['B']),np.linalg.norm(t-p['P'])))
    PINS[side]={k:(ROT@(v-O)*.001)[[0,2]] for k,v in p.items()}

def rotate(v,q):
    c,s=np.cos(q),np.sin(q)
    return np.array([[c,s],[-s,c]])@v

def angle(v,w):
    q=-(np.arctan2(w[1],w[0])-np.arctan2(v[1],v[0]))
    return (q+np.pi)%(2*np.pi)-np.pi

def intersect(a,ra,b,rb,sign):
    length=np.linalg.norm(b-a)
    if not abs(ra-rb)+1e-7<length<ra+rb-1e-7:raise ValueError('Linkage singularity or unreachable pose')
    t=(ra*ra-rb*rb+length*length)/(2*length)
    h=np.sqrt(ra*ra-t*t);x=(b-a)/length;y=np.array([-x[1],x[0]])
    return a+t*x+sign*h*y

def configuration(hip,difference,side='right',reference=None):
    p=PINS[side] if reference is None else reference
    L=lambda a,b:np.linalg.norm(p[a]-p[b])
    q={k:rotate(v,hip) for k,v in p.items()}
    q['A']=rotate(p['A'],hip+difference)
    cross=lambda a,b:a[0]*b[1]-a[1]*b[0]
    q['B']=intersect(q['A'],L('A','B'),q['P'],L('B','P'),np.sign(cross(p['P']-p['A'],p['B']-p['A'])))
    rocker=angle(p['B']-p['P'],q['B']-q['P'])
    q['C']=q['P']+rotate(p['C']-p['P'],rocker)
    q['D']=intersect(q['K'],L('K','D'),q['C'],L('C','D'),np.sign(cross(p['C']-p['K'],p['D']-p['K'])))
    shin=angle(p['D']-p['K'],q['D']-q['K'])
    for key in ['W','T']:q[key]=q['K']+rotate(p[key]-p['K'],shin)
    vals={'hip':hip,'crank':hip+difference,'rocker_pin':rocker-hip,
          'coupler_pin':angle(p['B']-p['A'],q['B']-q['A'])-hip-difference,
          'knee':shin-hip,'distal_pin':angle(p['D']-p['C'],q['D']-q['C'])-rocker,
          'gas_pin':angle(p['T']-p['S'],q['T']-q['S'])-hip,
          'gas_slide':L('T','S')*0+np.linalg.norm(q['T']-q['S'])-L('T','S'),
          'drive_hip_spin':hip,'drive_input_spin':hip+difference,'wheel_spin':0.}
    for name in ['rocker_pin','coupler_pin','knee','distal_pin','gas_pin']:
        vals[name]=(vals[name]+np.pi)%(2*np.pi)-np.pi
    return vals,q

if __name__=='__main__':
    print('origin',O,'bilateral pin difference',max(np.linalg.norm(PINS['left'][k]-PINS['right'][k]) for k in PINS['right']))
    for a,b in [('O','K'),('K','W'),('O','A'),('A','B'),('P','B'),('P','C'),('C','D'),('K','D'),('S','T')]:print(a+b,np.linalg.norm(PINS['right'][a]-PINS['right'][b]))
    for diff in np.arange(-.9,1.,.1):
        try:
            v,p=configuration(0.,diff)
            print('difference',round(diff,3),'knee',round(np.rad2deg(v['knee']),3),'length',round(np.linalg.norm(p['W']),4),'gaslen',round(np.linalg.norm(p['S']-p['T']),4))
        except ValueError:pass
