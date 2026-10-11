"""Continue only unexecuted package preparation after independent authored-endpoint query rejection."""
from second_io import *
import ast,zipfile,importlib.util
import numpy as np
def main():
 impl=D/'next_wave50_scope';assert not (R/'WAVE50_COMPONENT_FROZEN_PREPARED.json').exists()
 original=D/'decide_complete143_and_prepare50_once.py';src=original.read_text(encoding='utf8')
 parent=W/'MOD4_E1_G3_MATCHED_REVIEW_20261010/artifacts/e1-g3-derived35mm-paired-approach040-frozen-v2.zip'
 assert H(parent.read_bytes())=='858ad4ef431f188f3275dc8b3c3690bf1d987a5c074f9aed698e15343ad66d2b'
 with zipfile.ZipFile(parent) as z:members={n:z.read(n) for n in z.namelist()}
 manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[n])==h for n,h in manifest['files'].items())
 gp='runtime/isaac/mod4/g4_cad_wave_geometry.py';pp='runtime/isaac/mod4/g4_cad_profile.json';fp='runtime/isaac/mod4/frozen_history_flat.py'
 geom=(impl/'g4_cad_wave_geometry.py').read_text(encoding='utf8');profile=json.loads((impl/'g4_cad_profile.json').read_bytes());half=profile['span_m']/2
 spec=importlib.util.spec_from_file_location('g4_author_endpoint_cpu',impl/'g4_cad_wave_geometry.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mesh,_=mod.make_mesh((9.,9.));verts=mesh.vertices.copy();verts[:,:2]-=4.5
 centers=(np.arange(80)//2+.5)*9.-180.;requested=np.r_[-half-.4,np.linspace(-half,half,33),half+.4];actual=np.asarray(centers[:,None]+requested,dtype=np.float32).astype(np.float64)-centers[:,None]
 tri=verts[mesh.faces];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];direction=np.array([0.,0.,-1.]);cross=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,cross);assert np.all(abs(det)>1e-12)
 errors=[];original_requested_profile_errors=[];knots=np.r_[np.asarray(profile['profile_x_m'])[:-1],profile['span_m']];heights=np.asarray(profile['normalized_height'])*.05
 for x in actual.ravel():
  origin=np.array([x,0.,2.]);delta=origin-tri[:,0];u=np.einsum('ij,ij->i',delta,cross)/det;q=np.cross(delta,e1);w=q@direction/det;dist=np.einsum('ij,ij->i',e2,q)/det
  hits=(u>=-1e-12)&(w>=-1e-12)&(u+w<=1+1e-12)&(dist>=0);assert hits.any();height=2.-dist[hits].min()
  errors.append(abs(height-np.interp(x+half,knots,heights,left=0.,right=0.)))
  original_requested_profile_errors.append(abs(height-np.interp(x+half,np.asarray(profile['profile_x_m']),heights,left=0.,right=0.)))
 assert max(errors)<1e-10 and abs(np.ptp(mesh.vertices[:,2])-.05)<1e-12 and (mesh.face_normals[:,2]>0).all()
 save('WAVE50_AUTHORED_JOIN_QUERY_CPU_REVIEW.json',dict(epoch=time.time(),original_builder=str(original),original_SHA=H(original.read_bytes()),original_rejection_preserved=True,profile_last_x_m=profile['profile_x_m'][-1],authored_last_join_x_m=profile['span_m'],old_make_mesh_explicit_last_join_span_identity=True,CPU_only_original_query_max_error_m=max(original_requested_profile_errors),CPU_only_authored_query_max_error_m=max(errors),original_geometry_and_profile_bytes_not_changed=True,ground_tolerance_m=1e-6,no_GPU_or_result_replay=True))
 decision=json.loads((R/'WAVE143_COMPLETE_OBSERVED_SCOPE_DECISION.json').read_bytes());checkpoint=decision['own_checkpoint']
 marker="    old=members[fp].decode();proto=";assert src.count(marker)==1
 tail=marker+src.split(marker,1)[1].split("\nif __name__=='__main__':",1)[0]
 tail='\n'.join(line[1:] if line.startswith(' ') else line for line in tail.splitlines())
 tail=tail.replace("np.asarray(wave_profile['profile_x_m']),np.asarray(wave_profile['normalized_height'])*.05", "np.r_[np.asarray(wave_profile['profile_x_m'])[:-1],wave_profile['span_m']],np.asarray(wave_profile['normalized_height'])*.05")
 # Execute the original yet-unexecuted package section only. Earlier decision and component files remain immutable.
 exec(compile(tail,str(original)+'#unexecuted-package-section','exec'),globals(),locals())
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE50_QUERY_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only=True,no_GPU_or_budget_write=True));raise
