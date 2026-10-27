# =============================================================================
#  ONE-CELL KAGGLE BUILD  —  "Why Did Humans Start Cooking?"
#  Paste this ENTIRE file into a single Kaggle notebook cell and Run.
#
#  IMPORTANT: In the Kaggle notebook, set  Settings -> Internet = ON.
#  This cell clones a public GitHub repo, installs edge-tts, and calls the
#  Microsoft neural-TTS endpoint. All three need internet. Everything else
#  (word-locked cuts, Ken Burns, sound cues, loudness normalisation, encode,
#  packaging) is deterministic and local to the Kaggle machine.
#
#  This cell is the ONLY thing that produces audio and video. The workspace
#  repo holds frames + metadata only; it never runs TTS or ffmpeg itself.
#
#  Stages print their name on entry and "OK" on exit. If a stage fails, the
#  last lines printed name the exact stage that failed.
# =============================================================================

# ----- STAGE: BOOTSTRAP ------------------------------------------------------
import os, sys, re, csv, json, glob, wave, shutil, zipfile, subprocess, threading, asyncio
from contextlib import contextmanager

def _run(cmd, check=True):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if check and r.returncode != 0:
        raise RuntimeError("command failed (%d): %s\n%s" %
                           (r.returncode, " ".join(map(str, cmd))[:300], (r.stdout or "")[-2000:]))
    return r.stdout or ""

@contextmanager
def STAGE(name):
    print("\n" + "=" * 72, flush=True)
    print(">>> STAGE:", name, flush=True)
    print("=" * 72, flush=True)
    try:
        yield
        print("<<< OK:", name, flush=True)
    except Exception as e:
        print("!!! FAILED AT STAGE: %s  ->  %s: %s" % (name, type(e).__name__, e), flush=True)
        raise

# Config (kept here so the cell is fully self-bootstrapping).
REPO_URL = "https://github.com/AsuraXP/newrepo.git"
BRANCH   = "arena/065c2e4b-newrepo"
SLUG     = "why-humans-started-cooking"
ZIP_NAME = SLUG + "_DELIVERABLE.zip"
FPS      = 30
LUFS_I, LUFS_TP, LUFS_LRA = -16, -1.5, 11
CUE_GAIN = 0.12

WORK  = "/kaggle/working" if os.path.isdir("/kaggle/working") else os.getcwd()
BUILD = os.path.join(WORK, "build_" + SLUG)
REPO  = os.path.join(BUILD, "newrepo")
CLIPS = os.path.join(BUILD, "clips")
PKG   = os.path.join(BUILD, "package")
for d in (BUILD, CLIPS, PKG):
    os.makedirs(d, exist_ok=True)
ZIP = os.path.join(WORK, ZIP_NAME)

with STAGE("BOOTSTRAP (deps + ffmpeg)"):
    _run([sys.executable, "-m", "pip", "install", "-q", "edge-tts", "numpy", "pillow"])
    FFMPEG = shutil.which("ffmpeg")
    if not FFMPEG:
        _run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"])
        import imageio_ffmpeg
        FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    import numpy as np
    from PIL import Image
    print("ffmpeg:", FFMPEG)
    print("work dir:", WORK)

def ff(args):
    """Run ffmpeg; args is a list AFTER the binary."""
    return _run([FFMPEG, "-y", "-loglevel", "error"] + args)

# ----- STAGE: CLONE / UPDATE REPO -------------------------------------------
with STAGE("CLONE / UPDATE REPO @ " + BRANCH):
    if not os.path.isdir(os.path.join(REPO, ".git")):
        _run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO_URL, REPO])
    else:
        _run(["git", "-C", REPO, "fetch", "--depth", "1", "origin", BRANCH])
        _run(["git", "-C", REPO, "reset", "--hard", "FETCH_HEAD"])
    COMMIT = _run(["git", "-C", REPO, "rev-parse", "HEAD"]).strip()
    print("COMMIT HASH:", COMMIT)

    P = lambda *p: os.path.join(REPO, *p)
    script_path   = P("script.md")
    sources_path  = P("SOURCES.md")
    youtube_path  = P("youtube.txt")
    meta_path     = P("metadata.json")
    visuals_path  = P("visuals.csv")
    thumb_land    = P("thumbs", "thumbnail.jpg")
    thumb_port    = P("thumbs", "thumb_portrait.png")
    frames_dir    = P("frames")

# ----- STAGE: PREFLIGHT ------------------------------------------------------
with STAGE("PREFLIGHT (frames + metadata)"):
    meta = json.load(open(meta_path, encoding="utf-8"))
    rows = list(csv.DictReader(open(visuals_path, encoding="utf-8")))
    assert len(rows) == meta["frame_count"] == 117, "row/frame count mismatch"

    expected = ["beat%02dm%02d.png" % (int(r["slide_id"]), int(r["moment"])) for r in rows]
    missing = [f for f in expected if not os.path.isfile(os.path.join(frames_dir, f))]
    assert not missing, "missing frames: %s" % missing[:8]

    sizes = {}
    for f in expected:
        with Image.open(os.path.join(frames_dir, f)) as im:
            sizes[im.size] = sizes.get(im.size, 0) + 1
    assert sizes == {(1920, 1080): 117}, "unexpected frame sizes: %s" % sizes

    NARR_TEXT = open(script_path, encoding="utf-8").read().strip()
    joined = " ".join(" ".join(r["moment_text"].split()) for r in rows)
    assert " ".join(NARR_TEXT.split()) == joined, "moment_text does not reproduce script.md"

    WORDS = [len(r["moment_text"].split()) for r in rows]
    M = sum(WORDS)
    for f in (sources_path, youtube_path, script_path, meta_path, visuals_path):
        assert os.path.getsize(f) > 0, "empty: " + f
    for t, want in ((thumb_land, (1280, 720)), (thumb_port, (1080, 1920))):
        with Image.open(t) as im:
            assert im.size == want, "thumbnail size %s != %s" % (im.size, want)
    print("frames:", len(expected), "all 1920x1080 | words:", M,
          "| moments:", len(rows), "| chapters:", len(meta["chapters"]))

# ----- STAGE: NARRATION (single continuous TTS take) -------------------------
MP3 = os.path.join(BUILD, "narration.mp3")
WAV = os.path.join(BUILD, "narration.wav")

def _run_async(coro_fn):
    box = {}
    def _t():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            box["v"] = loop.run_until_complete(coro_fn())
        except Exception as e:
            box["err"] = e
        finally:
            loop.close()
    th = threading.Thread(target=_t); th.start(); th.join()
    if "err" in box:
        raise box["err"]
    return box.get("v")

with STAGE("NARRATION (edge-tts, one continuous take)"):
    import edge_tts
    req = meta["voice"]["requested"]
    RATE = meta["voice"]["rate"]
    candidates = [req] + list(meta["voice"]["fallbacks"]) + \
                 ["en-US-ChristopherNeural", "en-US-EricNeural", "en-US-JennyNeural"]

    async def _synth(voice):
        # Newer edge-tts exposes a `boundary` kwarg; older builds do not.
        # Try word-boundary mode first (needed for word-locked cuts), then a
        # plain take, then retry once for transient stream errors.
        for attempt_kw in (dict(rate=RATE, boundary="WordBoundary"),
                           dict(rate=RATE), dict(rate=RATE)):
            try:
                comm = edge_tts.Communicate(NARR_TEXT, voice, **attempt_kw)
            except TypeError:
                comm = edge_tts.Communicate(NARR_TEXT, voice, rate=RATE)
            offs = []
            try:
                with open(MP3, "wb") as f:
                    async for ch in comm.stream():
                        t = ch.get("type")
                        if t == "audio":
                            f.write(ch.get("data", b""))
                        elif t in ("WordBoundary", "SentenceBoundary") and ch.get("offset") is not None:
                            # edge-tts offset is in 100-nanosecond ticks.
                            offs.append(ch["offset"] / 1e7)  # -> seconds
                return offs
            except Exception:
                continue  # retry (falls back to proportional timing if all fail)
        raise RuntimeError("edge-tts stream failed for voice " + voice)

    word_offsets, VOICE_USED = [], None
    for v in candidates:
        try:
            word_offsets = _run_async(lambda v=v: _synth(v))
            VOICE_USED = v
            break
        except Exception as e:
            print("  voice %s unavailable: %s" % (v, str(e)[:160]))
    assert VOICE_USED and os.path.getsize(MP3) > 1000, "TTS produced no audio for any voice"
    print("voice used:", VOICE_USED, "| rate:", RATE,
          "| word boundaries captured:", len(word_offsets))

    ff(["-i", MP3, "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", WAV])

# ----- STAGE: WORD-LOCKED TIMINGS (derived from final audio) -----------------
with STAGE("WORD-LOCKED TIMINGS (from measured audio)"):
    def read_wav(path):
        w = wave.open(path, "rb")
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n); w.close()
        assert sw == 2
        d = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
        if ch > 1:
            d = d.reshape(-1, ch).mean(axis=1)
        return sr, d

    SR, NARR = read_wav(WAV)
    D = len(NARR) / SR                          # measured audio duration, seconds
    assert D > 30, "audio too short: %.2fs" % D

    c = np.concatenate([[0], np.cumsum(WORDS)])  # c[i] = words before frame i
    f = c / M                                    # word fraction at each cut

    timing_method = "word_boundary_pacing"
    if len(word_offsets) >= 4 and max(word_offsets) > 0:
        offs = np.array(sorted(word_offsets), dtype=float)
        offs = np.clip(offs, 0, D)
        offs = np.append(offs, D)                # guarantee an end point
        offs = np.maximum.accumulate(offs)       # monotone
        offs[0] = 0.0
        frac_axis = np.linspace(0, 1, len(offs))
        def t_curve(x):
            return float(np.interp(x, frac_axis, offs))
    else:
        timing_method = "proportional_by_word_count"
        def t_curve(x):
            return float(x) * D

    cut = np.array([t_curve(x) for x in f])
    cut[0] = 0.0; cut[-1] = D
    cut = np.maximum.accumulate(cut); cut[0] = 0.0; cut[-1] = D

    # Quantise the word-locked cut times to whole video frames so the rendered
    # clip durations sum to exactly the frame timeline (no rounding drift).
    fb = np.round(cut * FPS).astype(np.int64)
    for i in range(1, len(fb)):
        fb[i] = max(fb[i], fb[i - 1] + 1)       # every clip >= 1 frame
    fb[-1] = max(fb[-1], int(np.ceil(D * FPS)))  # video >= audio length,
    # so -shortest can never truncate the final spoken word.
    NFR = np.diff(fb)                            # 117 integer frame counts
    DUR = NFR / FPS                             # 117 clip durations (seconds)
    assert len(DUR) == 117 and (NFR > 0).all()
    print("audio duration: %.3fs (%d:%02d) | timing: %s" %
          (D, int(D)//60, int(D)%60, timing_method))
    print("cut length  min %.2fs | mean %.2fs | max %.2fs | sum %.3fs" %
          (DUR.min(), DUR.mean(), DUR.max(), DUR.sum()))

    # Chapters come ONLY from the final audio timeline (cumulative word-locked cuts).
    chapter_lines, chapter_meta = [], []
    for ch in meta["chapters"]:
        idx = ch["frame"] - 1
        t = float(cut[idx])
        h, rem = divmod(int(round(t)), 3600)
        mm, ss = divmod(rem, 60)
        ts = ("%d:%02d:%02d" % (h, mm, ss)) if h else ("%d:%02d" % (mm, ss))
        chapter_lines.append("%s %s" % (ts, ch["title"]))
        chapter_meta.append({**ch, "start_seconds": round(t, 3), "time": ts})
    print("chapters (from audio):")
    for l in chapter_lines:
        print("   ", l)

# ----- STAGE: SOUND CUES (placed at beat events) -----------------------------
MIXED_WAV = os.path.join(BUILD, "mixed.wav")
with STAGE("SOUND CUES (beat events, mixed under narration)"):
    def make_cue(sr, seed, dur=0.55):
        n = int(sr * dur)
        rng = np.random.default_rng(1000 + seed)
        noise = rng.standard_normal(n).astype(np.float32)
        k = 48
        sm = np.convolve(noise, np.ones(k, np.float32) / k, mode="same")
        env = np.sin(np.pi * np.linspace(0, 1, n, dtype=np.float32)) ** 2
        x = sm * env
        return x / (np.max(np.abs(x)) + 1e-9) * 0.9

    cues = np.zeros(len(NARR), dtype=np.float32)
    for b, ch in enumerate(meta["chapters"]):
        s0 = int(cut[ch["frame"] - 1] * SR)
        cc = make_cue(SR, b)
        e0 = min(len(cues), s0 + len(cc))
        if s0 < len(cues):
            cues[s0:e0] += cc[:e0 - s0]
    mixed = np.clip(NARR + CUE_GAIN * cues, -1.0, 1.0)
    w = wave.open(MIXED_WAV, "wb")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mixed * 32767).astype("<i2").tobytes()); w.close()
    print("cues placed at %d beat events | mix gain %.2f" % (len(meta["chapters"]), CUE_GAIN))

# ----- STAGE: STITCH MP4 (Ken Burns, word-locked cuts) -----------------------
SILENT = os.path.join(BUILD, "video_silent.mp4")
VIDEO  = os.path.join(BUILD, "VIDEO.mp4")
with STAGE("STITCH MP4 (Ken Burns + word-locked cuts)"):
    KB = bool(meta["ken_burns"]["enabled"])
    ZLONG = meta["ken_burns"]["target_zoom_long"]
    ZSHORT = meta["ken_burns"]["target_zoom_short"]
    STRONG = meta["ken_burns"]["strong_from_words"]

    common_out = ["-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
                  "-bf", "0", "-g", str(FPS), "-keyint_min", str(FPS),
                  "-sc_threshold", "0", "-pix_fmt", "yuv420p",
                  "-video_track_timescale", "30000"]

    def clip_cmd(frame, out, n, wc_i, ken):
        base = [FFMPEG, "-y", "-loglevel", "error", "-i", frame,
                "-frames:v", str(n)]
        if ken:
            # Documented Ken Burns: ONE still input, zoompan d=n emits n output
            # frames; 'zoom' accumulates each frame. Upscale 1.1x first so the
            # 1.0->zmax crop stays sharp and inside the source bounds.
            zmax = ZLONG if wc_i >= STRONG else ZSHORT
            dz = (zmax - 1.0) / max(n, 1)
            vf = ("scale=2112:1188:flags=lanczos,"
                  "zoompan=z='min(zoom+%.8f,%.5f)':"
                  "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                  "d=%d:s=1920x1080:fps=%d,format=yuv420p" % (dz, zmax, n, FPS))
        else:
            # Static: loop the still for exactly n frames.
            vf = "scale=1920:1080,format=yuv420p"
            base = [FFMPEG, "-y", "-loglevel", "error", "-loop", "1",
                    "-framerate", str(FPS), "-i", frame, "-frames:v", str(n)]
        return base + ["-vf", vf] + common_out + [out]

    # Probe Ken Burns on one frame; fall back to static clips if ffmpeg rejects
    # zoompan or emits too few frames (guard against a silently-stuck zoom).
    def count_frames(path):
        probe = shutil.which("ffprobe")
        if not probe:
            return None
        try:
            out = _run([probe, "-v", "error", "-count_frames",
                        "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", path])
            return int(out.strip().splitlines()[0])
        except Exception:
            return None

    if KB:
        n0 = int(NFR[0])
        probe = os.path.join(CLIPS, "_probe.mp4")
        try:
            _run(clip_cmd(os.path.join(frames_dir, expected[0]), probe, n0,
                          WORDS[0], True))
            cnt = count_frames(probe)
            assert os.path.getsize(probe) > 1000
            if cnt is not None:
                assert cnt >= n0 - 1, "zoompan produced %d/%d frames" % (cnt, n0)
            os.remove(probe)
            print("  Ken Burns probe OK (%s frames)" % (cnt if cnt is not None else n0))
        except Exception as e:
            print("  Ken Burns unavailable (%s); using static frames." % str(e)[:160])
            KB = False

    clip_paths = []
    for i, fn in enumerate(expected):
        n = int(NFR[i])
        out = os.path.join(CLIPS, "clip_%04d.mp4" % i)
        _run(clip_cmd(os.path.join(frames_dir, fn), out, n, WORDS[i], KB))
        clip_paths.append(out)
        if (i + 1) % 20 == 0 or i == len(expected) - 1:
            print("  rendered %d/%d clips" % (i + 1, len(expected)))
    print("motion:", "Ken Burns" if KB else "static",
          "| total frames:", int(NFR.sum()), "| total %.3fs" % DUR.sum())

    listfile = os.path.join(BUILD, "clips.txt")
    with open(listfile, "w") as f:
        for p in clip_paths:
            f.write("file '%s'\n" % os.path.abspath(p))
    ff(["-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy",
        "-movflags", "+faststart", SILENT])

    # Mux audio with loudness normalisation (EBU R128) -> final VIDEO.mp4.
    ff(["-i", SILENT, "-i", MIXED_WAV, "-filter_complex",
        "[1:a]loudnorm=I=%s:TP=%s:LRA=%s[a]" % (LUFS_I, LUFS_TP, LUFS_LRA),
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
        "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", VIDEO])
    assert os.path.getsize(VIDEO) > 100000, "VIDEO.mp4 too small"
    print("VIDEO.mp4: %.2f MB | runtime ~%.2fs" %
          (os.path.getsize(VIDEO) / 1e6, D))

# ----- STAGE: FINAL METADATA + youtube.txt (audio-derived chapters) ----------
with STAGE("FINAL METADATA + youtube.txt (audio-derived chapters)"):
    def fmt(s):
        h, rem = divmod(int(round(s)), 3600); mm, ss = divmod(rem, 60)
        return ("%d:%02d:%02d" % (h, mm, ss)) if h else ("%d:%02d" % (mm, ss))

    final_meta = dict(meta)
    final_meta["commit"] = COMMIT
    final_meta["voice_used"] = VOICE_USED
    final_meta["runtime_seconds"] = round(D, 3)
    final_meta["runtime_hms"] = fmt(D)
    final_meta["timing_method"] = timing_method
    final_meta["frame_durations_seconds"] = [round(float(x), 3) for x in DUR]
    final_meta["audio"] = {"codec": "aac", "sample_rate_hz": SR,
                           "loudness_target_lufs": LUFS_I,
                           "sound_cues": meta["sound_cues"]["type"]}
    final_meta["video"] = {"codec": "h264", "resolution": [1920, 1080],
                           "fps": FPS, "motion": "Ken Burns" if KB else "static",
                           "frame_count": 117}
    final_meta["chapters"] = chapter_meta
    with open(os.path.join(PKG, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(final_meta, f, indent=2, ensure_ascii=False)

    base = open(youtube_path, encoding="utf-8").read()
    pre, after = base.split("CHAPTERS\n", 1)
    _mid, post = after.split("SOURCES & FURTHER READING", 1)
    block = "CHAPTERS (derived from final audio, runtime %s)\n%s\n\n" % (fmt(D), "\n".join(chapter_lines))
    with open(os.path.join(PKG, "youtube.txt"), "w", encoding="utf-8") as f:
        f.write(pre + block + "SOURCES & FURTHER READING" + post)

    shutil.copy(VIDEO, os.path.join(PKG, "VIDEO.mp4"))
    shutil.copy(thumb_land, os.path.join(PKG, "thumbnail.jpg"))
    shutil.copy(thumb_port, os.path.join(PKG, "thumb_portrait.png"))
    shutil.copy(script_path, os.path.join(PKG, "script.md"))
    shutil.copy(sources_path, os.path.join(PKG, "SOURCES.md"))
    print("packaged files:", ", ".join(final_meta["zip_contents"]))

# ----- STAGE: PACKAGE ZIP ----------------------------------------------------
with STAGE("PACKAGE ZIP"):
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in final_meta["zip_contents"]:
            src = os.path.join(PKG, name)
            assert os.path.isfile(src), "missing for zip: " + name
            z.write(src, arcname=name)
    print("zip:", ZIP, "| %.2f MB" % (os.path.getsize(ZIP) / 1e6))

# ----- STAGE: VERIFY ---------------------------------------------------------
with STAGE("VERIFY (zip integrity + video decode + contents)"):
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None, "zip CRC failure"
        print("contents of %s:" % ZIP_NAME)
        for info in z.infolist():
            print("   %-24s %12s bytes" % (info.filename, format(info.file_size, ",")))
        names = set(z.namelist())
        for req in ("VIDEO.mp4", "thumbnail.jpg", "thumb_portrait.png",
                    "metadata.json", "youtube.txt", "script.md"):
            assert req in names, "zip missing " + req
    # decode-check the whole video, fail loudly if any frame is broken
    ff(["-i", os.path.join(PKG, "VIDEO.mp4"), "-f", "null", "-"])
    print("video decodes cleanly, start to finish")

# ----- FINAL LINK ------------------------------------------------------------
print("\n" + "#" * 72)
print("# DONE. commit %s | runtime %s | %d frames | voice %s" %
      (COMMIT[:10], final_meta["runtime_hms"], 117, VOICE_USED))
print("#" * 72)

from IPython.display import FileLink, display

# Print the exact required snippet, and show a clickable link as the cell output.
print("FileLink('%s')" % ZIP)
display(FileLink(ZIP))

# Last expression of the cell = the exact deliverable FileLink snippet.
FileLink(ZIP)
