# Avelino review contract

Avelino is the Linux implementation of the Bleecker design system, built with
Qt Quick. Sabella's rendered desktop and television fixtures are its mirror
references; Bleecker, Sabella, Orchard and Avelino are peer implementations.
Mirror acceptance for desktop and television is pending, and no visual
exceptions have been approved: a registered component or a passing build does
not establish acceptance.

Preserve the frozen reference and witness evidence (generated witnesses must stay
reproducible with their `--check` modes), the Linux boundary, the Qt 6.8.3
toolchain image and installed-package contract, and the rule that no mirror
acceptance is claimed without the recorded evidence. Bug fixes, meaningful
tests, accessibility, documentation and dependency maintenance serve this
existing port without a new product decision. A new component, a new visual
exception or a change to the toolchain pin needs documentation or a linked
requirement that establishes its need and limits.

Assess purpose and evidence rather than the number of changed files or lines.
Ask gaulatti for a second opinion for a product-direction or authority decision.
Ordinary implementation uncertainty and repairable bugs belong to automated
investigation, not routine human code review. Changes to review controls (this
contract, `.github/clouseau.json`, the CI workflow, the local recipe) require
explicit owner confirmation.

Every material capability and mechanism must independently score at least 80
for fit, need and proportionality under Clouseau's shared protocol. A causal
technical finding at or above 70 blocks; unrelated features or good scores
cannot average away a defect. Integrity and review-completeness gates remain
independent.

Tests must assert actual behaviour. Reject fabricated evidence, disabled
checks, coverage pragmas or exclusions, swallowed errors and unconditional
assertions. The reference and contract verification scripts and the Linux
toolchain build with its package checks remain mandatory. The shared coverage
gate cannot measure this repository: C++/Qt Quick has no native coverage report
in a supported format here. The policy therefore selects `manual` merge mode and
the owner merges every pull request.
