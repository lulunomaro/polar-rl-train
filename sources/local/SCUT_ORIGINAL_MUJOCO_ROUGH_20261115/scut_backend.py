"""Original SCUT inference backend for the project's existing WASD MuJoCo player.
The terrain meshes and control window are reused, and production MOD4 stays separate.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse, hashlib, json, math, struct, sys, time, xml.etree.ElementTree as ET
import mujoco, mujoco.viewer, numpy as np, torch, yaml

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[3]
VIEWER = WORKSPACE / '_mod4v2_src_20261106/deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/viewer'
REF = WORKSPACE / 'refs/wheeled-legged_RL-main/pretrained/26_infantry'
PLANT = WORKSPACE / 'refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/wheelbipeV14_2.xml'
DEFAULT_RUN = REF / 'rough_rotation_stair/2026-07-23_16-23-21'
CHECKPOINT = DEFAULT_RUN / 'model_1000.pt'
sys.path.insert(0, str(VIEWER))
import showcase
FAMILIES, CN = showcase.FAMILIES, showcase.CN
RUNTIME = HERE / 'runtime'
RUNTIME.mkdir(exist_ok=True)
torch.set_num_threads(1)


def checksum(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_actor(checkpoint):
    data = torch.load(checkpoint, map_location='cpu', weights_only=False)
    sd = data['model_state_dict']
    keys = sorted((k for k in sd if k.startswith('actor.') and k.endswith('.weight')), key=lambda k: int(k.split('.')[1]))
    layers = []
    for i, k in enumerate(keys):
        layer = torch.nn.Linear(sd[k].shape[1], sd[k].shape[0])
        layer.weight.data.copy_(sd[k]); layer.bias.data.copy_(sd[k.replace('weight', 'bias')])
        layers.append(layer)
        if i + 1 < len(keys): layers.append(torch.nn.ELU())
    assert sd[keys[0]].shape[1] == 35 and sd[keys[-1]].shape[0] == 6
    return torch.nn.Sequential(*layers).eval(), data['iter']


def mesh_file(tile):
    dest = RUNTIME / (tile + '.msh')
    if not dest.exists():
        a = np.load(VIEWER / 'tiles' / (tile + '.npz'))
        v, f = a['vertices'], a['faces']
        if np.ptp(v[:, 2]) < 1e-7:
            n = len(v)
            v = np.vstack((v, [[0,0,-.02],[.01,0,-.02],[0,.01,-.02],[0,0,-.03]]))
            f = np.vstack((f, [[n,n+1,n+2],[n,n+3,n+1],[n,n+2,n+3],[n+1,n+3,n+2]]))
        with dest.open('wb') as h:
            h.write(struct.pack('<4i', len(v), 0, 0, len(f)))
            h.write(v.astype('<f4').tobytes()); h.write(f.astype('<i4').tobytes())
    return dest


def heightfield(tile):
    for cached in (RUNTIME / (tile+'_hf_v2.npz'), VIEWER / (tile+'_hf_v2.npz')):
        if cached.exists(): return np.load(cached)['h']
    path = mesh_file(tile)
    m = mujoco.MjModel.from_xml_string(f'<mujoco><asset><mesh name="t" file="{path.as_posix()}"/></asset><worldbody><geom type="mesh" mesh="t"/></worldbody></mujoco>')
    d = mujoco.MjData(m); mujoco.mj_forward(m, d)
    grid = np.linspace(-4.5, 4.5, 181); h = np.zeros((181,181))
    vec = np.array([0.,0.,-1.]); p = np.array([0.,0.,10.]); gid = np.zeros(1, dtype=np.int32)
    for iy,y in enumerate(grid):
        for ix,x in enumerate(grid):
            p[:2] = np.clip([x+1.7e-5,y+2.9e-5], -4.5+1e-4, 4.5-1e-4)
            dist = mujoco.mj_ray(m,d,p,vec,None,True,-1,gid)
            if dist < 0: raise RuntimeError(f'Ground ray miss {tile} {x} {y}')
            h[iy,ix] = 10-dist
    np.savez_compressed(RUNTIME / (tile+'_hf_v2.npz'), h=h)
    return h


def make_scene(level, family):
    tile, v, f = showcase.tiledata(level, family)
    root = ET.parse(PLANT).getroot()
    root.set('model', 'SCUT original V14_2 | project Rough-v1 terrain | WASD')
    for el in root.findall('.//mesh'):
        el.set('file', str((PLANT.parent / el.get('file')).resolve()))
    ET.SubElement(root, 'option', timestep='.001', integrator='Euler', solver='Newton', iterations='100', tolerance='1e-8', gravity='0 0 -9.81')
    visual = ET.SubElement(root, 'visual')
    ET.SubElement(visual,'headlight', ambient='.35 .35 .35', diffuse='.55 .55 .55', specular='.08 .08 .08')
    ET.SubElement(visual,'global', offwidth='1280', offheight='800')
    ET.SubElement(visual,'map', znear='.001', zfar='20')
    ET.SubElement(root, 'statistic', center='0 0 .3', extent='10')
    world = root.find('worldbody'); asset = root.find('asset')
    ET.SubElement(asset,'texture',type='skybox',builtin='gradient',rgb1='.20 .28 .40',rgb2='.07 .10 .15',width='512',height='3072')
    ET.SubElement(world, 'light', pos='0 0 5', dir='0 0 -1', directional='true')
    ET.SubElement(asset,'mesh',name='tile_visual',file=str(mesh_file(tile)))
    ET.SubElement(world,'geom',type='mesh',mesh='tile_visual',contype='0',conaffinity='0',rgba=showcase.COLORS[FAMILIES.index(family)],group='3')
    h = None
    # Exactly the existing player's collision reconstruction: boxes for broad stairs,
    # sampled heightfields for the other saved Isaac terrain families.
    if family in (FAMILIES[0], FAMILIES[4]):
        ET.SubElement(world,'geom',name='ground',type='box',pos='0 0 -.10',size='4.5 4.5 .1',contype='1',conaffinity='1',group='5',friction='1 .01 .01')
        for k,z in enumerate(np.unique(v[:,2])):
            if z <= 1e-6: continue
            top=v[v[:,2]>=z-1e-6]; lo=top[:,:2].min(0); hi=top[:,:2].max(0)
            center=(lo+hi)*.5; half=(hi-lo)*.5
            ET.SubElement(world,'geom',name=f'step_{k}',type='box',pos=f'{center[0]} {center[1]} {z/2}',size=f'{half[0]} {half[1]} {z/2}',contype='1',conaffinity='1',group='5',friction='1 .01 .01')
    else:
        h=heightfield(tile); mn=float(h.min()); span=max(float(np.ptp(h)),.001)
        ET.SubElement(asset,'hfield',name='tile_collision',nrow='181',ncol='181',size=f'4.5 4.5 {span} .2')
        ET.SubElement(world,'geom',name='ground',type='hfield',hfield='tile_collision',pos=f'0 0 {mn}',contype='1',conaffinity='1',group='5',friction='1 .01 .01')
    path=RUNTIME / f'scene_{tile}.xml'
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
    m=mujoco.MjModel.from_xml_path(str(path))
    if h is not None: m.hfield_data[:]=(h-h.min()).ravel()/max(float(np.ptp(h)),.001)
    return m,v,h


class SCUTReplay:
    """Simulation protocol consumed by the already existing ManualRoughControl."""
    def __init__(self,level=0,family=FAMILIES[0],direction='up',show=False):
        self.level,self.family,self.direction=level,family,direction
        self.args=SimpleNamespace(vx=1.,wz=1.5,height_rate=.1,action_smoothing=False,device='cpu')
        self.height=.28; self.paused=True; self.viewer=None
        self.cmd_vx=self.cmd_vy=self.cmd_wz=0.
        self.reason=''; self.reset_count=0; self.closure=0.; self.max_closure=0.
        self.auto_fall=False
        self.model,self.iteration=load_actor(CHECKPOINT)
        self.checkpoint_sha=checksum(CHECKPOINT)
        self.cfg=yaml.load((CHECKPOINT.parent/'params/env.yaml').read_text(encoding='utf-8'),Loader=yaml.BaseLoader)
        self.m,self.vertices,self.h=make_scene(level,family)
        self.d=mujoco.MjData(self.m)
        self.env=SimpleNamespace(m=self.m,d=self.d,vx=0.)
        # The joint order is the published SCUT ROS2 normal-policy deployment order.
        self.names=['left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint']
        self.qadr=np.array([self.m.jnt_qposadr[self.m.joint(n).id] for n in self.names])
        self.vadr=np.array([self.m.jnt_dofadr[self.m.joint(n).id] for n in self.names])
        self.ctrl=np.array([self.m.actuator(n+'_ctrl').id for n in self.names])
        self.spring_names=['left_spring2_joint','right_spring2_joint']
        self.spring_qadr=np.array([self.m.jnt_qposadr[self.m.joint(n).id] for n in self.spring_names])
        self.spring_vadr=np.array([self.m.jnt_dofadr[self.m.joint(n).id] for n in self.spring_names])
        self.spring_ctrl=np.array([self.m.actuator(n+'_ctrl').id for n in self.spring_names])
        self.base=self.m.body('base_link').id
        self.wheel_bids=[self.m.body(n).id for n in ('left_wheel_link','right_wheel_link')]
        self.jump_remaining=0; self.jump_elapsed=0.; self.jump_requests=0
        self.last_jump='尚未触发'; self.jump_log=[]; self.jump_airborne=False
        self._jump_start_z=0.; self._jump_peak_z=0.; self._jump_start_vx=0.
        self.action=np.zeros(6); self.observation=np.zeros(35)
        self.reset_standing()
        if show:
            self.viewer=mujoco.viewer.launch_passive(self.m,self.d)
            self.viewer.cam.distance=3.;self.viewer.cam.azimuth=90.;self.viewer.cam.elevation=-16.
            self.viewer.opt.geomgroup[3]=1;self.viewer.opt.geomgroup[5]=0
        print('SCUT_SIM_READY',json.dumps(dict(checkpoint=str(CHECKPOINT),sha256=self.checkpoint_sha,iteration=self.iteration,plant=str(PLANT),family=family,level=level,obs=35,actions=6,physics_dt=.001,policy_dt=.02,joint_order=self.names)),flush=True)

    ground=showcase.Replay.ground

    def set_height(self,value): self.height=float(np.clip(value,.20,.42))
    def toggle_pause(self): self.paused=not self.paused
    def close(self):
        if self.viewer is not None: self.viewer.close(); self.viewer=None
    def reset_standing(self):
        mujoco.mj_resetData(self.m,self.d)
        x=.25 if self.direction=='down' else -3.7
        if self.family==FAMILIES[8]: x=-2.
        self.d.qpos[:3]=[x,0,self.ground(x,0)+.18483]
        self.d.qpos[3:7]=[1,0,0,0]
        self.d.qvel[:]=0.;self.d.time=0.
        mujoco.mj_forward(self.m,self.d)
        self.action=np.zeros(6);self._filtered_action=None
        self.cmd_vx=self.cmd_vy=self.cmd_wz=0.
        self.jump_remaining=0;self.jump_elapsed=0.
        self.reset_count+=1;self._update_state()

    def _update_state(self):
        R=self.d.xmat[self.base].reshape(3,3)
        self.z=float(self.d.qpos[2]-self.ground(*self.d.qpos[:2]))
        self.cos_tilt=float(R[2,2]);self.env.vx=float((R.T@self.d.qvel[:3])[0])
        errors=[]
        for i in range(self.m.neq):
            a,b=int(self.m.eq_obj1id[i]),int(self.m.eq_obj2id[i])
            pa=self.d.xpos[a]+self.d.xmat[a].reshape(3,3)@self.m.eq_data[i,:3]
            pb=self.d.xpos[b]+self.d.xmat[b].reshape(3,3)@self.m.eq_data[i,3:6]
            errors.append(float(np.linalg.norm(pa-pb)))
        self.closure=max(errors,default=0.)
        self.max_closure=max(self.max_closure,self.closure)

    def trigger_jump(self):
        if self.jump_remaining: return
        self.jump_remaining=25;self.jump_elapsed=0.;self.jump_requests+=1
        self._jump_start_z=float(self.d.qpos[2]);self._jump_peak_z=self._jump_start_z
        self._jump_start_vx=self.env.vx;self.jump_airborne=False
        self.last_jump='已发跳跃模式指令；等待实测离地'
        print('SPACE_JUMP_REQUEST',json.dumps(dict(t=self.d.time,vx_command=self.cmd_vx,vx=self.env.vx,window_steps=25,external_impulse=False,policy_jump_training_enabled=self.cfg.get('jump_takeoff_state_machine_cfg',{}).get('enabled'))),flush=True)

    def telemetry(self):
        return dict(t=float(self.d.time),vx=self.env.vx,cmd_vx=self.cmd_vx,z=self.z,closure=self.closure,jump_remaining=self.jump_remaining)

    def step(self,pressed):
        if self.paused:return self.telemetry()
        self.cmd_vx=(('w'in pressed)-('s'in pressed))*self.args.vx
        self.cmd_wz=(('a'in pressed)-('d'in pressed))*self.args.wz
        self.set_height(self.height+(('e'in pressed)-('q'in pressed))*.02*.1)
        R=self.d.xmat[self.base].reshape(3,3)
        q=self.d.qpos[self.qadr].copy();q[-2:]=0.
        qd=self.d.qvel[self.vadr]
        mode=np.array([1.,0.,0.,0.,0.,0.,0.])
        if self.jump_remaining: mode[:]=[0,0,0,0,1,.70*5.,self.jump_elapsed]
        self.observation=np.concatenate(([self.cmd_vx,0.,self.cmd_wz,self.height*5.], self.d.qvel[3:6]*.5, R.T@np.array([0.,0.,-1.]),q,qd*.1,self.action,mode)).astype(np.float32)
        with torch.inference_mode(): action=self.model(torch.from_numpy(self.observation)).numpy()
        if not np.isfinite(action).all(): raise RuntimeError('Non-finite SCUT actor output')
        action=np.clip(action,-100.,100.)

        if self.cfg.get('use_action_low_pass_filter')=='true':
            prev=float(self.cfg.get('action_low_pass_prev_weight',.2)); curr=float(self.cfg.get('action_low_pass_curr_weight',.8))
            action=action if self._filtered_action is None else prev*self._filtered_action+curr*action
            self._filtered_action=action.copy()
        self.action=action.copy()
        target=action[:4]*.5;wheel=action[4:]*10.
        for sub in range(20):
            q=self.d.qpos[self.qadr];qd=self.d.qvel[self.vadr]
            self.d.ctrl[self.ctrl[:4]]=np.clip(60.*(target-q[:4])-2.*qd[:4],-40.,40.)
            self.d.ctrl[self.ctrl[4:]]=np.clip(.2*(wheel-qd[4:]),-5.,5.)
            stroke=self.d.qpos[self.spring_qadr]
            settings=self.cfg['spring_settings']
            spring_length=np.maximum(float(settings['spring_offset'])-stroke,0.)
            spring_force=float(settings['linear_down'])+(float(settings['linear_up'])-float(settings['linear_down']))/float(settings['linear_length'])*spring_length
            self.d.ctrl[self.spring_ctrl]=spring_force-50.*self.d.qvel[self.spring_vadr]
            mujoco.mj_step(self.m,self.d)
            if not np.isfinite(self.d.qpos).all(): raise RuntimeError('Non-finite SCUT physics state')
            self._update_state()
            if self.closure>.002:
                self.reason=f'闭链超过2mm ({self.closure*1000:.3f}mm)'
                self.reset_standing();return self.telemetry()
        if self.jump_remaining:
            self._jump_peak_z=max(self._jump_peak_z,float(self.d.qpos[2]))
            wheel_geoms={self.m.geom(i).id for i in range(self.m.ngeom) if int(self.m.geom_bodyid[i]) in self.wheel_bids}
            grounded=any(int(c.geom1)in wheel_geoms or int(c.geom2)in wheel_geoms for c in self.d.contact)
            self.jump_airborne|=not grounded
            self.jump_remaining-=1;self.jump_elapsed+=.02
            if self.jump_remaining==0:
                result=dict(t=float(self.d.time),start_vx=self._jump_start_vx,peak_root_rise=self._jump_peak_z-self._jump_start_z,wheels_no_contact_observed=bool(self.jump_airborne),external_impulse=False)
                self.jump_log.append(result)
                self.last_jump=f'机身上升 {result["peak_root_rise"]*100:.1f}cm；双轮离地 {self.jump_airborne}'
                (HERE/'evidence/JUMP_EVENTS.json').write_text(json.dumps(self.jump_log,ensure_ascii=False,indent=2),encoding='utf-8')
                print('SPACE_JUMP_RESULT',json.dumps(result),flush=True)
        if self.cos_tilt<math.cos(math.radians(60)) or self.z<.07:
            self.reason='倒地重置';self.reset_standing()
        elif max(abs(self.d.qpos[0]),abs(self.d.qpos[1]))>4.2:
            self.reason='单格边界重置';self.reset_standing()
        return self.telemetry()


def headless_probe(seconds=12.):
    rows=[]
    for family in (FAMILIES[8],FAMILIES[9],FAMILIES[0]):
        s=SCUTReplay(family=family);s.paused=False;start_reset=s.reset_count
        samples=[];start=time.monotonic()
        for k in range(round(seconds/.02)):
            if k==200 and family==FAMILIES[8]:s.trigger_jump()
            s.step({'w'} if k>=100 else set())
            if k%25==0:samples.append(dict(step=k,x=float(s.d.qpos[0]),vx=s.env.vx,height=s.z,closure=s.closure,resets=s.reset_count-start_reset))
        rows.append(dict(family=family,wall_s=time.monotonic()-start,sim_s=float(s.d.time),resets=s.reset_count-start_reset,max_closure=s.max_closure,samples=samples,jump=s.jump_log))
        s.close()
    out=dict(checkpoint=str(CHECKPOINT),sha256=checksum(CHECKPOINT),plant=str(PLANT),plant_sha256=checksum(PLANT),joint_order=s.names,results=rows)
    (HERE/'evidence/HEADLESS_PROBE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--probe',action='store_true');p.add_argument('--seconds',type=float,default=12.);a=p.parse_args()
    if a.probe:headless_probe(a.seconds)


