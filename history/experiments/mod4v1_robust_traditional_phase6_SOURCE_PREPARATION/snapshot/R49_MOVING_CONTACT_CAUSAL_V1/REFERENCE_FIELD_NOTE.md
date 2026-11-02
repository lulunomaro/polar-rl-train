# V3 reference-field note (read derived metadata only)

In timed_capture the legacy phase.target_q4 can still retain flight values; it is not the actual current V3 leg-reference. Read landing_position_ref4/landing_transition_weight instead. Earlier SUPPLEMENT target column quotes the legacy field verbatim and is not a claim of a large tracking error in settled capture.

|event|phase|legacy target_q4|V3 landing_position_ref4|transitionweight|
|---|---|---|---|---|
|first_main_firstbar|timed_push|[0.4008466044556874, -0.012693947601226722, 0.4008466044556874, -0.012693947601226722]|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|0.0|
|first_landing|predicted_flight_retract|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|0.0|
|first_guide|predicted_flight_retract|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|0.0|
|last_guide|predicted_flight_retract|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|0.0|
|rear_cross_in_later_air|timed_capture|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|0.0|
|first_nextbar|timed_capture|[0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446]|[0.25032810955413787, 0.050328109554137856, 0.25032810955413787, 0.050328109554137856]|1.0|

At firstguide the two reference fields agree and capture is not started; the guide event timing finding is unchanged. At nextbar use the completed nominal landing reference, not the old crouch/flight target. No candidate/gain/score/source modified.
