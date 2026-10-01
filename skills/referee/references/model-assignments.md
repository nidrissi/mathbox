# Native delegation and model assignments

Keep review roles independent of provider names and harness APIs. These are
instructions for using the host's existing controls, not an API runner or a
new configuration format. Do not install providers, obtain credentials or
launch another harness to satisfy a model preference.

## Resolve assignments

Read model and reasoning preferences from the user's request and applicable
project instructions. An assignment can name any of `correctness`,
`adversarial`, `exposition`, `notation`, `claims`, and `final-referee`, or a
default for unspecified roles. It may be restricted to a named host. Apply
only assignments for the current host; never translate one provider's model
ID into a purported equivalent from another provider.

Follow instruction precedence: the user's assignment overrides project
defaults, subject to higher-priority host instructions and permissions.
Within one source, a role-specific assignment overrides its default. If
equally applicable assignments genuinely conflict, ask for clarification and
continue unaffected review work. Do not require a model preference merely to
start a review.

Resolve model and reasoning preferences independently; an unspecified field
inherits its applicable default. Name both instruction sources in provenance
when they supply different fields of the resolved assignment.

For example, a project can express its preferences in ordinary instructions:

```text
Referee model preferences for <host name>:
- default: <native model ID>
- correctness and adversarial: <native reasoning model ID>; reasoning <setting>
- final-referee: <native reasoning model ID>; reasoning <setting>
If a preference is unavailable, continue and disclose the fallback.
```

The angle-bracket values are placeholders, not model names to request. No
particular project file or metadata extension is required. Keep these
preferences in user/project instructions; shared skill frontmatter and
`agents/openai.yaml` do not acquire a model-routing schema.

Without a prescribed model, prefer an available model suited to mathematical
reasoning for correctness, adversarial review and final reconciliation, when
the host exposes enough information to choose one. Otherwise inherit the
host's default. Choose suitable available models for the other lanes without
inventing a capability ranking. Do not equate one host's reasoning labels
with another's; use only settings the current host actually supports. Respect
the user's budget and host limits.

## Apply native controls and fall back

Inspect the available delegation interface and documented capabilities.
When subagents are supported and authorized, start isolated reviewers and
pass the selected model and reasoning setting through the actual native
controls. A prompt telling a child to act as a named model does not select
that model. If the interface requires a fresh context to override settings,
supply the lane contract, protocol, exact source and dependencies explicitly.
Do not copy prior suspected answers into a fresh correctness review.

Use the same procedure in Codex, Claude and other harnesses: adapt to the
controls actually exposed in that session rather than assume shared parameter
names or a model catalog. A host that allows subagents but no model choice
still supports isolated review; inherit its settings and record the limitation.

If a model is unavailable, selection is forbidden, or a reasoning setting is
unsupported, use the suitable available alternative or inherited setting and
record exactly what could not be honored. Honor each supported part of an
assignment even when another part needs a fallback. Do not repeatedly attempt
an invalid model ID, block otherwise useful review, or treat a fallback as a
mathematical defect. A failed launch is not completed coverage; rerun the
affected scope with the fallback or leave it explicitly unreviewed.

Group lanes only when their resolved settings are compatible. Different
preferences can use separate agents sequentially when concurrency is limited.
Without authorized delegation, perform distinct sequential passes and label
them self-review, including their model-selection limitations.

For `final-referee`, apply the preference to the actual reconciliation
executor. If a prescribed setting requires a different executor, delegate
reconciliation to a compatible isolated agent when supported, supplying the
full source, protocol, coverage, raw findings and specialist artifacts. Check
the returned reconciliation and report before delivery. Otherwise reconcile
directly and disclose the inherited settings as the fallback. Do not claim
that the coordinator changed models because its prompt requested a different
one.
With no final-referee preference, the coordinator can reconcile directly.

## Record execution honestly

Follow [output-contract.md](output-contract.md) for every review pass and final
reconciliation. Distinguish the prescribed model/setting, the requested native
controls, and what the host actually confirms. A successful launch or echoed
request alone does not authenticate the model that ran. Use `null` for an
unexposed actual model or reasoning setting, and retain the available tool or
session evidence. Record model and reasoning substitutions separately in the
fallback explanation. Unknown identity alone does not imply a substitution.

When reusing a prior pass, preserve its original execution provenance; a new
preference does not relabel historical work. Check whether that evidence
satisfies the current assignment and report any deviation. Missing historical
settings remain unknown. Model diversity and isolated contexts can reduce
shared errors; neither establishes mathematical correctness or independence
by itself.
