"""Keep the unused first probe; bind standing root Z to the actual local ground."""
from scut_wave_io import *
s=(D/'scut_wave50_original_probe.py').read_text(encoding='utf8')
old=' env.terrain.env_origins[:,2]=0.'
new=" with np.load(D/'actual_mod4_wave50_query.npz',allow_pickle=False) as z:initial_ground=z['expected_actual_ground'][:,17].copy()\n env.terrain.env_origins[:,2]=torch.tensor(initial_ground,device=env.device)* (groups==2)"
assert s.count(old)==1;s=s.replace(old,new);compile(s,'scut_wave50_placement_reviewed_probe.py','exec')
p=D/'scut_wave50_placement_reviewed_probe.py';assert not p.exists();p.write_text(s,encoding='utf8')
save('SCUT_PLACEMENT_REVIEWED_PROBE_PREPARED.json',dict(epoch=time.time(),passed=True,original_unexecuted_probe_retained=True,standing_root_ground_height_bound_to_actual_saved_mesh=True,moving_start_ground_flat=True,other_original_SCUT_pose_DR_RNG_and_route_unchanged=True,path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes()),actual_GPU_admission_pending=True))
print(json.dumps(dict(prepared=True,probe=str(p))))
