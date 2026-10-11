"""Read existing145 query evidence; component proof never substitutes for fullroute."""
from second_io import *
from curb_io import WIN
import numpy as np
sys.path.insert(0,str(D/'wave50_worldmesh_scope'))
from g4_worldmesh_query_contract import expected_ground

def main():
    pub=json.loads((R/'WAVE50_WORLDMESH_FROZEN_PUBLISHED.json').read_bytes());jid=pub['jobs'][0]['job_id'];name='probe.json.worldmesh_query.npz';folder=R/'cases'/jid;folder.mkdir(parents=True,exist_ok=True);p=folder/name
    n,w=io.connect_both()
    try:
        with w.open_sftp() as f:
            raw=f.open(WIN+'/jobs/'+jid+'/'+name).read()
            if p.exists():assert p.read_bytes()==raw
            else:p.write_bytes(raw)
        ids=np.arange(80);centers=np.stack(((ids//2+.5)*9.-180.,(34+ids%2+.5)*9.-180.),axis=-1)
        with np.load(p,allow_pickle=False) as q:
            starts=q['actual_world_ray_origins'];tri=q['world_triangles'];assert starts.dtype==np.float32 and starts.shape==(80,35,3) and tri.shape[0]==80
            v=tri.reshape(-1,3);faces=np.arange(len(v)).reshape(-1,3)
            expected,receipts,_=expected_ground(v,faces,centers,starts)
            assert np.array_equal(expected,q['expected_actual_ground']) and np.array_equal(q['actual_canonical_ray_x'],starts[:,:,0].astype(float)-centers[:,None,0])
            error=float(np.max(abs(q['actual_sampled_ground']-expected)));ideal=float(np.max(abs(q['actual_sampled_ground']-q['ideal_profile_ground'])));assert error<=1e-6
        z=save('WAVE50_145_ACTUAL_QUERY_COMPONENT_REVIEW.json',dict(epoch=time.time(),job_id=jid,actual_query_evidence=dict(source=WIN+'/jobs/'+jid+'/'+name,local=str(p),bytes=len(raw),sha256=H(raw),large_index_only=True,original_retained=True),all80_actual_world_float32_mesh_triangles_byteexact=receipts,independent_CPU_triangle_expected_exact=True,actual_GPU_query_max_error_m=error,actual_GPU_vs_ideal_profile_difference_m=ideal,original_ground_tolerance_m=1e-6,passed=True,component_only_not_fullroute_or_scope_graduation=True,original144_GPU_error_numeric_not_saved_or_inferred=True,no_GPU_PPO_queue_or_budget_write=True))
        with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_WAVE50_145_ACTUAL_QUERY_COMPONENT_REVIEW.json',z.read_bytes())
        print(json.dumps(dict(report=str(z),actual_GPU_error_m=error,actual_vs_ideal_m=ideal,passed_component_only=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE50_145_QUERY_COMPONENT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
