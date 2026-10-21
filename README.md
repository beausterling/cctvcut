# CCTVCUT — source video to cinema

Turn CCTV, iPhone/phone recordings, handheld footage, archival film or another reference video into cinematic multi-camera coverage of the same visible moment.

This repository contains **two separate skills**. Both produce prompts and instructions; neither submits paid generations by default.

| Skill | Input | Output | Default handoff |
|---|---|---|---|
| [Cinematic skill](SKILL.md) | Original source/reference video | Timed cinematic prompt and review/assembly instructions | Seedance **2.5 / 480p**, unless overridden |
| [GenHQ Sound](skills/genhq-sound/SKILL.md), optional | The **newly generated cinematic video** | One detailed standalone sound-design prompt | Prompt + silent cinematic video → Seedance **2.0 / 480p**, audio enabled |

Model/resolution defaults can be overridden. Check the chosen provider's current prompt, reference, mode and duration limits before submitting; a default is not a guarantee that every frontend supports a particular request.

## The entire workflow

### 1. Produce the cinematic video

Give the main skill a reference clip. It inspects the evidence, maps timing/geography/identity and prepares cinematic coverage. Generate the first video using your chosen provider, review it, and keep the original cinematic file as the visual master. Source type is described honestly; moving phone footage is not treated as a static security camera.

An AI-over-source split-screen comparison is optional. Label the AI interpretation and preserve both sources' aspect ratios.

### 2. Optionally run GenHQ Sound on that new video

Load [`skills/genhq-sound/SKILL.md`](skills/genhq-sound/SKILL.md). It analyzes the **actual finished cinematic video**, not the original phone/CCTV clip or the planned storyboard. It measures the shot/event timing, inspects visible contacts/materials and returns **one detailed, copyable English prompt**, a compact event map and uncertainties.

The user can take that prompt to any tool. Prompt creation alone does not upload footage, generate audio, call a paid API or spend credits.

### 3. Default sound pass: Seedance 2.0 at 480p

Keep the original cinematic master. If it has audio, create a separate silent copy for the sound pass:

```sh
ffmpeg -i cinematic-original.mp4 -map 0:v:0 -c:v copy -an cinematic-silent.mp4
```

Submit **the GenHQ sound prompt and that silent cinematic video** to Seedance **2.0**, request **480p**, and turn **audio generation on**. Use the measured cinematic runtime and preserve its timing/cuts in the prompt. The user controls submission and can choose another model or service.

If the selected frontend rejects the length, references or settings, report that limitation instead of silently shortening, splitting or retiming the film or switching to a costlier model. A prompt's timing instructions are targets, not proof of generated synchronization.

### 4. Put the returned audio onto the original cinematic picture

Download the returned sound-pass video. Its 480p image is only an **audio carrier**. Extract its new audio and attach it to the **original cinematic video from step 1**—not to the original reference clip, and not to the low-resolution carrier picture.

A local helper performs that assembly without network or model calls:

```sh
python3 skills/genhq-sound/scripts/attach_audio.py \
  --original cinematic-original.mp4 \
  --carrier seedance-sound-carrier.mp4 \
  --output cinematic-with-sound.mp4
```

It produces:
- `cinematic-with-sound.mp4` — original video packets with the new audio, replacing any prior audio;
- `cinematic-with-sound.audio.mka` — unmodified encoded carrier-audio archive;
- `cinematic-with-sound.manifest.json` — duration, audio and packet-hash checks.

The helper copies rather than re-encodes the picture and verifies its packet hash. Delivery audio is AAC-encoded; no added sounds, mastering, stretching, looping or padding is applied. Existing files are not overwritten. Materially short audio or a start offset stops assembly for review rather than hiding drift. Technical checks do not certify Foley realism; listen to the result.

That is the default path. There is no automatic model tournament, library-search stage or separate multi-stem production pipeline.

## Sound-design intent

By default, sound is diegetic: environmental air/ambience, bodies/props and supported visible events on the finished film's actual timing. Preserve relative quiet and acoustic distance. No unrequested score, narration, intelligible words or artificial transition hits. A camera cut is not an impact, and small material movements do not automatically justify loud crunches. Explicit user intent overrides genre-template conventions.

The main skill's original AUDIO block is preserved. GenHQ Sound expands the post-video prompt-writing step, without claiming generated sound is recovered original evidence or guaranteed frame-perfect Foley.

## Use with an assistant

```sh
git clone https://github.com/beausterling/cctvcut.git
```

Load the main [`SKILL.md`](SKILL.md) and its `references/` alongside the source video. For the optional second step, separately load [`skills/genhq-sound/SKILL.md`](skills/genhq-sound/SKILL.md) with its own `references/` and `scripts/` directory.

For file-based skill loaders, copy the root `SKILL.md` plus root `references/` into a `cctvcut` skill folder, and copy the entire `skills/genhq-sound/` directory into a separate `genhq-sound` skill folder. Use the skill location supported by your assistant. No API key is needed for analysis/prompt preparation or local assembly.

### Local tools

- FFmpeg and ffprobe for video inspection, silent copies and final assembly.
- Python 3.9+ for the assembly helper and tests.
- NumPy for the supplied GenHQ beat analyzer only. Install in an isolated environment if needed:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/genhq-sound/requirements.txt
.venv/bin/python skills/genhq-sound/scripts/analyze.py cinematic-original.mp4
```

The analyzer's cuts/motion peaks are candidates, not semantic proof of contacts. View the frames before writing the sound prompt.

### Offline verification

```sh
python3 -m unittest discover -s tests -v
```

The assembly tests use short synthetic FFmpeg fixtures, never a model or paid API. They check picture preservation, extracted-audio integrity, missing audio, short audio, input validation and overwrite protection. They do not test a generative model's audio quality.

## Provenance and rights

- [`references/CCTVCUT.original.md`](references/CCTVCUT.original.md) preserves the supplied cinematic template unchanged.
- [`references/LOCAL_EXECUTION.md`](references/LOCAL_EXECUTION.md) contains source/evidence, provider-limit and aspect-ratio qualifications for the working cinematic skill.
- [`skills/genhq-sound/references/genhq-original.md`](skills/genhq-sound/references/genhq-original.md) preserves the supplied GenHQ sound template. Its working adaptation is the optional prompt-first skill above.

The supplied templates' upstream authorship and redistribution licenses were not established. No new MIT, Apache or other blanket license is asserted over those materials; a public copy does not grant additional rights beyond those held by the relevant rights holders.

No project footage, generated media, private transcripts, account data, credentials or billing configuration is included. Installing a skill does not authorize spending, private uploads or publication. Use assets you have permission to process/share and label AI interpretations clearly.
