# Handoff brief: best-practice guidance layer

You are picking up **human-spec** cold. This file tells you what the project is, what state it is in, and what to build next. Nothing here is a decision you have to keep; it is context so you do not have to rediscover it.

## What the project is

human-spec is a read-only viewer for [OpenSpec](https://github.com/Fission-AI/OpenSpec) repositories. OpenSpec is a spec-driven development (SDD) workflow built for coding agents: specs live under `openspec/specs/<capability>/spec.md`, work in flight lives under `openspec/changes/<name>/` (a `proposal.md`, a `tasks.md` checklist, optional `design.md`, and spec deltas under `specs/<capability>/spec.md` that add, modify, remove or rename requirements), and finished work moves to `openspec/changes/archive/YYYY-MM-DD-<name>/` with its deltas merged into the specs.

The viewer is **one HTML file, no build step, no dependencies** (`index.html`, about 1,700 lines: CSS first, then one script). It reads a repository from a local folder (File System Access API, with live refresh) or from GitHub, builds a model, and renders views: Overview, Specs, Changes, Project. It already draws three spatial diagrams: a lifecycle flow (Drafting → Not started → In progress → Complete → Archived → Specs, with active changes placed in their stage), an impact flow (changes on the left, capabilities on the right, one band per delta), and a lineage strip per requirement (the archived changes that shaped it). The README's "The storyline" section walks through all of this with screenshots and is the fastest way to understand what the user sees.

## Repository state

- `main` is clean and equal to `origin/main` at `f9d079b`. Not GitButler managed.
- Files: `index.html`, `README.md`, `LICENSE`, `docs/showcase.png`, `docs/story-*.png`, and this `TASK.md`.
- `docs/.claude/launch.json` is untracked (excluded via `.git/info/exclude`) and starts a Python static server on port 8080 serving the repository root. Earlier sessions ran with `docs/` as the working directory; that is why it lives there.
- The public repository `Fission-AI/OpenSpec` loads fine through the GitHub source and is the standing test fixture. Load it by typing `Fission-AI/OpenSpec` into the welcome page and clicking "Load repository".

## The next task

**Enhance the app so it guides and teaches the user the best practices of spec-driven development with OpenSpec.** Today the app only shows state. The goal is for it to also say, in context, what good practice looks like and where the loaded repository departs from it.

The source material is a collection of best practices gathered from the OpenSpec community plus the official OpenSpec guidelines. **That document is not in the repository yet.** Your first step is to get it: ask the user whether they have it ready, and if not, gather it from the official OpenSpec repository (its README, docs folder and the agent instruction templates it ships) and from community write-ups, then agree the collected list with the user before building against it. Keep the collected practices as a file in the repository so later agents can revise them without reading the code.

The scope beyond that is open. Points worth settling with the user early, since they shape the work differently:

- **Where the guidance lives.** Options range from a dedicated "Guide" view that teaches the workflow stage by stage, to inline hints attached to the existing views, to a rule set that evaluates the loaded repository and reports findings. These are not exclusive, and a reasonable first slice is one of them done well.
- **Teaching versus checking.** Teaching content is static prose and diagrams that explain the practice. Checking is a predicate over the model that flags where a repository departs from it. The app already has the second kind in embryo (see below), so extending it is cheap; the first kind is new.
- **Whether guidance should be dismissable or persistent**, and whether a "teaching mode" toggle is wanted so experienced users can hide it.

## Where guidance hooks into the existing code

These are the natural seams. All functions are in `index.html`; section markers in the script read `// ---------- name ----------`.

- **`healthCheck(m)`** (section `model`) already produces a needs-attention list of `{ lvl: 'warn' | 'info', text, href }` issues: changes without proposals, tasks without deltas, deltas that modify requirements the spec no longer has, requirements without scenarios, complete-but-unarchived changes, duplicate requirement names, requirements touched by several active changes. A best-practice rule set is a direct extension of this: add a source or rationale to each issue, group by practice, and link to the explanation. The Overview renders the list.
- **`renderWelcome()`** embeds the lifecycle explainer diagram before any repository is loaded. It is the obvious home for a stage-by-stage introduction.
- **`renderChanges()`** has tabs (proposal, tasks, deltas, design, files). Per-stage advice ("a proposal should state why before what", "tasks should map to deltas") fits beside the content it concerns.
- **`renderProject()`** already parses `project.md`, `config.yaml` and `AGENTS.md` from the openspec root. Practices about project context and agent instructions can check these.
- **The lifecycle diagram** (`layoutLifecycle` / `svgLifecycle`, section `diagrams`) takes an optional `explainer` flag. Stage-level guidance could annotate its nodes.
- **`buildModel(files)`** is the single place the model is assembled; anything a rule needs that is not yet computed goes there, not in a renderer.

## Conventions you must keep

- Renderers return HTML strings; escape every value with `esc()`; build internal links with `link(view, id, tab)`. State is one `state` object; expanded sections persist through `state.open` (a Set of keys). Delegated event handlers live in `wireCommon`.
- Colour is reserved for state and comes from CSS custom properties with light and dark themes. Do not introduce a new colour for guidance; use the existing tone scale and weight.
- `window.OSV` exposes the parsers, `buildModel`, `md` and the three layout functions for programmatic use and tests. Export anything new that a test would want.
- No new files in the application itself: it stays one HTML file. Data files (the collected practices) are fine as a separate Markdown or JSON file in the repository, but think about how the single-file app reads them when opened from `file://` (fetch is blocked there), so embedding at build-less time may mean keeping the content inside `index.html` and the source file as documentation.
- From `AGENTS.md`: no em dashes in new text; no invented labels or acronyms; delegate larger implementation to subagents and keep the plan-and-review role yourself; commit incrementally with messages that say why; end commit messages with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`; confirm with the user before pushing.

## How to verify

- Syntax: extract the script and run `node --check` on it. Logic: Node `vm` with stubbed `document`, `localStorage` and `location` works for the parsers, model and layouts without a browser.
- Visual: start the preview server from `docs/.claude/launch.json`, load `Fission-AI/OpenSpec`, check light and dark (the browser pane follows the system theme; set the colour scheme explicitly when comparing).
- Screenshots for the README were produced with headless Google Chrome driven over the DevTools Protocol from Node (global `WebSocket`), emulating `prefers-color-scheme: light`, capturing at 2x and downscaling with `sips`. The scripts lived in a session scratchpad and are gone; the approach is a few dozen lines to recreate if you change what the README shows.

## Known debt, not requested

Mentioned to the user in an earlier review and left alone on purpose. Touch only if the task leads you there: localStorage access is scattered rather than behind one helper; file filters and name normalisers are duplicated between the local and GitHub sources; `state.files` is written but never read; there is no `.gitignore`; the README's needs-attention bullet lists fewer checks than `healthCheck` performs; the GitHub subfolder path and the lost-folder-access path were verified only in Node, not in a browser.
