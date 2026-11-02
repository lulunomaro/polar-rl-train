"""Read public nominal XML/MCI only; export small mesh-free constants.
No MuJoCo/SDK import, no episode/randomized model or source modification.
"""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;TASK=R.parent
XML=TASK/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'
PINS=TASK.parent/'traditional_control_20261101/reports/model_manifest.json'
KIN=TASK.parent/'traditional_control_20261101/kinematics.py'
GAIN=TASK/'nominal_gain_v1.json'
EXPECTED='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(s,default):return list(map(float,(s if s is not None else default).split()))
def main():
    assert sha(XML)==EXPECTED
    target=R/'PUBLIC_NOMINAL_CONSTANTS.json';assert not target.exists()
    doc=ET.parse(XML).getroot();base_defaults=doc.find('default/joint').attrib.copy();bodies=[];joints=[];sites=[]
    def body(e,parent):
        name=e.attrib['name'];ii=e.find('inertial');assert ii is not None
        b={'name':name,'parent':parent,'pos_m':arr(e.get('pos'),'0 0 0'),'quat_wxyz':arr(e.get('quat'),'1 0 0 0'),'mass_kg':float(ii.attrib['mass']),'com_local_m':arr(ii.get('pos'),'0 0 0'),'inertia_full_body':arr(ii.get('fullinertia'),'0 0 0 0 0 0'),'joint_names':[]}
        assert ii.get('fullinertia') is not None,'Export must explicitly handle inertia orientation instead of guessing'
        bodies.append(b)
        for j in e.findall('joint'):
            a={**base_defaults,**j.attrib};jn=a['name'];limited=a.get('limited','auto')!='false' and 'range' in a
            record={'name':jn,'body':name,'type':a.get('type','hinge'),'axis':arr(a.get('axis'),'0 0 1'),'pos_m':arr(a.get('pos'),'0 0 0'),'range_rad_or_m':arr(a.get('range'),'0 0') if limited else None,'limited':limited,'damping':float(a.get('damping',0)),'armature':float(a.get('armature',0)),'stiffness_N_per_m':float(a.get('stiffness',0)),'springref_m':float(a.get('springref',0)),'frictionloss':float(a.get('frictionloss',0))}
            joints.append(record);b['joint_names'].append(jn)
        for s in e.findall('site'):sites.append({'name':s.get('name'),'body':name,'pos_m':arr(s.get('pos'),'0 0 0')})
        for child in e.findall('body'):body(child,name)
    root=doc.find("worldbody/body[@name='chassis']");body(root,None)
    gain=json.loads(GAIN.read_text(encoding='utf-8'))['gain'];q=gain['q'];tau=gain['tau']
    assert len(bodies)==31 and len(joints)==30
    export={'schema':'public_nominal_contact_proxy_v1','source_xml_sha256':EXPECTED,'source_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [XML,PINS,KIN,GAIN]],'units':'SI; radians; fullinertia Ixx Iyy Izz Ixy Ixz Iyz in authored body frame','runtime_frame':'chassis body coordinates; exported root world pos discarded in FK','bodies':bodies,'joints':joints,'sites':sites,'pins_xz_m':json.loads(PINS.read_text(encoding='utf-8'))['neutral_skeleton_xz_m'],'actuators':[dict(a.attrib) for a in doc.findall('actuator/motor')],'total_nominal_mass_kg':sum(b['mass_kg'] for b in bodies),'nominal_q4':[q[3],q[3]+q[4],q[5],q[5]+q[6]],'nominal_ff_tau4':[tau[i] for i in [0,1,3,4]],'nominal_proper_root_B':[0.,0.,9.81],'no_runtime_DR_override_api':True,'known_omission':'wheel spin angle/rate/acceleration not observed by requested4encoder interface; wheel rotational load omitted, tiny off-axis wheelCOM phase held0; not full RNE'}
    raw=json.dumps(export,ensure_ascii=False,indent=2,allow_nan=False)+'\n';target.write_text(raw,encoding='utf-8')
    print(json.dumps({'file':str(target),'sha256':sha(target),'bodies':len(bodies),'joints':len(joints),'mass':export['total_nominal_mass_kg'],'q4':export['nominal_q4'],'ff_tau4':export['nominal_ff_tau4']},indent=2))
if __name__=='__main__':main()
