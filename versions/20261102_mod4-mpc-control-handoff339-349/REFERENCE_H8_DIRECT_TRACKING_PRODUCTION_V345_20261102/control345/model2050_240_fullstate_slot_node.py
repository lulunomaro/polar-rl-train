"""Known own finite cold-PPO node; no authority write or credential file."""
from pathlib import Path
import os,sys,time,json,hashlib,fcntl,subprocess,traceback,psutil,shutil
from report_classification312 import classify_error_reports
import three_slot_common_v1 as b
from forwarded_original_owner_control_v1 import send,close
B=Path(__file__).resolve().parent
def env_for(spec):
    e=dict(os.environ,CUDA_VISIBLE_DEVICES=spec["GPU_UUID"],PYTHONDONTWRITEBYTECODE="1",PYTHONNOUSERSITE="1",PYTHONUNBUFFERED="1",OMNI_KIT_ACCEPT_EULA="YES",ISAACSIM_ACCEPT_EULA="Y")
    for k in ("PYTHONHOME","PYTHONPATH","LD_PRELOAD","RANK","LOCAL_RANK","WORLD_SIZE","MASTER_ADDR","MASTER_PORT"):e.pop(k,None)
    for key,name in {"HOME":"home","TMPDIR":"tmp","TMP":"tmp","TEMP":"tmp","XDG_CACHE_HOME":"cache","XDG_CONFIG_HOME":"config","XDG_DATA_HOME":"data","XDG_STATE_HOME":"state","XDG_RUNTIME_DIR":"state/runtime","TORCH_HOME":"cache/torch","CUDA_CACHE_PATH":"cache/cuda","WARP_CACHE_PATH":"cache/warp"}.items():
        p=Path(spec["job_root"])/"private_train"/name;p.mkdir(parents=True,exist_ok=True);e[key]=str(p)
    return e
def node(spec):
    p=None;lock=None;error=None;go=None;last=time.time();begin=time.time();J=Path(spec["job_root"]);out=J/"production"
    b.put(B/"NODE_IDENTITY.json",b.ident(os.getpid()))
    try:
        assert spec["key"] in b.CAPS and spec["GPU_UUID"]==b.GPUS[spec["key"]]
        mpath=J/spec["manifest_file"];assert b.H(mpath)==spec["manifest_SHA"]
        manifest=b.read(mpath)
        for row in manifest["files"]:
            f=J/row["relative"];assert f.resolve().is_relative_to(J.resolve()) and f.stat().st_size==row["bytes"] and b.H(f)==row["SHA"]
        admission=b.read(J/"FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json");assert admission["manifest_SHA"]==spec["manifest_SHA"]
        closed=dict(value=admission,SHA=hashlib.sha256(json.dumps(admission,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
        lock=Path(spec["private_lock"]).open("rb+");fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if spec["execution_backend"]=="target72":
            with Path("/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock").open("rb+") as f:
                fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
        line=subprocess.check_output(["nvidia-smi","-i",spec["GPU_UUID"],"--query-gpu=uuid,name,memory.free,utilization.gpu","--format=csv,noheader,nounits"],text=True).strip()
        a=[x.strip() for x in line.split(",")];ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free
        b.put(B/"ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json",dict(epoch=time.time(),GPU_line=line,RAM_available=ram,disk_free=disk,private_EX=True,no_other_PID_read=True))
        assert a[0]==spec["GPU_UUID"] and a[1]=="NVIDIA GeForce RTX 4090" and int(a[2])>15669 and int(a[3])<=30 and ram>32*1024**3 and disk>25*1024**3
        phase="ready"
        while True:
            row=dict(key=spec["key"],phase=phase,manifest_SHA=spec["manifest_SHA"],closed_source_CPU=closed,
                original_error=False,worker=b.ident(p.pid) if p and p.poll() is None else None,returncode=None)
            reply=send(spec,row,b.PORT);last=time.time()
            if go is None and reply.get("go"):
                go=reply["go"];assert go["run_id"]==spec["run_id"] and go["teacher_student345"] and go["FROZEN_TEACHER"] and go["source_model_SHA"]==spec["source_SHA"]
                assert go["max_parent_seconds"]==3900 and go["save_deadline"]==go["learning_started_epoch"]+3600
                b.put(J/"GO_PRODUCTION.json",go);assert not out.exists()
                args=[spec["python"],"-u","-B",str(J/spec["worker_script"]),"--task",str(J/"TASK345.json")]
                with (B/"production_WORKER.log").open("xb") as log:
                    p=subprocess.Popen(args,cwd=J,env=env_for(spec),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True,close_fds=True)
                b.put(B/"WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json",b.ident(p.pid));phase="production"
            if p and p.poll() is not None:
                rc=p.wait();final=b.read(out/"FINAL.json");errors,diagnostic_reports=classify_error_reports(out)
                assert rc==0 and final and final.get("passed") and final.get("actual_new_WM_updates",0)>0 and final.get("actual_new_PPO_updates")==0 and final.get("actual_new_Pi_updates",0)>0 and final.get("actual_new_critic_updates",0)>0 and not errors,dict(returncode=rc,final=final,errors=errors)
                break
            stop=reply.get("stop") or time.time()-last>120 or time.time()-begin>10800 or (go and time.time()>=go["save_deadline"])
            if stop:
                if p and p.poll() is None:
                    out.mkdir(exist_ok=True);b.put(out/"STOP_AFTER_SAVE.json",dict(epoch=time.time(),reason="Own original finite save deadline or owner stop"))
                else:raise RuntimeError("WM warm stopped before any learning")
            b.put(B/"NODE_CURRENT.json",dict(epoch=time.time(),row=row,reply=reply))
            time.sleep(3)
    except BaseException:
        error=traceback.format_exc();b.put(B/"NODE_ORIGINAL_ERROR.json",dict(epoch=time.time(),error=error,no_automatic_retry=True))
        if p and p.poll() is None:
            out.mkdir(exist_ok=True);b.put(out/"STOP_AFTER_SAVE.json",dict(epoch=time.time(),reason="Own node exception; complete saved stop"))
    finally:
        if p:p.wait()
        row=dict(key=spec["key"],phase="terminal",manifest_SHA=spec["manifest_SHA"],
            closed_source_CPU=locals().get("closed"),original_error=error is not None,
            terminal_all_own_children_waited=True,returncode=p.returncode if p else 1,
            final=b.read(out/"FINAL.json"),worker=b.ident(p.pid) if p else None)
        b.put(B/"NODE_TERMINAL_ACTUAL.json",dict(epoch=time.time(),row=row))
        ack=False
        for attempt in range(3):
            try:send(spec,row,b.PORT);ack=True;break
            except BaseException:b.put(B/("TERMINAL_HANDOFF_ERROR_"+str(attempt)+".json"),dict(error=traceback.format_exc()));time.sleep(5)
        close()
        if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
        b.put(B/"NODE_EXIT_ACTUAL.json",dict(epoch=time.time(),all_own_children_waited=True,private_EX_released=True,terminal_owner_ack=ack))
    if error:raise RuntimeError("Cold node original error preserved")
if __name__=="__main__":
    spec=json.loads(sys.stdin.readline());assert spec["role"]=="node"
    assert not (B/"node_CONSOLE.log").exists();pid=os.fork()
    if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role="node")),flush=True)
    else:
        os.setsid();fd=os.open(str(B/"node_CONSOLE.log"),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd)
        fd=os.open("/dev/null",os.O_RDONLY);os.dup2(fd,0);os.close(fd);node(spec)

