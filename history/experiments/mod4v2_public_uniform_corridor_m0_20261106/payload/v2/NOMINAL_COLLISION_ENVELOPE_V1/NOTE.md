# Nominal P0 compiled-geometry envelope
One originalP0 model, one MjData, setter once consuming soleforward; integration/statics/DARE/oldQA0.
Nominal q_eq from own nominal_gain_v2, absolute crank=hip+delta; ROOT chassis frame, wheel phase0.
All robot bodyid>0 geoms versus separate collision-mask OR!=0; world excluded, not an environment corridor collision test.
geom_aabb is local center+halfsize: local8 corners transformed by actual geom pose then into ROOT; mesh scale/PCA already compiled, no double mesh transform.
Boxes enclose primitives/mesh; union is conservative at THIS joint pose, not exact mesh hull or arbitrary-joint sweep.
Any nonfinite/negative/allzero box stays unknown; incomplete envelope fields remain null, no extra run.
Requested top-level bbox_all_root3_min_m / max_m / max_corner_norm_m are in RESULT.
1nm numeric padding is not manufacture/calibration margin.
Example eachRPY error<=.1 yields principal angle<=.3, displacement<=2Rsin(.15); lateral±.2 separately added, fixedjoint rigid rotation only.
Root0 with ground intersection is pose-only: no integration, no physical-contact inference.
Official source: https://raw.githubusercontent.com/google-deepmind/mujoco/main/src/user/user_objects.cc (main not pinned; installed header and primitive numeric check retained).
