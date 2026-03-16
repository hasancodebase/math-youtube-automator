"""
================================================
  MATHSOLVER — STAGE 5: VIDEO ASSEMBLY
  Combines Manim animations + Voice audio
  into one complete 1080p MP4 video
================================================
"""

import subprocess
import os
from pathlib import Path
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip
)


# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
OUTPUT_DIR   = Path("D:/math-channel/output")
MANIM_DIR    = OUTPUT_DIR / "animations"
AUDIO_DIR    = OUTPUT_DIR / "audio"
FINAL_DIR    = OUTPUT_DIR / "final_videos"
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def render_all_scenes(problem: str, safe_name: str):
    """
    Renders all Manim scenes for a given problem.
    Saves scene videos to output/animations folder.
    """
    print("\n[Stage 2] Rendering Manim scenes...")

    scenes = [
        "TitleScene",
        "ProblemScene",
        "StepScene",
        "SummaryScene",
    ]

    scene_files = []

    for scene in scenes:
        print(f"  Rendering {scene}...")
        out_file = MANIM_DIR / f"{safe_name}_{scene}.mp4"

        cmd = [
            "manim",
            "-ql",
            "--output_file", str(out_file),
            "D:/math-channel/test_manim.py",
            scene
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Find rendered file
            found = list(Path("media/videos").rglob(f"*{scene}*.mp4"))
            if found:
                scene_files.append(str(found[-1]))
                print(f"  ✓ {scene} done!")
            else:
                print(f"  ✗ {scene} file not found")
        else:
            print(f"  ✗ {scene} failed: {result.stderr[:100]}")

    return scene_files


def assemble_video(scene_files: list, audio_file: str, output_name: str):
    """
    Combines all scene MP4 files + voice audio
    into one final complete video.
    """
    print("\n[Stage 5] Assembling final video...")

    if not scene_files:
        print("  ✗ No scene files found!")
        return None

    # Load and concatenate all scene clips
    print(f"  Loading {len(scene_files)} scene clips...")
    clips = []
    for f in scene_files:
        if Path(f).exists():
            clip = VideoFileClip(f)
            clips.append(clip)
            print(f"  ✓ Loaded: {Path(f).name} ({clip.duration:.1f}s)")
        else:
            print(f"  ✗ Missing: {f}")

    if not clips:
        print("  ✗ No valid clips found!")
        return None

    # Concatenate all scenes
    print("  Concatenating scenes...")
    final_video = concatenate_videoclips(clips, method="compose")
    total_duration = final_video.duration
    print(f"  Total video duration: {total_duration:.1f} seconds")

    # Add voice audio if available
    if audio_file and Path(audio_file).exists():
        print(f"  Adding voice audio: {Path(audio_file).name}")
        voice = AudioFileClip(audio_file)

        # Trim or loop audio to match video length
        if voice.duration > total_duration:
            voice = voice.subclip(0, total_duration)
        
        final_video = final_video.set_audio(voice)
        print("  ✓ Audio added!")
    else:
        print("  ! No audio file found — video will be silent")

    # Save final video
    out_path = FINAL_DIR / f"{output_name}.mp4"
    print(f"\n  Saving final video to: {out_path}")
    print("  This takes 2-5 minutes...")

    final_video.write_videofile(
        str(out_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        logger=None
    )

    # Close clips to free memory
    for clip in clips:
        clip.close()
    final_video.close()

    print(f"\n  ✓ Final video saved!")
    print(f"  Path: {out_path}")
    print(f"  Size: {out_path.stat().st_size / (1024*1024):.1f} MB")

    return str(out_path)


def assemble_from_folder(safe_name: str, audio_file: str = None):
    """
    Finds all rendered scene files for a problem
    and assembles them into a final video.
    """
    print(f"\n{'='*50}")
    print(f"  Assembling video for: {safe_name}")
    print(f"{'='*50}")

    # Search for scene files in media folder
    media_path = Path("media/videos")
    scene_files = []

    scene_order = [
        "TitleScene",
        "ProblemScene", 
        "StepScene",
        "SummaryScene",
    ]

    for scene in scene_order:
        found = list(media_path.rglob(f"*{scene}*.mp4"))
        if found:
            # Get most recent file
            latest = max(found, key=lambda x: x.stat().st_mtime)
            scene_files.append(str(latest))
            print(f"  Found: {latest.name}")
        else:
            print(f"  Missing: {scene}")

    if not scene_files:
        print("\n  No scene files found!")
        print("  Run each scene first:")
        print("  manim -ql test_manim.py TitleScene")
        print("  manim -ql test_manim.py ProblemScene")
        print("  manim -ql test_manim.py StepScene")
        print("  manim -ql test_manim.py SummaryScene")
        return None

    print(f"\n  Found {len(scene_files)} scenes")

    # Find audio file if not provided
    if not audio_file:
        audio_files = list(AUDIO_DIR.glob("*.mp3"))
        if audio_files:
            audio_file = str(audio_files[-1])
            print(f"  Audio: {Path(audio_file).name}")

    return assemble_video(scene_files, audio_file, safe_name)


# ─────────────────────────────────────────────
#  RUN DIRECTLY
# ─────────────────────────────────────────────
if __name__ == "__main__":

    print("=" * 50)
    print("  MATHSOLVER — VIDEO ASSEMBLER")
    print("=" * 50)

    # Assemble the test video
    result = assemble_from_folder(
        safe_name  = "Solve_2x_5_13",
        audio_file = None  # Auto-finds MP3 from output/audio folder
    )

    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"Final video: {result}")
        print(f"\nOpen this file to watch your complete math video!")

        # Open the output folder
        os.startfile(str(FINAL_DIR))
    else:
        print("\n✗ Assembly failed — check errors above")