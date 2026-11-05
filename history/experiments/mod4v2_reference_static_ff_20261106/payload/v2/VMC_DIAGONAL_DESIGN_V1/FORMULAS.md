# Nominal virtual-coordinate PD coupling — geometry only

- [PREEXEC](<PREEXEC.json>) / [fresh small-input pins](<PREEXEC_INPUT_PINS.json>) / [single-run RESULT](<RESULT.json>) / [helper](<compute_once.py>); no controller or gain adoption. Public q0 is absolute hip/crank `.250328110365/.050328110365` on each side, not hip/delta.
- ROOT/chassis r=`[-.034202394679,-.238543198153]`m; l=`.240982698936`m; phi=`atan2(x,-z)=-.142409708402`rad. No thigh-origin subtraction.
- Left T0=`[[-.162462366696,+.162462366697],[-.452247995524,-.547752004482]]`; rows m/rad and rad/rad. Right independently computed; max T difference `1.46495593434e-11`.
- Kvirt=`[[2293.9764228473,70.54237426447],[70.54237426447,239.9999999974]]`; Dvirt=`Kvirt/30`. They are SPD, normalized cross rho=`.095071419183`, not a huge coupling or a root-cause certificate.
- Units of K entries: `[[N/m,N/rad],[Nm/m,Nm/rad]]`; D: `[[Ns/m,Ns/rad],[Nms/m,Nms/rad]]`. SPD means positive energy with conjugate units; raw mixed-unit condition/eigenvalues depend on scaling. Normalized correlation is unit-scale invariant (rad treated SI dimensionless).
- Delete virtual offdiagonal only: Kj=`[[109.63404081187,-1.094521887237],[-1.094521887237,132.555002962814]]` Nm/rad; Dj=`Kj/30` Nms/rad. Joint eigenvalues become `109.581893836/132.607149938`, ratios `.913182449/1.105059583` to120I. Thus one direction softens8.68%, one stiffens10.51%; this is NOT uniform softening, extra damping, or a demonstrated explanation of support loss.

## One hypothetical M2 mapping, not selected

To isolate the coordinate change while preserving the existing joint-common loop, use the shared frozen nominal tangent, not a claim of exact nonlinear length/angle control:

`e_tilde = T0*((qrefL-qL)-(qrefR-qR))`

`edot_tilde = T0*((vrefL-vL)-(vrefR-vR))`

`u = .5*(diag(Kvirt)*e_tilde + diag(Dvirt)*edot_tilde)`

`delta_tauL = T0.T*u; delta_tauR = -delta_tauL`

Equivalently use `.5*(Kj*(eqL-eqR)+Dj*(evL-evR))` and its negative. Do not add this on top of the existing differential PD; if parent ever selects it, replace only that term. This task selects no scalar multiplier/grid/axial-D/MPC change. It does not supply new measured Fn, alpha, support/contact permission or confidence.

For static refs, `U=.25*ediff.T*Kj*ediff` and damping power `P=-.5*vdiff.T*Dj*vdiff<=0` before saturation/delays/PD/DC/DR. The one work vector gave `P=-.429488093475W`, exact linear virtual-work discrepancy0J, tiny nonlinear FK discrepancy `6.35802094330e-16J`. Moving refs may inject energy; independent saturation need not preserve passivity.

For TRUE nonlinear z=[l,phi], the power-conjugate map instead is `uL=u,uR=-u; tauL=TL.T*u,tauR=-TR.T*u`. It has virtual-effort zero sum but joint-common increment `(TL.T-TR.T)*u`, generally nonzero. Conversely the shared-T0 joint-zero-sum map above yields actual efforts `TL^-T*T0.T*u` and `-TR^-T*T0.T*u`, generally not virtual-zero-sum. Do not promise both for TL!=TR. Neither property by itself guarantees vertical support-force balance or root-pitch neutrality in the coupled body/gas/contact dynamics.

**Sign:** phi as specified here has conjugate effort u_phi=-physical body+y wheel-force moment. [Existing nominal_model.leg_coordinates](<../CONTACT_PROXY_V2/nominal_model.py#L172-L184>) uses the opposite angular coordinate and physical Tp_y. Outward length effort is -axial compression. Never rename u_phi as Tp_y or flip only a torque sign while retaining the other coordinate convention.

**Optional bridge check NOT performed:** [bridge_v2](<../bridge_v2.py#L7-L21>) imports MuJoCo and physical bridge modules at top level; geometry() itself constructs public pins, but calling through the actual module violates this run's zero-SDK-import PREEXEC. Per parent instruction no AST-copy alternative or extra geometry check was built. Actual control-geometry T0 alignment remains unverified here; no schema/control substitution implied.

Cost: one public nominal derivatives call (base+8 fixed FK stencil evaluations), one additional tiny FK pose, total10 pure FK calls; no old three-pose validator, SDK import, model compile/forward/step, statics/DARE, old raw/QA, controller edit, hardware, Git, Goal or agents. 9.51% coupling only establishes a modest coordinate effect; it does not compel selecting diagonalization as M2. Parent owns the physical candidate decision.
