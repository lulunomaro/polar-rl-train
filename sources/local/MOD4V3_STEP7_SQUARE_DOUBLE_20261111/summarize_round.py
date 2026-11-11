"""Summarize saved checkpoints and the one completed paired replay, without training."""
from pathlib import Path
import hashlib,json,shutil
import torch

TRIAL=Path(__file__).resolve().parent
REPO=TRIAL.parents[2]
LOCAL=Path(r"D:\claude2\fangzhen\tmp\step7_square_double_20261111_r1")
E=TRIAL/"evidence"
M=E/"training_round"
W=TRIAL/"weights"

def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert (M/"MONITOR_COMPLETE.json").exists()
    final=read(M/"FINAL.json")
    assert final["elapsed_seconds"]>=2400 and read(M/"SAFE_CLOSED.json")["scene_closed"]
    result=read(E/"paired_final_r1_RESULT.json")
    closed=read(E/"paired_final_r1_SAFE_CLOSED.json")
    assert closed["result"] and not closed["error"] and result["no_optimizer_constructed"]
    plan=read(TRIAL/"PLAN.json")
    assert result["input_sha256"]["parent"]==plan["parent_sha256"]
    W.mkdir(exist_ok=True)
    model_rows=[]
    receipts=[("first",read(E/"FIRST_CHECKPOINT_READBACK.json"),"model_first_complete.pt")]
    receipts += [(f"{minute:03d}m",read(M/f"PERIODIC_{minute:03d}M.json"),f"model_{minute:03d}m.pt") for minute in range(5,41,5)]
    known={}
    for label,receipt,name in receipts:
        src=LOCAL/name
        expected=receipt.get("SHA",receipt.get("sha256"))
        digest=sha(src)
        assert digest==expected and src.stat().st_size==receipt["bytes"]
        dst=W/name
        if not dst.exists():shutil.copyfile(src,dst)
        assert sha(dst)==digest
        data=torch.load(src,map_location="cpu",weights_only=False)
        required=("actor_state_dict","critic_state_dict","optimizer_state_dict","cpu_rng","cuda_rng","domain_randomization_state")
        assert all(k in data for k in required),(label,tuple(data))
        assert int(data["iter"])==receipt["iteration"]
        actor_input=int(data["actor_state_dict"]["mlp.0.weight"].shape[1])
        critic_input=int(data["critic_state_dict"]["mlp.0.weight"].shape[1])
        assert (actor_input,critic_input)==(35,78)
        row=dict(id="square1_"+label,iteration=data["iter"],bytes=src.stat().st_size,sha256=digest,git_path=dst.relative_to(REPO).as_posix(),original_local_path=str(src),original_remote_path=(plan["support"].rsplit("/support",1)[0]+"/train040m_square_double_r1/model_first_complete.pt" if label=="first" else receipt.get("remote",receipt.get("path"))),identity_evidence=(E/"FIRST_CHECKPOINT_READBACK.json" if label=="first" else M/f"PERIODIC_{label.upper()}.json").relative_to(REPO).as_posix(),complete_PPO=True,optimizer_entries=len(data["optimizer_state_dict"]["state"]),actor_input=actor_input,critic_input=critic_input,domain_randomization_state_fields=list(data["domain_randomization_state"]),resume_scope=data["resume_scope"],aliases=[])
        model_rows.append(row);known[digest]=row
    final_src=LOCAL/"model_final.pt";digest=sha(final_src)
    assert digest==final["checkpoint"]["SHA"]
    if digest in known:
        known[digest]["aliases"].append("model_final.pt (byte-identical)")
        final_id=known[digest]["id"]
    else:
        dst=W/"model_final.pt";shutil.copyfile(final_src,dst)
        d=torch.load(final_src,map_location="cpu",weights_only=False)
        row=dict(id="square1_final",iteration=d["iter"],bytes=dst.stat().st_size,sha256=digest,git_path=dst.relative_to(REPO).as_posix(),original_local_path=str(final_src),original_remote_path=final["checkpoint"]["path"],identity_evidence=(M/"FINAL.json").relative_to(REPO).as_posix(),complete_PPO=True,optimizer_entries=len(d["optimizer_state_dict"]["state"]),domain_randomization_state_fields=list(d["domain_randomization_state"]),resume_scope=d["resume_scope"],aliases=[])
        model_rows.append(row);final_id=row["id"]
    write(E/"MODEL_ARCHIVE_INDEX.json",dict(models=model_rows,final_model_id=final_id,unique_models=len(model_rows),total_bytes=sum(x["bytes"] for x in model_rows),storage="ordinary Git full PT bytes; byte-identical final aliased"))
    summaries=[]
    formal=lambda row: row["task"] not in ("combo_0.9_1.2","forward_2.7_diagnostic")
    for model in result["input_sha256"]:
        for variant in ("nominal0","Step7_all_remaining_DR"):
            pre=[x for x in result["rows"] if x["model"]==model and x["variant"]==variant]
            post=[x for x in result["recovery_rows"] if x["model"]==model and x["variant"]==variant]
            official=[x for x in pre if formal(x)]
            forward=[x for x in post if x["task"] in ("forward_2.0","forward_2.2")]
            err=[abs(v[0]-(2.0 if x["task"]=="forward_2.0" else 2.2)) for x in forward for v in x["per_env_post_stable"]]
            summaries.append(dict(model=model,variant=variant,pre_passed=sum(x["passed"] for x in official),post_passed=sum(x["post_push_passed"] for x in post if formal(x)),requested=sum(x["requested"] for x in official),formal_resets=sum(x["resets"] for x in official),diagnostic_resets=sum(x["resets"] for x in pre if not formal(x)),forward_post_mean_absolute_error=sum(err)/len(err),pre_rows=pre,post_rows=post))
    write(E/"ROUND_SUMMARY.json",dict(training_elapsed_seconds=final["elapsed_seconds"],training_last_progress=final.get("last_progress"),paired_num_envs=result["num_envs"],paired_wall_seconds=result["wall_seconds"],paired_numerical=sum(x["reasons"]["numerical"] for x in result["rows"]),paired_closure_resets=sum(x["reasons"]["closure"] for x in result["rows"]),paired_max_closure_m=max(x["max_closure_m"] for x in result["rows"]),action_slot_max_error=result["action_slot_max_error"],motor_envelope_violation_nm=result["motor_envelope_violation_nm"],models=summaries))
    for x in summaries:
        if x["variant"]!="Step7_all_remaining_DR":continue
        f=[y for y in x["post_rows"] if y["task"].startswith("forward_")]
        print(json.dumps({k:v for k,v in x.items() if k not in ("pre_rows","post_rows")}|{"forward_post":[[y["task"],y["post_push_stable_mean"][0],y["post_push_passed"]] for y in f]},ensure_ascii=False))
    print(json.dumps(dict(models=len(model_rows),final_model_id=final_id),ensure_ascii=False))

if __name__=="__main__":main()
