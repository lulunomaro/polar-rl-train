#ifndef PA1_ALLOCATOR_H
#define PA1_ALLOCATOR_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define PA1_AXES 6u
#define PA1_BISECTIONS 40u
#define PA1_LOAD_SIDE_NM_RAD_S 1u
/* Each bit is a CALLER evidence assertion, not a hardware discovery. */
#define PA1_CAL_COORD_CURRENT UINT32_C(0x001)
#define PA1_CAL_GEAR_SIGN UINT32_C(0x002)
#define PA1_CAL_QUADRANTS UINT32_C(0x004)
#define PA1_CAL_K_LOWER UINT32_C(0x008)
#define PA1_CAL_BUS_LOSS UINT32_C(0x010)
#define PA1_CAL_EFFICIENCY UINT32_C(0x020)
#define PA1_CAL_VOLTAGE_DOMAIN UINT32_C(0x040)
#define PA1_CAL_TEMPERATURE_DOMAIN UINT32_C(0x080)
#define PA1_CAL_SPEED_DOMAIN UINT32_C(0x100)
#define PA1_CAL_CURRENT_DOMAIN UINT32_C(0x200)
#define PA1_CAL_INDEPENDENT_EVIDENCE UINT32_C(0x400)
#define PA1_CAL_REQUIRED UINT32_C(0x7ff)
#define PA1_FRAME_COORDINATES UINT32_C(0x01)
#define PA1_FRAME_REACHABLE_SPEED UINT32_C(0x02)
#define PA1_FRAME_LIVE_BUS UINT32_C(0x04)
#define PA1_FRAME_TEMPERATURE UINT32_C(0x08)
#define PA1_FRAME_SIGNED_DC_BOX UINT32_C(0x10)
#define PA1_FRAME_QUALIFIED_RESERVE UINT32_C(0x20)
#define PA1_FRAME_BUDGETS UINT32_C(0x40)
#define PA1_FRAME_DRIVER_RATE UINT32_C(0x80)
#define PA1_FRAME_REQUIRED UINT32_C(0xff)
#define PA1_ALL_QUADRANTS UINT32_C(0xf)
/* Calibration bits: coordinate/current convention, gear/sign, quadrants,
   K lower, bus-loss envelope, drive/regen efficiency, voltage, temperature,
   speed, current domain, independent evidence. All default UNBOUND. */
/* Frame bits: coherent load coordinate, reachable speed, live voltage,
   temperature interval, signed-DC box, qualified reserve, budgets, driver-rate. */
typedef enum {
 PA1_OK=0, PA1_RESERVE_INFEASIBLE=1, PA1_RESERVE_UNCERTIFIED=2,
 PA1_DEADLINE=3, PA1_CLOCK_ERROR=4, PA1_UNBOUND=5, PA1_BAD_ARGUMENT=6,
 PA1_BAD_CONTEXT=7, PA1_BAD_ALIAS=8, PA1_NONFINITE=9, PA1_BAD_DOMAIN=10,
 PA1_STALE=11, PA1_NUMERIC=12, PA1_LATCHED=13, PA1_BAD_OPTIONS=14,
 PA1_INVALID_FRAME=15
} pa1_status;
typedef enum {
 PA1_PHASE_ENTRY=0, PA1_PHASE_VALIDATED=1, PA1_PHASE_RESERVE=2,
 PA1_PHASE_REQUEST=3, PA1_PHASE_BISECTION=4, PA1_PHASE_FINAL_CHECK=5,
 PA1_PHASE_FINAL_POLL=6
} pa1_phase;
typedef enum {
 PA1_SOURCE_SPEED=0, PA1_SOURCE_BUS=1, PA1_SOURCE_TEMPERATURE=2,
 PA1_SOURCE_BOX=3, PA1_SOURCE_LIMITS=4, PA1_SOURCES=5
} pa1_source;
/* Return exactly 1 with an available monotonic ns sample, otherwise fault. */
typedef int (*pa1_clock_fn)(void *context,pa1_phase phase,uint32_t iteration,
                           uint32_t axis,uint64_t *now_ns);
typedef struct { double lo,hi; } pa1_interval;
typedef struct {
 uint32_t bindings,coordinate_id,quadrants[PA1_AXES];
 uint64_t evidence_id,valid_from_ns,valid_until_ns,max_observation_age_ns;
 double Kload_lower_Nm_per_A[PA1_AXES];
 double Cbus_loss_upper_W_per_A2[PA1_AXES]; /* BUS referred, NOT winding ohms. */
 double eta_drive_lower[PA1_AXES],eta_regen_upper[PA1_AXES];
 double current_domain_max_A[PA1_AXES],speed_domain_abs_max_rad_s[PA1_AXES];
 double temperature_domain_lo[PA1_AXES],temperature_domain_hi[PA1_AXES];
 double voltage_domain_lo_V,voltage_domain_hi_V;
} pa1_calibration;
typedef struct {
 uint32_t valid,bindings,coordinate_id;
 uint64_t calibration_evidence_id,frame_id,drive_frame_id;
 uint64_t sampled_ns[PA1_SOURCES],valid_until_ns[PA1_SOURCES];
 double reserve_tau_Nm[PA1_AXES],requested_tau_Nm[PA1_AXES];
 double torque_lo_Nm[PA1_AXES],torque_hi_Nm[PA1_AXES];
 double speed_lo_rad_s[PA1_AXES],speed_hi_rad_s[PA1_AXES];
 double temperature_lo[PA1_AXES],temperature_hi[PA1_AXES];
 double axis_current_limit_A[PA1_AXES];
 double bus_voltage_lo_V,bus_voltage_hi_V;
 double electronics_other_upper_W,positive_power_limit_W,charge_power_limit_W;
 double discharge_bus_current_limit_A,charge_bus_current_limit_A;
} pa1_input;
typedef struct {
 uint64_t cycle_start_ns,budget_ns;
 pa1_clock_fn clock;
 void *clock_context;
 size_t clock_context_bytes; /* Entire callback-owned range must be disjoint. */
} pa1_options;
typedef struct {
 pa1_interval positive_power_W,charge_power_W;
 pa1_interval discharge_bus_current_A,charge_bus_current_A;
 pa1_interval axis_current_A[PA1_AXES];
} pa1_certificate;
typedef struct {
 uint32_t evaluations,iterations,clock_polls,last_phase,last_axis;
 uint64_t start_observed_ns,last_ns,elapsed_ns;
} pa1_stats;
typedef struct {
 pa1_status status,first_latched_fault;
 uint32_t valid,reserve_evaluated,reserve_certified;
 uint32_t reserve_not_certified_mask,reserve_proven_violation_mask;
 double s,s_not_certified_hi,tau_Nm[PA1_AXES];
 pa1_certificate accepted; /* Zero unless valid. */
 pa1_certificate reserve_diagnostic; /* Nonaccepted diagnostic only. */
 pa1_stats stats;
} pa1_result;
typedef struct {
 uint32_t magic,magic_inverse,have_clock;
 pa1_status latched_fault;
 uint64_t last_clock_ns;
 pa1_calibration calibration;
} pa1_context;
typedef struct {
 pa1_interval torque[PA1_AXES];
 double rounded_tau[PA1_AXES],saved_tau[PA1_AXES];
 pa1_certificate trial,reserve,saved;
} pa1_workspace;
/* Defaults create UNBOUND objects; zero reserve arrays are not qualified. */
void pa1_calibration_default(pa1_calibration *calibration);
void pa1_input_default(pa1_input *input);
pa1_status pa1_calibration_validate(const pa1_calibration *calibration);
pa1_status pa1_init(pa1_context *context,const pa1_calibration *calibration);
/* Context/input/options/workspace/result/clock range must be disjoint.
   An aliased result is unusable (do not overwrite source to zero it).
   Invalid tau6=0 is NOT a safe reserve/fallback, particularly at overspeed.
   Final poll covers only elapsed execution up to that sample, not driver.
   Context/workspace are exclusive to this call and may not be used by the
   callback or concurrently by another thread. Input reserve stays untouched. */
pa1_status pa1_allocate(pa1_context *context,const pa1_input *input,
 const pa1_options *options,pa1_workspace *workspace,pa1_result *result);
#ifdef __cplusplus
}
#endif
#endif
