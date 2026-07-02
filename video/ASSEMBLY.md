# Diya — Final MP4 Assembly Instructions

> Follow this after all shots from `video/SHOT_LIST.md` are captured into `video/footage/`.
> Scene timings + narration: `video/FINAL_VIDEO_SCRIPT.md`. Scratch narration WAVs:
> `video/narration/scene01.wav … scene09.wav`.

## Status of this machine (checked 2026-07-02)

**ffmpeg is NOT installed** (`ffmpeg -version` → command not found).

Two paths — pick one:

- **Path A (recommended): install ffmpeg** — precise, scriptable, repeatable.
  ```powershell
  winget install ffmpeg
  ```
  (Resolves to Gyan.FFmpeg. Close and reopen the terminal afterwards so PATH refreshes;
  verify with `ffmpeg -version`.)
- **Path B: Clipchamp** — built into Windows 11, zero install, fully GUI. See bottom.

---

## Scene duration table (both paths need this)

| Scene | File stem | Start | Duration (s) |
|---|---|---|---|
| 1 | scene01 | 0:00 | 24 |
| 2 | scene02 | 0:24 | 28 |
| 3 | scene03 | 0:52 | 20 |
| 4 | scene04 | 1:12 | 23 |
| 5 | scene05 | 1:35 | 22 |
| 6 | scene06 | 1:57 | 18 |
| 7 | scene07 | 2:15 | 15 |
| 8 | scene08 | 2:30 | 22 |
| 9 | scene09 | 2:52 | 8  |

Total: 180 s.

---

## Path A — ffmpeg workflow

Run everything from `E:\sbi hack\video`. Uses a working dir `build\`.

### A1. Trim + normalize each scene's video to its exact duration

For every scene, pick the in-point (`-ss`, seconds into the raw clip where the scene should
start — remember the 3–5 s handles) and force exact duration, 1080p, 60 fps, no audio:

```powershell
mkdir build
# Repeat per scene — adjust -ss per clip, -t from the table above:
ffmpeg -ss 3 -i footage\shot01_problem.mp4 -t 24 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -an build\v01.mp4
```

Scenes built from multiple shots (Scene 2 = shots 02+03; Scene 4 = shots 05+06; Scene 9 =
shots 11a/11b/11c + end card) are concatenated first, then trimmed to the scene duration.
End-card still → video:

```powershell
ffmpeg -loop 1 -i footage\shot12_endcard.png -t 4 -vf "scale=1920:1080,fps=60" -c:v libx264 -crf 18 -pix_fmt yuv420p -an build\endcard.mp4
```

Mini-concat example (Scene 2):

```powershell
# build\s2list.txt  (forward slashes or escaped backslashes; paths relative to the txt file)
# file 'v02a.mp4'
# file 'v02b.mp4'
ffmpeg -f concat -safe 0 -i build\s2list.txt -c copy build\v02.mp4
```

### A2. Concatenate the 9 scene videos

Create `build\clips.txt`:

```
file 'v01.mp4'
file 'v02.mp4'
file 'v03.mp4'
file 'v04.mp4'
file 'v05.mp4'
file 'v06.mp4'
file 'v07.mp4'
file 'v08.mp4'
file 'v09.mp4'
```

```powershell
ffmpeg -f concat -safe 0 -i build\clips.txt -c copy build\video_only.mp4
```

(`-c copy` works because A1 encoded everything identically.)

### A3. Build the narration track (pad each WAV to its scene's duration, then concat)

Each narration WAV is shorter than its scene — pad with trailing silence to the exact scene
duration so scene N+1's narration starts exactly at its boundary:

```powershell
ffmpeg -i narration\scene01.wav -af "apad=whole_dur=24" -ar 48000 -ac 2 build\a01.wav
ffmpeg -i narration\scene02.wav -af "apad=whole_dur=28" -ar 48000 -ac 2 build\a02.wav
ffmpeg -i narration\scene03.wav -af "apad=whole_dur=20" -ar 48000 -ac 2 build\a03.wav
ffmpeg -i narration\scene04.wav -af "apad=whole_dur=23" -ar 48000 -ac 2 build\a04.wav
ffmpeg -i narration\scene05.wav -af "apad=whole_dur=22" -ar 48000 -ac 2 build\a05.wav
ffmpeg -i narration\scene06.wav -af "apad=whole_dur=18" -ar 48000 -ac 2 build\a06.wav
ffmpeg -i narration\scene07.wav -af "apad=whole_dur=15" -ar 48000 -ac 2 build\a07.wav
ffmpeg -i narration\scene08.wav -af "apad=whole_dur=22" -ar 48000 -ac 2 build\a08.wav
ffmpeg -i narration\scene09.wav -af "apad=whole_dur=8"  -ar 48000 -ac 2 build\a09.wav
```

> **Scratch-TTS caveat (measured 2026-07-02):** the machine-generated WAVs run longer than
> their slots because the TTS voice pauses heavily at punctuation:
>
> | WAV | Measured | Slot | Fits? |
> |---|---|---|---|
> | scene01.wav | 26.1 s | 24 s | no |
> | scene02.wav | 28.0 s | 28 s | exact |
> | scene03.wav | 21.1 s | 20 s | no |
> | scene04.wav | 20.3 s | 23 s | yes |
> | scene05.wav | 22.4 s | 22 s | ~ |
> | scene06.wav | 20.9 s | 18 s | no |
> | scene07.wav | 18.3 s | 15 s | no |
> | scene08.wav | 24.2 s | 22 s | no |
> | scene09.wav | 10.1 s | 8 s | no |
>
> If you keep the scratch TTS (instead of re-recording at ~150 wpm, which fits exactly),
> time-fit each long WAV BEFORE the apad step with pitch-preserving tempo adjustment —
> tempo = measured ÷ slot:
>
> ```powershell
> ffmpeg -i narration\scene01.wav -af "atempo=1.09" build\fit01.wav   # 26.1/24
> ffmpeg -i narration\scene03.wav -af "atempo=1.06" build\fit03.wav   # 21.1/20
> ffmpeg -i narration\scene05.wav -af "atempo=1.02" build\fit05.wav   # 22.4/22
> ffmpeg -i narration\scene06.wav -af "atempo=1.16" build\fit06.wav   # 20.9/18
> ffmpeg -i narration\scene07.wav -af "atempo=1.22" build\fit07.wav   # 18.3/15
> ffmpeg -i narration\scene08.wav -af "atempo=1.10" build\fit08.wav   # 24.2/22
> ffmpeg -i narration\scene09.wav -af "atempo=1.27" build\fit09.wav   # 10.1/8
> ```
>
> then feed the `fitNN.wav` files into the apad commands above. Scenes 2 and 4 need no fit.
> (In Clipchamp there is no tempo tool — either re-record, or accept slightly longer scene
> holds and trim Scene 8's tail to keep total ≤ 3:00.)
>
> Generic check for any replacement WAV:
> `ffprobe -v error -show_entries format=duration -of csv=p=0 <file>` — if longer than its
> slot, tighten the read or lengthen that scene's hold and rebalance a neighbour; keep total
> at 180 s.

Create `build\audio.txt` (`file 'a01.wav'` … `file 'a09.wav'`), then:

```powershell
ffmpeg -f concat -safe 0 -i build\audio.txt -c pcm_s16le build\narration_full.wav
```

### A4. (Optional) mix quiet background music

```powershell
ffmpeg -i build\narration_full.wav -i assets\music.mp3 -filter_complex "[1:a]volume=0.08,atrim=0:180[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[out]" -map "[out]" -c pcm_s16le build\mix.wav
```

(Skip if you have no cleared/royalty-free track. Narration-only is fine for judges.)

### A5. Mux to the final MP4 (H.264 + AAC, 1080p)

```powershell
ffmpeg -i build\video_only.mp4 -i build\narration_full.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest DIYA_SUBMISSION.mp4
```

### A6. Verify

```powershell
ffprobe -v error -show_entries format=duration -of csv=p=0 DIYA_SUBMISSION.mp4   # expect ~180.0
```

Watch it once end-to-end: audio/video sync at each scene boundary, no dead frames, ≤ 3:00.

---

## Path B — Clipchamp fallback (no install)

1. Open **Clipchamp** (Start menu → Clipchamp, built into Windows 11) → **Create a new video**.
2. **Import media:** drag in all `video/footage/*.mp4`, the end-card PNG, and all
   `video/narration/*.wav`.
3. **Video track:** place the shots in scene order (see the coverage map at the bottom of
   `SHOT_LIST.md`). Trim each with the split tool so its length matches the duration table
   above — Clipchamp shows a timecode ruler; snap scene starts to 0:00, 0:24, 0:52, 1:12,
   1:35, 1:57, 2:15, 2:30, 2:52.
4. **Audio track:** drag `scene01.wav` to start at 0:00, `scene02.wav` at 0:24, `scene03.wav`
   at 0:52, and so on per the table. Do NOT stretch the WAVs; trailing silence per scene is
   intentional.
5. **Detach/limit clip audio:** mute every video clip (speaker icon on the clip) EXCEPT
   Shot 7 where the app's own TTS voice should stay faintly audible (set its volume ~30%).
6. **Text overlays:** add the captions from each scene's "Text overlays" list in
   `FINAL_VIDEO_SCRIPT.md` using a clean sans-serif lower-third preset; keep each on screen
   3–5 s.
7. **Export:** Export → **1080p** (60 fps if offered for your source). Clipchamp exports MP4
   (H.264/AAC) by default. Rename to `DIYA_SUBMISSION.mp4`.
8. Verify: total length ≤ 3:00, audio aligned at every scene boundary.

---

## Re-recording narration (optional but recommended)

The WAVs in `video/narration/` are machine-scratch (Microsoft Zira). For the submission, a human
read is warmer — record per scene reading the narration blocks verbatim from
`FINAL_VIDEO_SCRIPT.md` (phone voice memo in a quiet room is fine), export/convert to WAV or MP3
with the SAME filenames, and both paths above work unchanged.
