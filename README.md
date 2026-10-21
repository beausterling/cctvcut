# CCTVCUT

A skill for turning a short source clip into a timestamped cinematic multi-camera prompt, then reviewing the generated interpretation against the source.

This is a prompt/workflow skill, not a video generator or a promise of frame-perfect synchronization. The supplied template targets Seedance 2.5. Its evidence gathering, motion tracking, continuity planning and review methods can inform other video workflows, but provider-specific prompts and limits must be adapted and checked.

## What's included

- [`SKILL.md`](SKILL.md) — the working skill, with one added instruction to read the execution notes.
- [`references/CCTVCUT.original.md`](references/CCTVCUT.original.md) — the supplied original, preserved unchanged.
- [`references/LOCAL_EXECUTION.md`](references/LOCAL_EXECUTION.md) — execution and accuracy qualifications, kept separate from the original template.

No source footage, generated media, private account data, credentials or paid-generation configuration is included.

## Workflow

1. Inspect the actual video and identify its source type honestly. Handheld footage is not fixed CCTV.
2. Separate visible evidence, measurements, external reporting and uncertainty.
3. Build the beat timeline, cast, geography, entry routes and motion/continuity map.
4. Write the timestamped cinematic camera sequence and a concise operational prompt.
5. Obtain any required approval before uploads, paid generation or publication.
6. Compare generated actions and cuts against the source. Report drift rather than claiming synchronization from the prompt alone.
7. Assemble an AI-labelled comparison without stretching either source's aspect ratio.

Sound can be handled separately using the finished cinematic edit as the sound clock. Preserve the approved picture and choose an appropriate video-to-audio or editing backend for each run; this repository does not bundle or require a sound-generation service.

## Use with an assistant

```sh
git clone https://github.com/beausterling/cctvcut.git
```

Give your assistant `SKILL.md` and the `references/` directory, along with a source video. For a file-based skill loader, copy those files together into a `cctvcut` skill directory. Keep the relative directory structure intact.

Common per-user skill locations include `~/.claude/skills/cctvcut/`, `~/.codex/skills/cctvcut/` and `~/.hermes/skills/cctvcut/`; use the location supported by your installed assistant. The analysis examples require tools such as FFmpeg/ffprobe or Python with OpenCV. Access to a video-generation provider is separate.

Installing this skill does not authorize spending, uploading private footage, or publishing. Provider limits, content rules, model availability and prices must be checked before each run.

## Customizations in this copy

The working `SKILL.md` differs from the preserved original only by an instruction to read `references/LOCAL_EXECUTION.md`. Those notes add:

- Honest source identification and separation of evidence from creative interpretation.
- Real measurements and generation review rather than assumed exact synchronization.
- Provider-specific prompt, duration and reference-limit checks; no silent retiming or truncation.
- Aspect-ratio-safe split-screen assembly and respect for silent-output requests.
- No invented identities, outcomes, smoke chemistry or supposedly recovered sound.
- Respect for provider safeguards and explicit approval boundaries.

Some notes record a particular provider's documented behavior as an execution example. They are not permanent model guarantees; recheck current first-party documentation.

## Provenance and rights

The original template was supplied by the repository owner; its upstream author and redistribution license were not established. It is retained as a separate reference so the source and local additions can be distinguished. No new MIT, Apache or other broad license is asserted over the supplied material. A public copy alone does not grant rights beyond those held by the relevant rights holders.

Use only footage and other assets you have permission to process and share. Label generated interpretations clearly, and do not present generated picture or sound as authenticated documentation of an event.
