---
name: integration-planner
description: Plan how to integrate a method, component, or implementation into an existing project by comparing the target codebase against one or more references, extracting the essential logic, and recommending the simplest viable path.
---

# Integration Planner

Use this skill when the task is to add a method, algorithm, component, subsystem, or implementation idea into an existing project. This includes cases where there are one or many reference repos, papers, code snippets, or prior implementations that may inform the integration.

Favor the simplest viable integration. Preserve the target project’s existing idioms, abstractions, and interfaces whenever possible. Be explicit about uncertainty, tradeoffs, and rejected complexity.

## What this skill is for

Use this skill when the work involves any of the following:

- comparing a target project against one or more reference repos
- deciding how to port or re-implement a method inside a current codebase
- identifying the minimal algorithmic core that must be added
- evaluating whether to adapt existing target abstractions or introduce new ones
- planning a safe, transparent integration before implementation
- designing a general integration path even when there is no single authoritative reference repo

This skill is not limited to repo-to-repo porting. It also applies to more general integration tasks, such as:

- embedding a new module into an existing training or inference pipeline
- incorporating an external method described in a paper or spec
- wiring a new dependency or subsystem into a codebase with minimal disruption
- merging a useful pattern from a prototype into a production-oriented project

## Start by framing the integration task

Before proposing changes, identify as concretely as possible:

- the target project
- the thing to integrate
- the intended use case inside the target
- the available references, if any
- the constraints on complexity, dependencies, style, performance, and invasiveness

Separate the task into the right mode:

- understanding the target project
- understanding the candidate integration
- comparing reference implementations
- planning the integration
- implementing the chosen path

Do not jump into implementation before clarifying which of these is actually needed.

## Inspect the target project first

Understand the target codebase before treating any external reference as a template.

Find the relevant:

- modules
- entrypoints
- data flow
- control flow
- extension points
- existing abstractions
- configuration surfaces
- testing surfaces

Prefer adapting to the target project’s structure over importing foreign structure.

- Do not overengineer for hypothetical future generality unless the current task truly requires it.
