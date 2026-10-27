# projects/ — new video work

Every new video gets its own directory here, created by the agent on its first
turn, before any script is written. Nobody types a path by hand.

    projects/<slug>/
      README.md       what this video is, its state, how it builds
      brief.md        the confirmed brief
      STATE.md        current step, run mode, next action
      continuity.md   style and subject blocks, invariants, anchor prompts
      script.md       the narration
      visuals.csv     one row per image moment
      frames/         one frame per moment
      refs/           reference images, if any
      build/          the handoff script and what it produces
      README          <- plus a line in ../PROJECTS.md, same turn

`examples/` is the old layout and holds finished and abandoned projects. New
work does not go there.
