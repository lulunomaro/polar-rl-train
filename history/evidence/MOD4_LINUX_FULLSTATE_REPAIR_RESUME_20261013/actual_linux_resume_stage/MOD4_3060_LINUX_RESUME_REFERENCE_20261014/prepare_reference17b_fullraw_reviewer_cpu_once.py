"""New complete-data reviewer source; actualfuture reports not fabricated."""
from pathlib import Path
P=Path(__file__).resolve().parent;W=P.parent
old=(W/'MOD4_3060_DIRECT_FACTOR_20261013/review_direct3060_new1500_complete_actual_cpu.py').read_text()
source=old.replace("CASES={'baseline':'native3060_bodypos_worldpos_baseline1500_v2','D3':'native3060_bodypos_worldpos_D3current1500_v2'}", "CASES={'baseline':'native3060_17b_bodypos_worldpos_reference1500_v1'}")
source=source.replace("source,j=collected(case+'_CURRENT_ACTUAL_*.json')", "source,j=collected('REFERENCE17B_CURRENT_ACTUAL_*.json')")
source=source.replace('91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4','17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9')
start=source.index(" if a.factor=='baseline':basepath,base=collected(")
end=source.index(" profile=json.loads(",start)
replacement=""" oldR=D.parent/'MOD4_3060_DIRECT_FACTOR_20261013/reports'
 basepath=sorted(oldR.glob('native3060_bodypos_worldpos_baseline1500_v2_CURRENT_ACTUAL_*.json'))[-1]
 base=json.loads(basepath.read_bytes());bc=base['outputs']['COMPLETE_ACTUAL.json'];brow,bdata=raw(base)
 initial_exact=c['initial']==bc['initial']
 initial_differences=[]
 def differences(x,y,path='initial'):
  if type(x)is not type(y):initial_differences.append(dict(path=path,reason='type'));return
  if isinstance(x,dict):
   if set(x)!=set(y):initial_differences.append(dict(path=path,reason='keyset'))
   for k in set(x)&set(y):differences(x[k],y[k],path+'/'+str(k))
  elif isinstance(x,list):
   if len(x)!=len(y):initial_differences.append(dict(path=path,reason='length'));return
   for i,(u,v) in enumerate(zip(x,y)):differences(u,v,path+'/'+str(i))
  elif x!=y:initial_differences.append(dict(path=path,old_value=y,new_value=x))
 differences(c['initial'],bc['initial'])
 assert c['seed']==bc['seed']==20260928
 assert bc['checkpoint_sha256']=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
 assert not c['factor']['feedback_current'] and not c['factor']['policy_factor'] and not c['factor']['sensor_clean']
 assert c['recipe']==bc['recipe'], 'Original frozenfixture recipe identity'
 actorproof=j['outputs']['FROZEN_POLICY_SOURCE107_ACTUAL.json']
 assert actorproof and actorproof['checkpoint_sha256']==c['checkpoint_sha256'] and actorproof['source_floating107']
 assert actorproof['source_saved_envs']==512 and actorproof['fixture_envs']==8
 cpuproof=json.loads((R/'REFERENCE17B_SOURCE_FROZEN_CPU_PREPARED_ACTUAL.json').read_bytes())
 assert actorproof['actual_GPU_actor_nine_tensors_source_byteexact']==cpuproof['actual_actor_nine_CPU_rows']
 assert actorproof['no_training_perenv_DR_projection_or_restore'] and actorproof['no_initializer_or_PPO']
 stdoutrow=next(r for r in j['local_collected_files'] if r['relative'].endswith('/worker.log'))
 stdout=Path(stdoutrow['local_path']).read_bytes();assert H(stdoutrow['local_path'])==stdoutrow['sha256']
 lower=stdout.lower()
 for token in (b'buffer overflow detected',b'contacts have been dropped',b'physx scene is corrupted',b'cuda error',b'out of memory'):
  assert token not in lower, ('Complete actual stdout physical failure',token)
 prefix=None
"""
source=source[:start]+replacement+source[end:]
source=source.replace("source91d_SHA=c['checkpoint_sha256'],initial_full_qXYZ_DR_queue_captured_RNG_exact_to_reference=True,reference_collector=str(basepath),prefix120_actual=prefix,", "source17b_SHA=c['checkpoint_sha256'],reference91d_SHA=bc['checkpoint_sha256'],initial_full_qXYZ_DR_queue_captured_RNG_exact_to_reference=initial_exact,initial_differences=initial_differences,reference_collector=str(basepath),prefix120_actual=prefix,actual_GPU_nine_actor_source_byteexact=actorproof,complete_stdout_no_overflow_actual=stdoutrow,")
source=source.replace(" out=R/('DIRECT3060_BASELINE1500_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json' if a.factor=='baseline' else 'DIRECT3060_D3CURRENT1500_COMPLETE_PAIRED_CPU_ACTUAL_REVIEW.json')", " out=R/'REFERENCE17B_FULL1500_COMPLETE_PAIRED91D_CPU_ACTUAL_REVIEW.json'")
source=source.replace("initial_pair_exact=True,prefix120=prefix is not None", "initial_pair_exact=initial_exact,prefix120=prefix is not None")
source=source.replace("source91d_SHA=", "source17b_SHA=")
p=P/'review_reference17b_fullraw_direct91d_actual_cpu.py';assert not p.exists();compile(source,str(p),'exec');p.write_text(source,encoding='utf8')
print(str(p))
