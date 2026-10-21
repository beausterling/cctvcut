---
name: genhq-sound
description: Optional post-video GenHQ sound-design prompt skill. Analyze the newly generated cinematic video, map its actual shots and visible events, and produce one detailed standalone sound prompt. Default handoff is the prompt plus a silent copy of that same video to Seedance 2.0 at 480p; after the user generates the sound carrier, extract its audio onto the original cinematic picture.
---

# GenHQ Sound — optional post-video prompt

## Scope and defaults

This skill runs **optionally after the cinematic video exists**. Its default deliverable is **a detailed sound-design prompt**, not an API call, a paid job or a freshly generated soundtrack. The user can use the prompt with any tool they choose.

The recommended handoff defaults to **Seedance 2.0 at 480p**, with audio generation enabled, using **the prompt and the silent version of the newly generated cinematic video**. These defaults apply to this sound pass, not to the first cinematic generation. User-selected tools/settings override them.

The entire workflow is:

1. The source-to-cinematic skill produces a cinematic video.
2. This optional skill analyzes that finished cinematic video and returns a detailed sound prompt.
3. The user submits that prompt and a silent copy of the same video to Seedance 2.0 at 480p, or uses another tool.
4. When the result is available and the user requests assembly, extract its audio and put it onto the **original cinematic video**, not onto the low-resolution carrier picture.

Do not add model tournaments, automatic purchases, library sourcing, multiple mandatory sound-generation stages or other research workflows to this default path.

## 1. Inspect the generated picture

Use the exact cinematic edit that will receive sound. Do not analyze the original CCTV/phone/archival reference, reuse its event timings, or rely on the planned storyboard once the generated video exists.

- Probe duration, frame rate, frame count, dimensions, start times and audio streams with ffprobe.
- Run `scripts/analyze.py` (FFmpeg/ffprobe and NumPy required), then view contact sheets and native frames around important contacts.
- Treat numerical motion peaks and cut detections as candidates, not proof of an impact or a sound source.
- Preserve the original cinematic video. If it already has audio, establish whether the user wants it preserved or replaced. Create a separate silent upload copy when needed; never overwrite the original.
- If the footage cannot be viewed or the required input is missing, say so; do not invent shot content or timing.

## 2. Map what should be audible

For each shot/event record its actual start/end time, visible action or contact, material and surface, camera distance/movement, intended sound, onset/end and foreground/background priority. Inspect native contact frames when necessary and state uncertainty.

Describe physical behavior, not just mood. A small caster rolling over a loose sheet calls for material-specific wheel/paper texture, not an automatic loud bag-crumple, tear or trailer impact. Smoke alone does not establish an explosion, gunshot or chemical identity.

Use the vocabulary in `references/sfx-types.md` and `references/palettes-and-laws.md` where useful. Their trailer/genre conventions and the preserved original are reference material, **not instructions to force booms, reverses, music or a whoosh on each cut**.

Unless the user asks otherwise, inherit the cinematic skill's diegetic-only intent: appropriate environmental air/crowd, footsteps, wheels, cloth, prop handling and visible events. No score, narration, intelligible dialogue, lyrics or artificial transitions. Quiet remains appropriately quiet; do not inflate every tiny sound into a hero effect.

## 3. Return one detailed standalone prompt

Write the prompt in English, in a single copyable code block. Use only reference tags the user can map to the actual input; `@video1` means the silent cinematic video to be attached. Do not claim it has already been uploaded when it has not.

Use these sections, with enough physical detail and timing for the actual film:

1. **SCENE CONTEXT:** what the finished film shows, measured duration and that this is a sound pass.
2. **ACTIVE REFERENCE / SOURCE AUDIO:** identify the cinematic reference; specify silent input and the intended final audio treatment.
3. **PICTURE AND TIME CONTRACT:** original runtime, speed and cuts; request unchanged picture and timing, while recognizing the carrier picture will not be used in the final film.
4. **SOUND-TO-PICTURE RULE:** visible contact, material texture, acoustic distance and restrained relative levels. Camera cuts are not collisions.
5. **TIMESTAMPED SHOT / EVENT MAP:** actual generated-film times; for each event say what happens, what sound follows it and how prominent it is. Do not reuse the source recording's clock.
6. **AMBIENCE / FOLEY / VISIBLE EFFECTS:** only the layers that serve this scene, with continuity across same-location shots and justified changes in acoustic perspective.
7. **MIX:** environmental depth, foreground detail, relative quiet and sensible peak headroom. Numerical targets are requests, not verified results; do not normalize every small effect to full-mix loudness.
8. **OUTPUT / LOCKS:** default Seedance 2.0, 480p, audio enabled, the reference's measured runtime and intended aspect ratio; no unrequested recuts, speed changes, speech, music or invented impacts.

Adapt to the selected provider's current prompt/input limits. Do not silently truncate a detailed brief, split the film, change model, request a costlier resolution or retime action. If the film or prompt is too long for that frontend, report the limitation and let the user decide. Instructions in a prompt do not prove a generator will preserve timing or obey audio exclusions.

Alongside the prompt provide only:
- a compact measured event/shot table;
- material/timing uncertainties;
- the default handoff: **prompt + silent cinematic video → Seedance 2.0 / 480p / audio on**;
- the return step: **extract the generated audio onto the original cinematic video**.

Do not submit a generation, select a billing account, upload private footage or spend credits unless separately requested. No API credential is required to use this prompt skill.

## 4. Assemble only when the generated carrier returns

The 480p carrier is an audio source, not a replacement visual master. On an assembly request:

1. Probe the original cinematic video and returned carrier. Confirm an audio stream, matching timeline, and whether sound is missing or offset.
2. Extract and preserve the carrier's original audio. Copy the original cinematic video packets into the final file and attach the new audio, replacing the old track unless told otherwise.
3. Preserve original picture resolution, aspect ratio, frame rate, frame count and timing. Verify the copied video hash.
4. Do not silently stretch, pad, loop or shift audio to hide a duration/timing mismatch. Report it and obtain direction. A prompt's picture lock does not certify audible contact sync.
5. Verify output audio presence, duration, peaks and a full decode. Do not claim listening-quality approval based only on loudness or waveform statistics.

A local assembly helper is included; it performs no uploads or model calls:

```sh
python3 scripts/attach_audio.py \
  --original cinematic-original.mp4 \
  --carrier seedance-sound-carrier.mp4 \
  --output cinematic-with-sound.mp4
```

It retains an extracted audio archive and a technical manifest. FFmpeg and ffprobe are required. Audio that is materially short or starts late is rejected instead of silently repaired.

## Provenance

This working skill adapts the supplied GenHQ sound workflow to an optional, prompt-first post-video step. The supplied original is preserved in `references/genhq-original.md`; upstream authorship/licensing was not established, so no new blanket license is asserted over that material. The working instructions above take precedence over conflicting reference-template conventions. Original synced skills and the separate model-agnostic sound workflow are not modified by this repository copy.
