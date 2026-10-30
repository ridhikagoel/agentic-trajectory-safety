# Results (final.csv)

## Screening flow
- S1 NVD: retrieved 1231; included 225; stage breakdown {('audit-sample', 'exclude'): 56, ('manual', 'include'): 94, ('manual', 'exclude'): 29, ('census', 'exclude'): 782, ('audit-sample2', 'exclude'): 47, ('census', 'include'): 61, ('audit-broad', 'exclude'): 52, ('audit-sample2', 'include'): 3, ('audit', 'exclude'): 40, ('audit-broad', 'include'): 21, ('audit', 'include'): 42, ('audit-sample', 'include'): 4}
- S2a AIID: keyword hits 71; title screen {'full-text': 29, 'E-NOAGENT': 29, 'E-MISUSE': 11, 'E-NONAI': 2}; full text {'include': 23, 'E-NONAI': 1, 'E-MISUSE': 2, 'E-INSCOPE': 2, 'E-DUP': 1}
- S2b primary disclosures: candidates 36; {'E-DUP': 5, 'E-SIM': 4, 'E-BENCH': 5, 'include': 14, 'E-DETAIL': 2, 'E-DATE': 6}
- S3 block A stage 2: {'exclude': 282, 'include': 90}
- S3 block B stage 2: {'exclude': 41, 'include': 43}
- S5 snowballing: new in-window references 1403; stage 1 {'no-abstract': 169, 'keep': 125, 'drop': 1109}; stage 2 {('exclude', ''): 223, ('include', 'B'): 31, ('include', 'A'): 21, ('unscreened', ''): 19}

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
- cves `per_action_flaggable`: ID=13, N=35, Y=178 (n=226)
- cves `min_state`: ID=13, none=178, resource-metadata=27, trajectory=8 (n=226)
- cves `monitor_present`: ID=8, N=92, Y=126 (n=226)

## Literature
- agent papers `mechanism`: benchmark=21, formal=11, graph-model=3, hybrid=22, ifc-provenance=9, learned=17, llm-judge=5, position=2, probabilistic=5, representation=7, rule=9 (n=111)
- agent papers `state_scope`: cross-session=7, cross-trajectory=2, multi-agent=13, session=5, trajectory=82, window=2 (n=111)
- agent papers `timing`: mixed=4, none=2, online=40, post-hoc=28, pre-execution=26, predictive=11 (n=111)
- agent papers `evaluated_on`: benchmark=81, case-study=3, none=5, preliminary=2, production-harness=2, real-traces=5, simulation=6, synthetic=7 (n=111)
- agent papers `reports_fp_or_cost`: ID=4, N=61, Y=46 (n=111)
- agent papers `reports_timeliness`: ID=1, N=97, Y=13 (n=111)
- fraud papers `state_scope`: ID=1, both=29, graph=26, sequence=18 (n=74)
- fraud papers `production_data`: ID=7, N=47, Y=20 (n=74)
