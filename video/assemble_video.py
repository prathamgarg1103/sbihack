# Assembles the submission MP4 from the app captures + TTS narration.
# Scene mapping follows video/FINAL_VIDEO_SCRIPT.md. Narration is tempo-adjusted
# 1.07x so the full cut lands under the 3:00 submission cap (scratch TTS ran 3:11).
#
# Run:  backend\.venv\Scripts\python video\assemble_video.py   (ffmpeg must be on PATH)
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"E:\sbi hack")
CAP = ROOT / "video" / "captures"
NARR = ROOT / "video" / "narration"
SLIDES = Path(
    r"C:\Users\prath\AppData\Local\Temp\claude\E--sbi-hack"
    r"\1263b62a-e9b2-43ff-a32c-d733ec897512\scratchpad\slides"
)
WORK = ROOT / "video" / "build"
WORK.mkdir(exist_ok=True)
OUT = ROOT / "video" / "Diya-Demo.mp4"

TEMPO = 1.10
FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")
if not FFMPEG:
    sys.exit("ffmpeg not on PATH")

# scene -> (narration wav, [images in display order], optional fixed first-image seconds)
SCENES = [
    ("scene01.wav", [SLIDES / "slide1.png", CAP / "f01_hero.png"], 5.0),
    ("scene02.wav", [CAP / "f02a_consent_hi.png", CAP / "f02b_nudge_hi.png", CAP / "f02d_comparison.png", CAP / "f02e_donothing.png"], None),
    ("scene03.wav", [CAP / "f03a_missold_flag.png", CAP / "f03c_exit_vs_stay.png"], None),
    ("scene04.wav", [CAP / "f02c_why_da.png", CAP / "e10_decision_log.png"], None),
    ("scene05.wav", [CAP / "f05a_flowa_nudge_en.png", CAP / "f05b_flowa_nudge_hi.png"], None),
    ("scene06.wav", [CAP / "f06_guardian.png"], None),
    ("scene07.wav", [CAP / "f08_compliance.png"], None),
    ("scene08.wav", [CAP / "f07_mission_control.png"], None),
    ("scene09.wav", [CAP / "f09a_open_shelf.png", CAP / "f09b_flowd_walkthrough.png", SLIDES / "slide14.png"], None),
]

VF = "format=yuv420p"

# The concat demuxer needs every frame to be the same size — normalize all
# images to padded 1920x1080 up front (mixed sizes silently truncate segments).
from PIL import Image  # noqa: E402

NORM = WORK / "norm"
NORM.mkdir(exist_ok=True)
BG = (11, 31, 58)  # yono ink


def normalize(img: Path) -> Path:
    out = NORM / f"{img.stem}.png"
    if not out.exists():
        im = Image.open(img).convert("RGB")
        im.thumbnail((1920, 1080), Image.LANCZOS)
        canvas = Image.new("RGB", (1920, 1080), BG)
        canvas.paste(im, ((1920 - im.width) // 2, (1080 - im.height) // 2))
        canvas.save(out)
    return out


def dur(path: Path) -> float:
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


segments = []
total = 0.0
for i, (wav, images, first_fix) in enumerate(SCENES, 1):
    for img in images:
        if not img.exists():
            sys.exit(f"missing image: {img}")
    images = [normalize(img) for img in images]
    a_dur = dur(NARR / wav) / TEMPO
    tail = 0.7 if i == len(SCENES) else 0.25  # let the end card breathe
    t_total = a_dur + tail

    # split scene time across its images (optionally pinning the first)
    if first_fix and len(images) > 1:
        rest = (t_total - first_fix) / (len(images) - 1)
        durs = [first_fix] + [rest] * (len(images) - 1)
    else:
        durs = [t_total / len(images)] * len(images)

    lst = WORK / f"scene{i:02d}.txt"
    lines = []
    for img, d in zip(images, durs):
        lines.append(f"file '{img.as_posix()}'")
        lines.append(f"duration {d:.3f}")
    lines.append(f"file '{images[-1].as_posix()}'")  # concat demuxer needs a final entry
    lst.write_text("\n".join(lines), encoding="utf-8")

    seg = WORK / f"seg{i:02d}.mp4"
    subprocess.run(
        [
            FFMPEG, "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", str(lst),
            "-i", str(NARR / wav),
            "-filter_complex", f"[0:v]{VF},fps=30[v];[1:a]atempo={TEMPO},apad[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", f"{t_total:.3f}",
            str(seg),
        ],
        check=True,
    )
    segments.append(seg)
    total += t_total
    print(f"seg{i:02d}: {t_total:.1f}s  ({', '.join(p.name for p in images)})")

concat_list = WORK / "all.txt"
concat_list.write_text(
    "\n".join(f"file '{s.as_posix()}'" for s in segments), encoding="utf-8"
)
subprocess.run(
    [
        FFMPEG, "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", "-movflags", "+faststart",
        str(OUT),
    ],
    check=True,
)
final = dur(OUT)
m, s = divmod(final, 60)
print(f"\n{OUT.name}: {int(m)}:{s:04.1f} ({final:.1f}s, planned {total:.1f}s)")
if final > 180:
    print("WARNING: over the 3:00 submission cap!")
else:
    print("under the 3:00 cap — OK")
