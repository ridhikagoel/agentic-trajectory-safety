"""Coder 1 literature codes (abstract-level) -> coding/lit_coder1.csv, plus a blank
sheet for Coder 2. Codes are from title + abstract only; full-text checks are a
listed limitation.

Block A fields: mechanism, state_scope, timing, evaluated_on, reports_fp_or_cost, reports_timeliness
Block B fields: state_scope (sequence / graph / both / ID), production_data (Y/N/ID)
"""
import csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

A = {  # idx: (mechanism, state_scope, timing, evaluated_on, fp_or_cost, timeliness)
 28:("hybrid","trajectory","online","benchmark","Y","N"),
 32:("graph-model","multi-agent","online","benchmark","Y","N"),
 34:("hybrid","multi-agent","online","case-study","N","N"),
 39:("rule","trajectory","pre-execution","benchmark","ID","N"),
 41:("benchmark","trajectory","post-hoc","benchmark","N","N"),
 45:("probabilistic","trajectory","predictive","simulation","ID","Y"),
 46:("llm-judge","trajectory","post-hoc","benchmark","Y","N"),
 56:("hybrid","multi-agent","online","synthetic","N","N"),
 58:("learned","trajectory","predictive","benchmark","Y","Y"),
 60:("learned","trajectory","pre-execution","benchmark","ID","N"),
 61:("formal","cross-trajectory","mixed","simulation","N","N"),
 66:("hybrid","trajectory","online","benchmark","N","N"),
 78:("benchmark","trajectory","online","benchmark","Y","N"),
 80:("learned","trajectory","online","benchmark","N","N"),
 82:("hybrid","trajectory","online","simulation","N","N"),
 85:("learned","trajectory","online","benchmark","Y","N"),
 91:("learned","trajectory","online","benchmark","N","N"),
 94:("benchmark","trajectory","online","benchmark","Y","Y"),
 101:("learned","trajectory","post-hoc","synthetic","N","N"),
 104:("hybrid","trajectory","pre-execution","benchmark","Y","N"),
 105:("learned","trajectory","post-hoc","benchmark","N","N"),
 116:("hybrid","multi-agent","post-hoc","benchmark","N","N"),
 120:("hybrid","session","online","preliminary","Y","N"),
 123:("rule","trajectory","pre-execution","benchmark","Y","N"),
 125:("rule","session","pre-execution","synthetic","Y","N"),
 131:("probabilistic","trajectory","predictive","benchmark","Y","Y"),
 134:("benchmark","trajectory","post-hoc","benchmark","N","N"),
 135:("rule","trajectory","online","real-traces","Y","N"),
 141:("benchmark","trajectory","online","benchmark","N","N"),
 143:("hybrid","trajectory","online","benchmark","N","N"),
 144:("benchmark","trajectory","post-hoc","benchmark","N","N"),
 147:("benchmark","trajectory","online","benchmark","Y","N"),
 148:("hybrid","session","online","benchmark","N","N"),
 153:("rule","trajectory","pre-execution","benchmark","Y","N"),
 156:("learned","session","online","synthetic","Y","N"),
 158:("hybrid","trajectory","pre-execution","benchmark","Y","Y"),
 159:("probabilistic","cross-session","online","benchmark","N","N"),
 160:("hybrid","window","pre-execution","benchmark","Y","N"),
 162:("graph-model","multi-agent","post-hoc","case-study","N","N"),
 165:("graph-model","multi-agent","post-hoc","benchmark","Y","N"),
 168:("position","multi-agent","none","none","N","N"),
 172:("representation","trajectory","online","benchmark","N","Y"),
 173:("benchmark","multi-agent","post-hoc","benchmark","N","N"),
 174:("formal","trajectory","predictive","benchmark","N","Y"),
 177:("probabilistic","trajectory","predictive","ID","N","Y"),
 184:("llm-judge","cross-session","post-hoc","benchmark","N","N"),
 185:("hybrid","cross-session","post-hoc","benchmark","N","N"),
 187:("ifc-provenance","trajectory","pre-execution","benchmark","N","N"),
 190:("hybrid","trajectory","online","benchmark","Y","N"),
 191:("representation","trajectory","predictive","benchmark","N","Y"),
 192:("benchmark","multi-agent","online","benchmark","Y","N"),
 194:("learned","trajectory","post-hoc","benchmark","N","N"),
 205:("benchmark","trajectory","predictive","benchmark","N","Y"),
 209:("llm-judge","trajectory","post-hoc","real-traces","Y","Y"),
 210:("hybrid","trajectory","pre-execution","benchmark","N","N"),
 229:("representation","trajectory","online","benchmark","N","ID"),
 236:("formal","trajectory","online","benchmark","N","N"),
 245:("benchmark","trajectory","post-hoc","production-harness","N","N"),
 249:("benchmark","multi-agent","online","synthetic","N","N"),
 259:("benchmark","trajectory","post-hoc","benchmark","N","N"),
 264:("ifc-provenance","trajectory","pre-execution","benchmark","ID","N"),
 267:("learned","trajectory","predictive","benchmark","Y","Y"),
 268:("benchmark","trajectory","post-hoc","production-harness","N","N"),
 275:("ifc-provenance","multi-agent","pre-execution","benchmark","Y","N"),
 276:("formal","trajectory","online","benchmark","N","N"),
 280:("learned","trajectory","predictive","benchmark","Y","Y"),
 284:("benchmark","trajectory","post-hoc","benchmark","N","N"),
 291:("learned","trajectory","post-hoc","benchmark","N","N"),
 293:("benchmark","trajectory","post-hoc","benchmark","N","N"),
 296:("representation","multi-agent","online","synthetic","N","N"),
 300:("ifc-provenance","trajectory","online","benchmark","N","N"),
 303:("rule","trajectory","pre-execution","simulation","Y","N"),
 304:("learned","trajectory","post-hoc","benchmark","N","N"),
 305:("learned","trajectory","pre-execution","benchmark","Y","N"),
 311:("ifc-provenance","trajectory","pre-execution","benchmark","Y","N"),
 312:("formal","cross-trajectory","online","none","N","N"),
 313:("representation","trajectory","online","benchmark","N","Y"),
 318:("probabilistic","trajectory","online","benchmark","Y","Y"),
 333:("rule","trajectory","online","none","N","N"),
 334:("hybrid","window","pre-execution","benchmark","ID","N"),
 335:("rule","trajectory","online","real-traces","N","N"),
 337:("formal","trajectory","mixed","benchmark","N","N"),
 338:("formal","trajectory","pre-execution","benchmark","Y","N"),
 342:("learned","trajectory","post-hoc","real-traces","N","N"),
 344:("ifc-provenance","trajectory","online","benchmark","N","N"),
 349:("benchmark","trajectory","predictive","benchmark","N","Y"),
 354:("benchmark","trajectory","online","benchmark","N","N"),
 361:("representation","trajectory","post-hoc","benchmark","N","N"),
 363:("learned","trajectory","online","benchmark","N","Y"),
 371:("hybrid","trajectory","predictive","ID","Y","Y"),
}
B = {  # idx: (state_scope, production_data)
 1:("sequence","N"),2:("both","N"),5:("sequence","Y"),10:("both","N"),11:("both","N"),14:("sequence","N"),
 15:("graph","N"),17:("both","N"),19:("sequence","ID"),20:("graph","N"),21:("both","N"),22:("sequence","N"),
 23:("graph","N"),24:("graph","Y"),26:("sequence","N"),31:("both","N"),35:("both","N"),36:("sequence","N"),
 37:("both","N"),38:("graph","ID"),40:("graph","N"),43:("graph","ID"),44:("both","N"),45:("both","N"),
 47:("graph","N"),48:("graph","ID"),50:("ID","N"),51:("graph","N"),52:("graph","ID"),54:("both","N"),
 55:("graph","N"),57:("both","N"),59:("sequence","N"),60:("sequence","Y"),62:("both","N"),63:("graph","N"),
 65:("graph","ID"),67:("graph","N"),71:("both","N"),74:("sequence","N"),78:("ID","N"),82:("sequence","ID"),
 83:("sequence","N"),
}

out = os.path.join(ROOT, "coding")
for blk, codes, fields in [("A", A, ["mechanism","state_scope","timing","evaluated_on","reports_fp_or_cost","reports_timeliness"]),
                           ("B", B, ["state_scope","production_data"])]:
    rows = [x for x in csv.DictReader(open(os.path.join(ROOT, "raw", f"s3_stage2_{blk}.csv"), newline=""))
            if x["stage2"] == "include"]
    assert {int(x["idx"]) for x in rows} == set(codes), blk
    for name, fill in [(f"lit_{blk}_coder1.csv", True), (f"lit_{blk}_coder2_blank.csv", False)]:
        with open(os.path.join(out, name), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["idx", "arxiv_id", "title"] + fields)
            for x in rows:
                c = codes[int(x["idx"])] if fill else [""] * len(fields)
                w.writerow([x["idx"], x["id"], x["title"]] + list(c))
    print(blk, len(rows))
