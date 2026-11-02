# State14 schema correction — documentation-only, original source preserved

Parent review found that SPR_AUDIT/portable_core_v1/README.md:19 labels columns4/6/11/13 as Lknee/Rknee and derivatives. That wording is wrong for the LQR gain state. The actual C code at ct_core.c:211–217 and frozen Python compute crank-minus-hip, not the passive knee angle. Existing source/math tests retain their bytes/hashes; this append-only erratum corrects the interpretation before deployment.

Authoritative14column order (zero-based):

|Index|Meaning|
|---|---|
|0|Estimated chassis-origin forward displacement gauge|
|1|Unwrapped chassis heading yaw|
|2|Chassis pitch|
|3|Left hip angle|
|4|Left crank angle MINUS left hip angle (`delta_L`)|
|5|Right hip angle|
|6|Right crank angle MINUS right hip angle (`delta_R`)|
|7|Estimated chassis-origin forward body velocity|
|8|Euler heading rate|
|9|Euler pitch rate|
|10|Left hip angular rate|
|11|Left crank rate MINUS left hip rate|
|12|Right hip angular rate|
|13|Right crank rate MINUS right hip rate|

The passive linkage knee angle is separately derived by closed-chainFK and used in wheel-body angular-rate kinematics; it is NOT substituted into state14[4] or [6]. Motor output row order remains Lhip,Lcrank,Lwheel,Rhip,Rcrank,Rwheel. Any wheel-firstHAL mapping is an explicit separate binding, never an implicit reorder.

This is a doc/schema correction, not a new robot episode or a realboard validation. Record with the next archive supplement if the prior snapshot was alreadysealed.
