# PROJECTS — read this before touching anything

This repo is shared by many conversations. Most of what is in it is finished or
abandoned. Only one project is current at a time.

**New work goes in `projects/`.** The agent creates the directory itself on its
first turn (see Step 0.5 of the pipeline prompt) and adds a row to the table
below in the same turn. `examples/` is the older layout: finished and abandoned
work, kept for reference, nothing added to it.

| Directory | Project | State | Frames | Rule |
|---|---|---|---|---|
| `examples/day_zero_video/` | **Day One** — Ep 1, *Your Room* (zombie-apocalypse series) | **BUILT**, awaiting end-to-end build verification | 104 | **CURRENT. Work here.** |
| `examples/day_one_video/` | Day One, earlier draft | superseded by `day_zero_video` | 122 | do not touch |
| `examples/day_one_v2/` | Day One, abandoned draft | abandoned | 10 | do not touch |
| `examples/day_one_v3/` | Day One, abandoned draft | abandoned | 17 | do not touch |
| `examples/crowd_crush_video/` | Crowd crush | abandoned | 78 | do not touch |
| `examples/night_one_video/` | Night One | abandoned | 72 | do not touch |
| `examples/nine_floors_video/` | Nine Floors | abandoned after style tests | 8 | do not touch |
| `examples/last_bus_video/` | Last Bus | script only, never built | 0 | do not touch |
| `examples/twenty_four_hour_video/` | Twenty Four Hours | script only, never built | 0 | do not touch |

## The rules for a fresh conversation

1. **One current project.** Work only in the directory marked CURRENT, or in a
   new directory under `projects/` that you create yourself for the new video.
   Nothing in `examples/` is a place to continue.
2. **Finished work is not a template.** Previous projects are reference for
   mechanics only — how a frame is named, how files are laid out, how a build
   script is written. Never for taste, never for style, never for continuity.
3. **A previous style block is not a default.** If a new brief does not state a
   look, ask. Do not inherit one from the folder next door.
4. **Continuity does not cross projects.** Episodes within one series inherit
   their series continuity forward. Unrelated videos inherit nothing but the
   machinery.
5. **Root scripts may be another project's assumptions.** `kaggle_day_zero.sh`
   and `run_video_kaggle.sh` were written for Day One. Read them before running
   them; do not reuse them blind. New project scripts belong inside the
   project's own directory.
6. **New work gets a new directory under `projects/`**, named and created by
   the agent, never by asking me. Never add frames to an existing folder, never
   overwrite a directory, and increment the version if the slug is taken.
7. **Every project directory carries its own README**: what it is, its state,
   its brief. A conversation starting cold must be able to open the folder and
   know what it is looking at without reading any chat log.

## What is not a project

- `VIDEO_PIPELINE_PROMPT.md` — the pipeline prompt. Obey it; do not edit it
  casually.
- `VIDEO_PIPELINE_AUDIT.md` — why the prompt says what it says. Reference only.
- `cartoonstyle/`, `tools/` — shared machinery. Changing it changes every
  project; do it deliberately.
- `WORKFLOW.md` — an earlier description of the process. The prompt outranks it
  wherever they disagree.
