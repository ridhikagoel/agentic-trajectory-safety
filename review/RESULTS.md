# Results (final.csv)

## Screening flow
- S1 NVD: retrieved 1231; included 164; stage breakdown {('audit-sample', 'exclude'): 56, ('manual', 'include'): 94, ('manual', 'exclude'): 29, ('auto', 'exclude'): 843, ('audit-sample2', 'exclude'): 47, ('audit-broad', 'exclude'): 52, ('audit-sample2', 'include'): 3, ('audit', 'exclude'): 40, ('audit-broad', 'include'): 21, ('audit', 'include'): 42, ('audit-sample', 'include'): 4}
- S2a AIID: keyword hits 71; title screen {'full-text': 29, 'E-NOAGENT': 29, 'E-MISUSE': 11, 'E-NONAI': 2}; full text {'include': 23, 'E-NONAI': 1, 'E-MISUSE': 2, 'E-INSCOPE': 2, 'E-DUP': 1}
- S2b primary disclosures: candidates 36; {'E-DUP': 5, 'E-SIM': 4, 'E-BENCH': 5, 'include': 14, 'E-DETAIL': 2, 'E-DATE': 6}
- S3 block A stage 2: {'exclude': 282, 'include': 90}
- S3 block B stage 2: {'exclude': 41, 'include': 43}

## Incidents
- incidents `setting`: ID=1, eval=9, external-deploy=14, internal-deploy=3, product-vuln=1, training=9 (n=37)
- incidents `per_action_flaggable`: N=3, NA=1, Y=33 (n=37)
- incidents `min_state`: NA=1, none=33, resource-metadata=3 (n=37)
- incidents `precursor_signal`: ID=2, N=10, NA=1, Y=24 (n=37)
- incidents `monitor_present`: ID=6, N=19, Y=12 (n=37)
- incidents `detected_by`: ID=3, automated-monitor=8, external-party=9, transcript-review=3, user=14 (n=37)
- incidents `harm_external`: N=11, Y=21, unclear=5 (n=37)
- incidents `root_cause`: combination=15, environment-config=2, model=19, software-defect=1 (n=37)
- incidents with a flaggable step `monitor_present`: ID=5, N=17, Y=11 (n=33)
- incidents with a flaggable step `precursor_signal`: ID=2, N=7, Y=24 (n=33)
- incidents with a monitor running `detected_by`: automated-monitor=6, external-party=1, user=5 (n=12)

## CVEs
- cves `per_action_flaggable`: ID=10, N=19, Y=136 (n=165)
- cves `min_state`: ID=10, none=136, resource-metadata=13, trajectory=6 (n=165)
- cves `monitor_present`: ID=6, N=76, Y=83 (n=165)

## Literature
- agent papers `mechanism`: benchmark=18, formal=7, graph-model=3, hybrid=17, ifc-provenance=6, learned=16, llm-judge=3, position=1, probabilistic=5, representation=6, rule=8 (n=90)
- agent papers `state_scope`: cross-session=3, cross-trajectory=2, multi-agent=12, session=4, trajectory=67, window=2 (n=90)
- agent papers `timing`: mixed=2, none=1, online=36, post-hoc=23, pre-execution=17, predictive=11 (n=90)
- agent papers `evaluated_on`: benchmark=65, case-study=2, none=5, preliminary=1, production-harness=2, real-traces=5, simulation=4, synthetic=6 (n=90)
- agent papers `reports_fp_or_cost`: ID=4, N=52, Y=34 (n=90)
- agent papers `reports_timeliness`: ID=1, N=77, Y=12 (n=90)
- fraud papers `state_scope`: ID=1, both=16, graph=15, sequence=11 (n=43)
- fraud papers `production_data`: ID=3, N=30, Y=10 (n=43)
