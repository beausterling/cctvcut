---
name: genhq-sound
description: >
  GENHQ professional sound design for Seedance. Use whenever the user uploads a video and wants
  sound design, sound effects, a sound bed, audio, SFX, foley, ambience, or a "sound pass" added
  to it — or asks for a Seedance prompt that adds sound to existing footage. Trigger on phrases
  like "add sound design to this video", "make a sound design prompt", "add SFX to my clip",
  "design the audio for this", "sound bed for this footage", "برومت ساوند ديزاين", "ضيف أصوات
  للفيديو". Analyse the footage first, then output a single standalone Seedance prompt.
---

# GENHQ Sound Design

Turn any uploaded video into a production-grade Seedance sound-design prompt.

**Output: always a single standalone prompt in a code block, in English.**

---

## CORE PRINCIPLE — WRITE THE AUDIBLE

The model reacts to **describable physical behaviour**, not mood words. Translate every abstraction into something a sound editor could actually build.

- ❌ "epic cinematic sound" → ✅ `a deep boom dropping to 30Hz with a long reverberant tail, preceded by 0.2s of silence`
- ❌ "add a whoosh" → ✅ `an airy whoosh with real doppler, rising and falling with the camera arc, short tail`
- ❌ "nice UI sounds" → ✅ `a felt-padded click over a warm rounded low tone with a fast air tail, no crack`

Every audio event must be anchored to something visible on a stated frame. Sound with no visible cause is the fastest way to make a piece feel fake.

---

## WORKFLOW

### Step 1 — Analyse the footage. Always. Before writing anything.

```bash
python3 scripts/analyze.py /path/to/video.mp4
```

Returns: duration, resolution, fps, whether an audio track already exists, hard cuts, major motion beats, soft beats, quiet windows, and a brightness/saturation profile.

Then **look at the footage** — extract a contact sheet and view it:

```bash
mkdir -p /tmp/gh && ffmpeg -v error -i VIDEO -vf "fps=1,scale=340:-1" /tmp/gh/f_%02d.png
```

View the frames. Identify per shot: location (interior/exterior), subject, what materials are visible, what moves, what the camera does, what the hero moment is.

**If the frames cannot be read, say so plainly and ask the user what is in the shot.** Never invent a shot list — sound design built on a guessed picture is worthless. Report the measured timing map (which is reliable) and ask for the content.

### Step 2 — Build the beat map

Convert the analysis into a shot list with timecodes. For every beat, decide:
- what is visibly happening
- which sound type serves it (see `reference/sfx-types.md`)
- how much weight it gets relative to the other beats

**The heaviest hit belongs to the heaviest visual event.** Everything else sits under it. Find that moment first, then build around it.

### Step 3 — Pick one palette

From `reference/palettes-and-laws.md`: Cinematic/Trailer · Sci-Fi · Horror · UI/Tech/Product · Motion Graphics · Sports · Luxury/Premium.

Mixing palettes is what makes a sound bed feel confused. If the user asks for "epic" on footage that is quiet and premium, say so and recommend the palette that actually fits the picture.

### Step 4 — Write the prompt

Use the structure below. Then run the checklist.

---

## ASSET TAGGING

The uploaded video is referenced by load order: `@video1`, `@video2`, … Images: `@image1`, `@image2`, … Audio: `@audio1`, … If the user gives explicit tags, use theirs.

Every reference gets a minimal anchor plus `100% matches the reference`. Do not describe the footage at length — long description conflicts with the reference and degrades it.

Never place a tag in a prompt where that asset is not present.

---

## CONTEXT ISOLATION

Each generation is a blank slate. A prompt is a sealed, single-document unit. Do not carry in scene numbers, prior-shot summaries, unused tags, or "as above / continues" phrasing.

---

## PROMPT STRUCTURE

A sound pass uses a reduced block set — visual blocks are dropped because the picture is fixed. Use only the blocks the piece needs.

```
SCENE CONTEXT
[1–2 sentences: what the footage is, its length, its tone, and that this is a sound-only pass.]

ACTIVE REFERENCES
[@video1 + minimal anchor + "100% matches the reference". State whether the source
 already carries audio and what happens to it.]

FORMAT MODE
[One continuous pass over @video1, real time, no re-cutting, no re-framing, no speed change.
 State that the existing cuts stay exactly where they are.]

SOUND-TO-PICTURE RULE
[The binding law: every layer is motivated by something visible. Cuts get transition elements,
 camera moves get whooshes shaped to them, on-screen contacts get foley on that frame,
 visible materials get their true texture, distance in frame maps to distance in the mix.]

SHOT-BY-SHOT MAP
[Every beat on the clock. One line per shot or per event:
   SHOT n — 0.00 to 1.85 — [what is on screen]
   [what the sound does, on which frame, with what weight]
 This is the core of the prompt. Be specific and measurable.]

LAYERS TO BUILD
[Numbered layers, each with its own character:
 1. AMBIENCE BED   2. MOVEMENT DESIGN   3. TRANSITION ELEMENTS
 4. FOLEY          5. TENSION / TEXTURE  6. ACCENTS   7. MUSIC (optional, restrained)]

MIX AND MASTER
[Ambience low and wide, foley intimate and centred, movement on the sides, hits carrying
 weight without boom. Full dynamic range with real quiet. Around -14 LUFS integrated,
 true peak under -1 dBTP, stereo, frame-accurate.]

STYLE
[The overall sonic character in words — no equipment names, no artist names.]

OUTPUT SETTINGS
[Resolution, aspect, exact runtime, fps, real-time speed, bitrate.]

POSITIVE LOCKS
[Short hard fixers in positive form. Picture unchanged, runtime exact, cuts unmoved,
 each event on its stated frame, one element per cut, no sound without a visible cause.]
```

---

## THE SIX LAYERS

Every professional sound bed is built from six layers. No more, no fewer.

| # | Layer | Job | Level |
|---|---|---|---|
| 1 | Ambience / Backgrounds | establishes place and time | low, wide, continuous |
| 2 | Foley | ties bodies to picture | close, dry, centred |
| 3 | Hard Effects / Spot FX | the specific visible events | mid, locked to frame |
| 4 | Design Elements | sound with no visible source — tension, unreality | as needed |
| 5 | Transitions | joins shots | fills the sides |
| 6 | Music / Score | emotion | under everything, never on top |

**Test:** remove a layer. If nothing changes, it was padding. If the scene collapses, it was structure.

---

## REFERENCE FILES

Read these before writing — they carry the detail this file summarises.

- `reference/sfx-types.md` — every sound type, what it does, and the exact English phrasing for the prompt
- `reference/palettes-and-laws.md` — genre palettes, timing laws, mix and master, common mistakes

---

## TIMING LAWS (the short list)

1. Whooshes start 3–5 frames **before** the move.
2. Hits land on the **exact** frame.
3. A reverse precedes every important hit by 0.3–0.8s.
4. Put **0.15–0.25s of silence** before the biggest hit.
5. Ambience switches on the **location-cut frame**.
6. **One** transition element per cut.
7. A repeated element dies — one or two booms per film, never more.
8. Distance in frame = distance in the mix.
9. No sound for movement that is not on screen.

---

## PROMPTING RULES

- **English prompts only.**
- **Positive phrasing only.** State the target, never the prohibition — except in a dedicated negative/locks section.
- **Measurable values.** Frequencies in Hz, times in seconds and frames, loudness in LUFS/dBTP. Not "fast", not "loud", not "deep".
- **No equipment names, no plugin names, no artist or film references.** Describe the sound, not the gear.
- **No copyrighted or recognisable music.** If music is included it must be original, minimal and restrained — a sparse warm pad or soft pulse sitting under the design.
- **No voiceover, no dialogue, no lyrics** unless the user explicitly asks.
- **Crowd beds stay texture** — no chanting, no audible individual words.

---

## HANDLING THE SOURCE AUDIO

Check whether the uploaded file already has an audio track. Three cases:

1. **No audio track** → build everything from scratch. State it in SCENE CONTEXT.
2. **Has audio, user wants it kept** → lock it: `keep the original audio track from @video1 exactly as it is, unchanged and in sync`.
3. **Has audio, user wants it replaced** → state that the original is discarded and the new bed is built from scratch.

Ask if it is unclear. This changes the whole prompt.

---

## WHAT TO TELL THE USER ALONGSIDE THE PROMPT

Keep it short. After the prompt, give them:
- the measured shot/beat table so they can verify it against their own footage
- any place where the analysis was uncertain
- one concrete suggestion for improving the result

Never pad the reply with process narration.

---

## CHECKLIST

- Footage analysed with the script **and** viewed before writing?
- If the frames could not be read, was that stated plainly instead of guessed?
- Source audio status established (none / keep / replace)?
- One palette chosen, not mixed?
- The heaviest hit assigned to the heaviest visual event?
- Every audio event tied to a visible cause on a stated frame?
- Silence placed before the biggest hit?
- Whooshes only where the camera actually moves?
- Ambience switching on location-cut frames?
- One transition element per cut, nothing stacked?
- Booms limited to one or two?
- Room tone present — no absolute digital silence?
- Runtime, resolution and fps stated exactly as measured?
- Loudness target stated (-14 LUFS, -1 dBTP)?
- Everything positive, measurable, in English, free of gear and artist names?
- Locks restate the critical facts once: picture unchanged, runtime exact, cuts unmoved?
