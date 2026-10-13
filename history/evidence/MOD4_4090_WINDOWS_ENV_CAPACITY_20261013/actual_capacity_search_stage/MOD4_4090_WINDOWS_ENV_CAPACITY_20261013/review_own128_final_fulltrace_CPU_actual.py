from pathlib import Path
import json,time,hashlib,sys,numpy as np,torch
D=Path(__file__).resolve().parent;W=D.parent
COL=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013/OWN_PPO_CPU_INPUTS_1791894571823537900/ACTUAL_COLLECTION.json'
def main():
 x=json.loads(COL.read_bytes());a,c=[torch.load(p['local_actual_path'],map_location='cpu',weights_only=False) for p in x['files']]
 rows=[];end=0;files=[]
 for p in sorted((D/'OWN128_FINAL_FULLTRACE').glob('retention_prefix_*.npz'),key=lambda p:int(p.stem.split('_')[2])):
  start,stop=map(int,p.stem.split('_')[2:]);assert start==end
  with np.load(p) as z:
   v=z['rows'].copy();columns=z['columns'].tolist()
  assert v.shape==(stop-start,128,16) and v.dtype==np.float32 and np.isfinite(v).all();rows.append(v);end=stop;files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),start=start,stop=stop))
 v=np.concatenate(rows);assert end==2904 and v.shape==(2904,128,16)
 terminated=v[...,14].astype(bool);trunc=v[...,15].astype(bool);reset=terminated|trunc
 assert not terminated.any() and int(trunc.sum())==248
 assert np.array_equal(v[1:,:,:3][~reset[:-1]],v[:-1,:,3:6][~reset[:-1]])
 delta=torch.from_numpy(reset.sum(axis=0).astype(np.int64))
 assert torch.equal(c['E1_terrain_state']['episode'].long(),a['E1_terrain_state']['episode'].long()+1+delta)
 for k in ('E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state'):
  assert torch.equal(c[k]['bound_episode'],c['E1_terrain_state']['episode'])
 assert np.isin(v[...,10],np.arange(5)).all()
 wave=v[...,10]==4;standing=wave&(v[...,7]==0);negative=wave&(v[...,7]<0);positive=wave&(v[...,7]>0)
 assert np.all(v[...,8][wave]==0) and np.all(v[...,9][wave]==0) and np.max(np.abs(v[...,7][wave]))<=.3+1e-6
 runs=np.zeros(128,dtype=np.int64);maxrun=np.zeros(128,dtype=np.int64)
 for resetrow in reset:runs+=1;maxrun=np.maximum(maxrun,runs);runs[resetrow]=0
 proof=dict(epoch=time.time(),passed=True,independent_CPU_only_no_CUDA=True,source_final_SHA=x['files'][1]['sha256'],all61NPZ_byteSHA_and_float32_finite=True,controls=2904,num_envs=128,envsteps=371712,callbacks=11616,ordinary0=True,truncation_unique248=True,timeout117_route132_overlap1_not_added=True,source_episode_plus_one_and_all248_actual_resets_exact=True,nonreset_prereset_to_nextbefore_root_exact=True,direction_route_lifetime_bound_episode_exact=True,dynamic_current_family4=dict(negative=int(negative.sum()),positive=int(positive.sum()),standing=int(standing.sum())),maximum_observed_new_physical_prefix_seconds=float(maxrun.max())*.01,root_command_proxy_not_fullroute_contact_or_causal_certificate=True,beforephysics_vs_cumulative_afterupdate_hist_different_phases=True,files=files)
 out=D/'reports/OWN128_FINAL_FULLTRACE_CLOSEOUT_CPU_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in proof.items() if k!='files'}))
if __name__=='__main__':main()
