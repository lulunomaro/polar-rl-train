"""Real native successful observation/action episodes, phase-balanced E1-only replay."""
from pathlib import Path
import hashlib,json
import numpy as np
import torch

class SuccessReplayPool:
    def __init__(self,max_frames=32768,seed=907):
        self.max_frames=max_frames;self.episodes=[];self.frames=0;self.total_accepted=0;self.cache=None
        self.generator=torch.Generator(device='cpu').manual_seed(seed)
    def add(self,frames,phases,metadata):
        assert metadata['accepted_native_success'] and metadata['stable_hold_s']>=.4-1e-6
        assert frames.ndim==2 and frames.shape[1]==461 and phases.shape==(len(frames),)
        assert np.isfinite(frames).all() and np.isin(phases,[0,1,2]).all()
        metadata=metadata.copy()
        frozen_v1=(metadata.get('source_model_sha256')=='a55eeaed11ed7c7471444e1369153824b3fe79544e59296c911a3235507bd7a4' and metadata.get('policy_update',0)==0)
        # Do not teach the old10m/online policy's rushing startup back into v1.
        excluded=0 if frozen_v1 else min(75,len(frames))
        metadata['BC_excluded_startup_frames']=excluded
        frames=frames[excluded:];phases=phases[excluded:]
        if not len(frames):return

        if len(frames)>self.max_frames:frames=frames[-self.max_frames:];phases=phases[-self.max_frames:]
        self.episodes.append((torch.from_numpy(frames.copy()).float(),torch.from_numpy(phases.copy()).long(),metadata.copy()))
        self.frames+=len(frames);self.total_accepted+=1;self.cache=None
        while self.frames>self.max_frames and len(self.episodes)>1:
            old=self.episodes.pop(0);self.frames-=len(old[0])
    def load_directory(self,directory):
        for path in sorted(Path(directory).glob('episode_*.npz')):
            with np.load(path,allow_pickle=False)as d:
                meta=json.loads(str(d['metadata_json']));self.add(d['frames'],d['phases'],meta)
    def sample(self,n,device):
        if not self.frames:return None
        if self.cache is None:
            frames=torch.cat([a[0]for a in self.episodes]);phases=torch.cat([a[1]for a in self.episodes]);self.cache=(frames,[torch.where(phases==i)[0]for i in range(3)])
        frames,groups=self.cache;chosen=[]
        for count,indices in zip([round(n*.2),round(n*.3),n-round(n*.2)-round(n*.3)],groups):
            if not len(indices):indices=torch.arange(len(frames))
            chosen.append(indices[torch.randint(len(indices),(count,),generator=self.generator)])
        f=frames[torch.cat(chosen)].to(device)
        return dict(policy=f[:,:35],obs_history=f[:,35:455],actions=f[:,455:461])
    def checkpoint_state(self):
        return dict(max_frames=self.max_frames,episodes=self.episodes,frames=self.frames,total_accepted=self.total_accepted,generator_state=self.generator.get_state())
    def summary(self):
        phases=torch.cat([a[1]for a in self.episodes])if self.episodes else torch.zeros(0,dtype=torch.long)
        return dict(kept_episodes=len(self.episodes),kept_frames=self.frames,total_accepted=self.total_accepted,phase_frame_counts=torch.bincount(phases,minlength=3).tolist(),phases=['settle','approach','top_support'],formal_or_fullDR_graduation=False)

class NativeSuccessRecorder:
    def __init__(self,env,directory,source_sha256,pool=None,window=None):
        self.env=env;self.ids=env.continuous_stair_mask.nonzero().flatten();self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.source_sha256=source_sha256;self.pool=pool or SuccessReplayPool();self.window=int(window or (env.max_episode_length+1));self.cursor=0
        self.frames=torch.zeros(self.window,len(self.ids),461,device=env.device);self.phases=torch.zeros(self.window,len(self.ids),dtype=torch.int8,device=env.device)
        self.length=torch.zeros(len(self.ids),dtype=torch.long,device=env.device);self.saved=0;self.steps=0;self.policy_update=0
    def push(self,observations,executed_actions,policy_update=0):
        self.frames[self.cursor]=torch.cat([observations['policy'][self.ids],observations['obs_history'][self.ids],executed_actions[self.ids].clamp(-6,6)],1).detach()
        self.length+=1;self.policy_update=policy_update
    def finish(self,done):
        env=self.env;support=env.replay_top_support_count[self.ids]
        command=self.frames[self.cursor,:,0]
        self.phases[self.cursor]=torch.where(command.abs()<.05,0,torch.where(support>0,2,1)).to(torch.int8)
        success=env.replay_success_now[self.ids]
        for local in success.nonzero().flatten().tolist():
            amount=min(int(self.length[local]),self.window);slots=torch.arange(self.cursor-amount+1,self.cursor+1,device=env.device)%self.window
            frames=self.frames[slots,local].detach().cpu().numpy();phases=self.phases[slots,local].detach().cpu().numpy()
            idx=int(self.ids[local]);meta=dict(accepted_native_success=True,stable_hold_s=.4,qualification='native training current speed tier, real bilateral support and body clear',formal_evaluation_pass=False,source_model_sha256=self.source_sha256,policy_update=self.policy_update,env_id=idx,episode_steps=int(self.length[local]),truncated=int(self.length[local])>self.window,physics_dt_s=.0025,policy_dt_s=.02,history_H=12,teacher_assistance=False,actual_full_DR=bool(env.replay_actual_DR_at_step[idx]),speed_limit_m_s=float(env.replay_speed_limit_at_step[idx]))
            self.pool.add(frames,phases,meta);self.saved+=1;path=self.directory/f'episode_{self.saved:06d}.npz'
            pending=path.with_name(path.stem+'.partial.npz')
            np.savez_compressed(pending,frames=frames,phases=phases,metadata_json=np.asarray(json.dumps(meta)))
            pending.replace(path)
        self.length[done[self.ids]]=0;self.cursor=(self.cursor+1)%self.window;self.steps+=1
        if bool(success.any()):self.write_manifest()
    def write_manifest(self):
        files={p.name:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)for p in self.directory.glob('episode_*.npz')}
        tmp=self.directory/'MANIFEST.json.partial';tmp.write_text(json.dumps(dict(**self.pool.summary(),new_saved_episodes=self.saved,source_model_sha256=self.source_sha256,files=files),indent=2)+'\n');tmp.replace(self.directory/'MANIFEST.json')
    def summary(self):return dict(**self.pool.summary(),new_saved_episodes=self.saved,recorded_policy_steps=self.steps)
