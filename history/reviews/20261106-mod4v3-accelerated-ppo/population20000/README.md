# User-requested population increase to 20,000

User: “换成20000环境吧”. This amends the already authorized official rough
continuation from 4,096 to 20,000 environments. The currently running 4,096
segment is not hot-patched or terminated. Its full save, safe close and
independent80/actual-pose recording remain the transition boundary.

The next task retains MOD4v3 R3, installed official ROUGH_TERRAINS_CFG defaults,
PhysX TGS32/4, Warp fused closure/mimic sampling with preallocated outputs and
CUDA Graphs, PPO settings, reward weights, motor parameters, DR off and the
standing-forward targets. Actor/critic/STD, all 17 Adam states, learning rate and
RNG are restored from the source final. The 20,000 physical episodes are fresh;
this is not a claim of restored 4,096-instance physics in a larger population.

The selected terrain's shared-tile spawn grid is bounded by each actual 8 m
tile for the larger population. The previous fixed 10-column grid could put
20,000-env offsets outside their tiles. The changed grid keeps the source
4,096 layout intact and derives columns/rows from actual tile occupancy for
larger populations. GRID_VALIDATION.json records deterministic grid formula
checks; the real 20,000 GPU startup remains the required population check.

Only the task's idle CPU map-boundary waiter was stopped and relaunched to load
the amended plan. The source training child and other chats were untouched.
The waiting code reloads its plan at the actual boundary, and the restore
receipt explicitly distinguishes resized populations from physical state.

POPULATION_CHANGE_DISPATCH.json and DISPATCH_READBACK.json record the real
remote plan with num_envs=20000. The readback captured source iteration196 and
full checkpoint iteration196, plus the active waiting PID22662. It does not
claim that 20,000 environments were already running at that time.

An inspection for a presumed PhysX config filename under the source directory
returned no files and caused a reader IndexError. A second read under the env
site-packages also found no matching file. Neither attempted a simulator or
configuration mutation. No GPU buffer settings were changed from these reads.

Prior 4,096 rough plan, amended plan, current work order and dispatch evidence
are preserved alongside this note. Append actual startup/update or failure
receipts after the population transition; do not rewrite the pending evidence
as a completed GPU test.
