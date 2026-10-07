## graphify

This project has a knowledge graph at `graphify-out/` with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"` before doing anything else.

Rules:
- For codebase questions where repository structure, dependencies, ownership, or cross-file context may matter, first run `graphify query "<question>"`. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than `GRAPH_REPORT.md` or raw grep output.
- Skip Graphify when the relevant file or symbol is already known and no cross-file reasoning is needed, when the task is about stale or incorrect graph output, or when the user explicitly says not to use it.
- Dirty `graphify-out/` files are expected after hooks or incremental updates; dirty graph files are not a reason to skip Graphify.
- If `graphify-out/wiki/index.md` exists, use it for broad navigation instead of raw source browsing.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Laya (local decision MCP)

Laya (`laya_*` MCP tools) is a cheap local decision layer for small typed decisions.

It sees only the `state` you pass — it never reads files or the repo — so a decision is only as good as the candidates and descriptions you put in `state`.

Which tool:
- `laya_decide` — default when the desired output shape is known. Schema of enums / booleans / bounded ints → typed values + per-field confidence. Pass `min_confidence` when abstention is preferable to a weak answer; `0.7` may be used as an initial heuristic, not a universal threshold.
- `laya_predict_batch` — evaluate many independent typed-decision requests together. Useful when applying the same decision schema to multiple candidate files, modules, or states.
- `laya_shortlist` — use for a choice with more than 20 options.
- `laya_predict` — use when explicit `choice`, `score`, or yes/no (`noul`) questions are more convenient than a schema-driven decision.

Good fits: filtering or ranking Graphify results before opening files; yes/no "do I need more context?" decisions; picking one of a few already-enumerated modules, files, tools, or actions.

Not for: writing or editing code, performing debugging or root-cause analysis, architectural reasoning,
open questions, or a candidate set you have not enumerated. It may assist with triage during these
tasks, but never replaces source inspection or main-model reasoning.

Skip it when the answer is already obvious from context — building `state` would cost more than the decision.

With Graphify:

`graphify (structure) → Laya (rank/filter, optional) → read only the strongest candidates → main model reasons and decides`

Laya is optional in this pipeline. Do not invoke it mechanically after every Graphify query.

Authority: Laya is advisory. It never decides HIGH-risk routing (Gard / Archie / Pipe), whether a hook or gate prompt can be dismissed, or whether a change is trivial enough to skip review.

On a `null` / low-confidence answer, ambiguous candidates, or a decision that could lead to a significant code change, read the source instead. If the server is unavailable, continue without it — never block on Laya.
