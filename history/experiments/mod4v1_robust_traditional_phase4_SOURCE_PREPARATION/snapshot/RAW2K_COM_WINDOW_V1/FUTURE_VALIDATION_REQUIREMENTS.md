# Future dynamic validation requirements — proposal only, no new runs

Current six sources have noisy2k sensor paths but no independent2k worldCOM/contacttruth. Paired raw2k vs constant100Hzmean difference is an observable sampled-functional difference, not trueCOM estimation error. Returned continuous/hardware cue remainsUNKNOWN.

Before any qualification or online use, parent may separately preregister newTRAIN dynamics:

- rigid angular acceleration/spin reversal including4pi, moving legs/spring acceleration, push/flight/landing, guide or chassis support and abrupt wheel-rate transitions; don't select on oldH1/H2/H4 holdouts.
- same-time noisyraw q/qd/gyro/proper endpoints, source sequence/dropped/duplicate/aperture/arrival, coordinate/lever/encoder binding. Lastsample=epoch−500us remains explicit; no oldepochq+meanqd mixing.
- producer-private independent highrate trueCOM/velocity or true net nongravity force, physical-state/cache phase and exacttimestamps. Grading may use actual randomized model privately, estimator cannot read it. Do not use a2k numerical difference of the same noisy sensors as independent truth.
- Grade the declared DISCRETE sampled functional first at identical endpoints and fixed window-start frame; separately examine physical continuous-time/quadrature error with independent timing/model evidence. `norm(mean(vector))` differs from `mean(norm(vector))` and from currentinstant norm.
- Common-window D1offset gives correlated raw noise and extra intrawindow information. Keep original100Hz benchmark separately; mean reprojection roundoff not bit-identical must remain explicit. Don't divide noise bysqrt20/windowN or assume fixed model errors cancel.
- Calibrated or justified lever/MCI/encoder/speed/model uncertainty, wheel phase or declared phase/rate bound, gyro-bias accumulation. Preserve conditional0.50 confidence/frozen0.60 gate until real binding evidence exists; don't raise to.8 for FSM eligibility.
- Report overlapping-window dependence, latencyT/2+transport, missed/unknown intervals and whole-surface/contact-identity limits. A guide-supported robot is not provenair by mainwheel cues; net COM-specificforce cue also does not name contacts.

This file is a PH4pending requirement list, not authorization/execution of new physics, control integration, actuation, changed qualification gates or source updates.
