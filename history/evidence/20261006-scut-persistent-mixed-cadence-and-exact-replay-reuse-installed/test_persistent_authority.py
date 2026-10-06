"""CPU-only injected lifecycle: healthy6h review continues; budget stops saved."""
import copy,importlib.util,json,sys,tempfile,types
from pathlib import Path
D=Path(__file__).resolve().parent


def run():
    with tempfile.TemporaryDirectory(prefix='mod4_cadence_contract_') as folder:
        root=Path(folder);reports={};state={'charged':0,'trained':0,'full_reviews':0}
        initial=dict(path='/complete/source.pt',sha256='source')
        def read(path):
            path=str(path)
            if path.endswith('PHYSICAL_DR_STAGE1_REVIEW_READY.json'):return {'paired_path':'anchor_paired'}
            if path=='anchor_paired':return {'rows':[dict(kind='flat',seed=20261002,profile='white_v3',report_path='anchor_flat')]}
            if path in ('anchor_flat','mixed'):return {}
            return reports[path]
        def atomic(path,obj):reports[str(path)]=copy.deepcopy(obj)
        def train(last,phase,duration):
            assert 0<duration<=7200
            state['charged']+=duration;state['trained']+=1
            return Path(f'/complete/policy_{state["trained"]}.pt')
        def paired(last,cache):
            state['full_reviews']+=1
            return {'world_progress_05_confirmed':True},'final_paired'
        base=types.SimpleNamespace(PY=sys.executable,atomic_json=atomic,checkpoint=lambda p:dict(path=str(p),finite_tensors=68),
            budget_state=lambda:dict(charged_training_seconds=state['charged']))
        ctl=types.SimpleNamespace(S={},remaining=lambda:28900-state['charged'],training=train,persist=lambda:None)
        c=types.SimpleNamespace(H=root,R=root,F=Path('/anchor'),P=root,ENTRY=None,base=base,ctl=ctl,
            helpers=types.SimpleNamespace(identity=lambda pid:dict(pid=pid,start_ticks='fake')),
            w=types.SimpleNamespace(read=read,STATE=root/'state',phase=lambda *a,**kw:None,hold=lambda *a:(_ for _ in ()).throw(AssertionError('Unexpected hold'))),
            mixed_probe=lambda *a:'mixed',verify=lambda:None,status=lambda *a,**kw:None,guardian=lambda *a:None)
        decision=dict(systematic_straight_regression_detected=False,rough_valid_segment_signs_correct=True,
                      pure_signed_yaw_fact_pass=True,auto_closeout_sufficient=True)
        q=types.ModuleType('supervise_scut_continuous_mix');q.c=c;q.wait_prior=lambda:{'checkpoint':initial}
        q.accept_boundary=lambda prior:(Path(initial['path']),'original_paired')
        q.checked_report=lambda *a:({},Path('/flat'),False);q.full_paired=paired;q.diagnostic=lambda *a:decision
        sys.modules['supervise_scut_continuous_mix']=q
        spec=importlib.util.spec_from_file_location('persistent_contract_subject',D/'supervise_scut_persistent_mix.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.subprocess=types.SimpleNamespace(Popen=lambda *a,**kw:types.SimpleNamespace(pid=123),DEVNULL=-3,STDOUT=-2)
        module.quick_summary=lambda *a:{'request_full_review':False}
        module.controller()
        assert state['trained']==4 and state['full_reviews']==2,state
        assert str(root/'CADENCE_STAGE_REVIEW_1.json') in reports
        assert reports[str(root/'CADENCE_REVIEW_READY.json')]['checkpoint']['path']==str(Path('/complete/policy_4.pt'))
        assert str(root/'CADENCE_PRACTICAL_CLOSEOUT.json') in reports
        assert reports[str(root/'RETENTION_REVIEW_READY.json')]['all_curricula_finished'] is False
        return dict(pass_=True,injected_CPU_only=True,healthy6h_review_auto_continued=True,
                    real_GPU_started=False,budget_boundary_saved_review=True,blocks=4,full_reviews=2)


if __name__=='__main__':print(json.dumps(run()))
