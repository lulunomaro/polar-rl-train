"""Export the measured experimental stair actor without optimizer/critic baggage."""
import hashlib
import torch
from fsm_paths import HERE,E0_SHA,JUMP_PATH
from fsm_io import put,sha256
from manual_fsm_model import make_stair


def main():
    source=HERE/'evidence/fsm_r9/train/model_009m.pt'
    payload=torch.load(source,map_location='cpu',weights_only=False)
    path=HERE/'weights/E_stair_r9_009m_selected.pt'
    data=dict(format='mod4v3_manual_fsm_stair_v1',architecture='cnn12_z2',stair=payload['stair'],
        source_checkpoint=str(source.relative_to(HERE)),source_sha256=sha256(source),
        ppo_updates=payload['ppo_updates'],optimizer_steps=payload['optimizer_steps'],
        export_optimizer_updates=0,e0_sha256=E0_SHA,detector=payload['detector'],
        status='experimental_not_graduated')
    torch.save(data,path)
    original=make_stair(payload).state_dict()
    exported=make_stair(torch.load(path,map_location='cpu',weights_only=False)).state_dict()
    assert original.keys()==exported.keys() and all(torch.equal(original[k],exported[k]) for k in original)
    identity=hashlib.sha256()
    for name,value in sorted(exported.items()):
        identity.update(name.encode());identity.update(value.contiguous().numpy().tobytes())
    proof=dict(source_sha256=sha256(source),export_sha256=sha256(path),
        inference_weight_identity_sha256=identity.hexdigest(),all_tensors_bitwise_equal=True,
        removed='critic, optimizer and rollout state',optimizer_updates_in_export=0)
    put(HERE/'evidence/SELECTED_ACTOR_IDENTITY.json',proof)
    put(HERE/'CANDIDATE.json',dict(checkpoint=str(path.relative_to(HERE)),sha256=sha256(path),
        status='experimental_not_graduated',strict_stair_acceptance_passed=False,
        source_round='fsm_r9',source_checkpoint=str(source.relative_to(HERE)),source_sha256=sha256(source),
        selected_round_ppo_updates=payload['ppo_updates'],selected_round_optimizer_steps=payload['optimizer_steps'],
        selected_snapshot_target_dr=payload['target_dr'],e0_sha256=E0_SHA,jump_sha256=sha256(JUMP_PATH),
        note='Experimental 9-minute snapshot. Full-DR final round is archived; full stair acceptance remains failed.'))
    print(proof)


if __name__=='__main__':main()
