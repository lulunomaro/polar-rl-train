# Native phase retention: conditional next-candidate review only

Keep the current86B run unchanged. Its first real positive proof confirms the
restored68/680WM/58Pi source reached its first new Pi at control72 and sampled80
starts in age100–135 among1536 attempted starts. That establishes the initial
scheduling repair. It does not establish complete-window phase coverage,
completed-Pi counts from sampling calls, convergence or physical skill.
The cached phase snapshot and preupdate event snapshot are different observation
points; they must not be combined as one synchronous control frame.

This review read the current86B payload's exact source copies and the existing
first-proof/work-order JSON. Four new tiny source/interface metadata checks
passed4/4. No candidate sampler was written or installed; no real PT/raw/NPZ,
remote/GPU/actor/physics rollout, Git or ledger operation occurred. The three old
helper directories remain frozen. These CPU checks are not target runtime proof.

## What the actual code does

ReplayBuffer is a fixed device-resident64×20000 time/environment ring. Its fields
are s73f32, s1:73f32, a6f32, a_prev6f32, xi49f32, r:f32, f:i64,
ep_step:i32 and done:bool: **845bytes per transition**,1,081,600,000 logical
bytes total, about1.007GiB. Existing active obs_hist is another102,400,000 bytes;
that is separate from replay and is not a source-history archive.

sample_starts draws age and environment uniformly from the currently stored
ring. It returns only raw `s,a_prev,xi,f` for the start and oldest-first padded
history. It returns no environment or episode ID. History backtracking is capped
by both saved ep_step and available ring age. The tiny interface check confirms
its final history row equals the returned start and a synthetic reset does not
pull preceding-episode history across that boundary.

The source bridge records transition f/ep_step from the pre-action info, records
pre-reset s1 from the original trace, then obtains the reset plant's next state.
done resets bridge ep_step and previous action to zero. The original physical
loop increments age before selected reset, then resets only selected IDs. This
ordering stays unchanged; there is no proposal to extend an episode or age.

WM trains on original8-step actual-transition windows. Pi requests512 valid
starts, hist10 and horizon16. Its current valid_imagination_start accepts every
frame; the partial-reference wrapper delegates this method. The shared original
CUDA RNG also serves collection action noise, so extra unreviewed global sampling
draws would change more than archive selection.

A finite ring can still lose an old request phase. In a single unreset
trajectory with age=f and C completed controls, the64 ring retains f=C−64…C−1.
Its last initial100…179 sample disappears at C244; original24-control policy
cadence last sees it at C240, then not C264. This is a source deduction, **not**
the observed86B population: selected resets can create new request phases later.
Expanding to128 or256 only moves that finite boundary;256 costs4,326,400,000
logical bytes, about3.02GiB more than64. The current frozen restore also rejects
changing buffer_steps because native args must match exactly. Increasing it is
not a free deployment choice or a permanent retention guarantee.

## Small bounded candidate, only if completed86B evidence supports it

Prefer reviewing an **ephemeral pool of starts already returned by the original
fresh-ring sampler**, rather than increasing WM replay or inventing foreign
transitions. Keep64 ring, original WM windows, network dimensions, trained
WM/Pi/critic weights and all three optimizers. Capture only originally valid
sampled starts with100≤f<180, together with the complete already-padded raw
history10. Capture the fresh original batch before any future composition;
never feed archive-selected records back into the archive as new physical data.

Suggested review bounds are K8192 FIFO records, fixed512 maximum admission/gather
batch and **64MiB extra logical tensor ceiling**. One raw start is520bytes;
start plus10-row history is5720bytes. Four i64 provenance values add32bytes:
sample-call sequence, sample index, native iteration, completed-control count.
These are available without guessing environment/episode IDs.

| Bounded storage | Logical bytes | MiB |
|---|---:|---:|
|8192×5752byte records|47,120,384|44.9375|
|Two maximum512-record scratch sets|5,890,048|5.6171875|
|Total candidate tensors|53,010,432|50.5546875|

This bounds the declared tensors, not the complete CUDA allocator/workspace or
task peak. Actual future memory headroom and target admission still apply.
Preallocation, detached copying and bounded scratch are required; retaining
references to the live ring, computation graphs or an unbounded Python list is
not this candidate.

An explicit future example is128 archived plus384 fresh starts per Pi when the
pool is nonempty. This **changes the sampling distribution**; it must not be
called the unchanged uniform-recent method. Keep the original fresh512 sampler
call and its original global RNG consumption. Archive selection would need its
own explicitly seeded device Generator, not torch.manual_seed or extra global
randint. Filling a FIFO from the original returned batch needs no RNG. Retained
selection should be uniform within the finite retained pool, with replacement,
and retain actual raw s/a_prev/xi/f, not cached normalized observations. A pool
with only80 records contains80 records, not8192 distinct experiences.

The raw histories are reused only as imagination starts. They are never injected
into the live physical action history or assembled later across resets. No
foreign Fudan transitions are added to WM. No age, reset, reward, action,
command, physics or original success threshold changes are proposed.

For the smallest first candidate, the pool starts empty at every new physical
continuation window and is explicitly not checkpointed, just like current
unsaved replay. This avoids silently changing the model save payload by another
45MiB per frequent preupdate save. It also means pool/RNG state is not resumed
exactly. A later persisted pool would require a separate reviewed publication,
source/disk/save-time contract; that is outside this proposal.

New instrumentation would have to distinguish fresh sampled starts, retained
starts and composed attempted starts. Existing cumulative phase counts cannot
be relabelled as fresh physical exposure, unique environments or completed Pi.
No new sampling implementation or instrumentation was added in this task.

## Decide from the completed86B phase and physical events first

| Completed result | Next decision |
|---|---|
|Fresh request-phase samples continue late in the window|Retention is not yet the demonstrated bottleneck; preserve the current method while assessing original task events and model/objective limitations.|
|Late fresh exposure disappears after earlier real100–179 exposure, and source/FINAL/cost are healthy|Review the bounded start-pool candidate with exact source/RNG/memory/semantics admission before proposing a distinct next window.|
|Only100–135 is observed;136–179 never appears|A pool cannot invent the missing later phase. Determine whether real episodes reached it; do not alter resets/ages or fabricate event coverage.|
|Physical takeoff/cross/land/recovery remain absent despite sustained relevant exposure|Do not blame all failure on the ring. Step-distance information, frozen imagined context and partial foreign-reference coverage remain separate existing limitations.|
|A source/finite/save/integrity failure occurs|Preserve the original failure and qualify sources through the existing full-state boundary; do not promote an unqualified partial result or blindly reuse the same window.|

Use the formal86B continuation FINAL/new-Pi delta, original complete-control
events, full collected phase report and actual independent fees/allout. The
current phase file stores cumulative bands and only its last call. Comparing the
first and final snapshots can show additional exposure and the ending sample,
but cannot prove uninterrupted exposure or identify every interval of starvation.
Missing optional phase data remains an observability limitation, not an added
model-health or skill gate. Do not make the current authorized close depend on
new FP64, tolerance or extra physical audits.

Reject a future retention candidate that silently changes trained parameters,
native dimensions/config, global RNG ownership, original recent sampler draw
count, WM data origin, reset/history boundaries or physical success semantics.
Reject an unbounded allocation, unstated distribution mixture, guessed episode
provenance, actor-history injection, foreign/synthetic physical transitions, or
a claim that80 cached starts prove general success. Require explicit reviewed
source pins and fresh actual target/resource/save admission for any future
implementation. This document grants no next GO, budget, deployment or replay
of a consumed once, and does not authorize another identical blind window.

All sources and first-proof SHA references are in the metadata CPU report. There
were no failed checks or failed attempts in this task; every saved artifact is
listed in the frozen index and awaits root's ordinary supplement to trial1457.
