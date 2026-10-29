"""Original E2_WORLD_MOVING_SIGNED4 diagnostic labels; no SDK/RNG/commands changed."""
PROFILES=('standing','straight_negative','straight_zero','straight_positive','pure_negative','pure_positive','transition_initial_negative','transition_initial_positive','moving_yaw_minus4','moving_yaw_plus4')
TRANSITION_PHASES=('start_0_1','hold_1_4','brake_4_5','stop_5_6','reverse_6_7','reverse_hold_7_10','reverse_brake_10_11','final_stop_11_12','post12_stop')

def classify(torch,standing,pure,moving,transition,command,signed_yaw):
    assert not bool((standing&(pure|moving)).any()) and not bool((pure&moving).any())
    assert not bool((transition&~pure).any())
    key=torch.full_like(signed_yaw,-1,dtype=torch.long)
    key[standing]=0
    straight=~(standing|pure|moving)
    key[straight&(command[:,0]<0)]=1;key[straight&(command[:,0]==0)]=2;key[straight&(command[:,0]>0)]=3
    key[pure&~transition&(signed_yaw<0)]=4;key[pure&~transition&(signed_yaw>0)]=5
    key[transition&(signed_yaw<0)]=6;key[transition&(signed_yaw>0)]=7
    key[moving&(signed_yaw<0)]=8;key[moving&(signed_yaw>0)]=9
    assert bool((key>=0).all()),'Unclassified actual E2 command flags; no silent profile replacement'
    return key

def transition_phase(torch,phase_elapsed):
    boundaries=phase_elapsed.new_tensor([1.,4.,5.,6.,7.,10.,11.,12.])
    return torch.bucketize(phase_elapsed.contiguous(),boundaries,right=True)
