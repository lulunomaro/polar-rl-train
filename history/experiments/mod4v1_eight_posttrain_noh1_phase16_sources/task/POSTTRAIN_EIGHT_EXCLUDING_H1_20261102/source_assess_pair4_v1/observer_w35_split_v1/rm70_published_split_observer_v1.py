"""Pure row-metadata counts only. No I/O, thresholds, clock, RNG or SDK.
Grouping uses the original row.standing boolean, not speed/velocity proxies.
The original natural-complete and accepted booleans are read, never recomputed.
"""
ROW_FIELD_MAPPING=dict(record_type='same_UID_original_RM70_command',group_field='standing',
    complete_field='natural_complete_nonterminal_interval',accepted_field='complete_interval_bounds_fact')

def empty_counts():
    return dict(moving_complete=dict(count=0,original_bounds_met=0),standing_complete=dict(count=0,original_bounds_met=0))

def observe_row(counts,row):
    """Stateless: return independent updated counts, leave row/counts untouched."""
    out={k:dict(v)for k,v in counts.items()}
    if row.get('record_type')!=ROW_FIELD_MAPPING['record_type']:return out
    for field in('standing','natural_complete_nonterminal_interval','complete_interval_bounds_fact'):
        if type(row[field])is not bool:raise ValueError('Original row boolean expected: '+field)
    complete=row['natural_complete_nonterminal_interval'];accepted=row['complete_interval_bounds_fact']
    if accepted and not complete:raise ValueError('Original accepted fact must imply original complete fact')
    if not complete:return out
    key='standing_complete'if row['standing']else'moving_complete'
    out[key]['count']+=1;out[key]['original_bounds_met']+=int(accepted)
    return out

def publish_counts(counts,original_events,book_constructor_model_label):
    out={k:dict(v)for k,v in counts.items()}
    if sum(v['count']for v in out.values())!=original_events['natural_complete_intervals']:
        raise ValueError('Observed original complete rows do not match original book aggregate')
    if sum(v['original_bounds_met']for v in out.values())!=original_events['complete_kinematic_bounds_met']:
        raise ValueError('Observed original accepted rows do not match original book aggregate')
    out.update(source_row_field_mapping=dict(ROW_FIELD_MAPPING),metric_or_grouping_threshold_changed=False,
        counting_point='Existing RM70Intervals227.emit_columns row immediately before original self.rows.append(row)',
        counts_are_original_booleans_not_new_skill_predicates=True,
        book_constructor_model_label=book_constructor_model_label,
        actor_identity_authority='Actual FINAL.source_cache/Task loaded actor identity; this book label never overrides it',
        phase_reference_root_vs_COM_worldgetter_gap_still_unresolved=True,
        original_accepted_cohort_or_full_RM70_graduation_claimed=False)
    return out
