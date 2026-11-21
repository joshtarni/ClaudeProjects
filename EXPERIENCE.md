# Screen Recorder Project Log

## Current state

- Windows desktop screen-area recorder implemented in `screen_recorder.py` with
  Tkinter/ttk and a dark-themed control window.
- Capture region is a transparent, always-on-top rectangle: drag to move and
  use the lower-right handle to resize.
- Records video at 20 FPS, H.264 (`libx264`, CRF 28), plus system playback audio
  from the default Windows output device, encoded as AAC at 128 kbps.
- Video is captured with `mss`; FFmpeg is supplied by `imageio-ffmpeg`.
- While recording, temporary MP4 and WAV files are created beside the script.
  Stopping finalizes and combines them; the user then chooses a destination
  and filename. Canceling deletes the temporary recording.
- Microphone input is not captured.

## Dependencies and run command

Dependencies are in `requirements.txt`: `imageio-ffmpeg`, `mss`, `numpy`, and
`soundcard`. Install and run from the project directory:

```powershell
py -m pip install -r requirements.txt
py screen_recorder.py
```

## Implementation notes

- The FFmpeg video process reads raw RGB frames from stdin; `screen_recorder.py`
  separately records loopback audio to a temporary WAV, then muxes audio and
  video into the temporary MP4.
- Worker-thread updates are sent to the Tkinter event loop via a queue.
- Errors opening the default output or finalizing/muxing the audio are reported
  to the user rather than silently producing a video without sound.
- Keep the control window outside the capture rectangle to avoid recording it.

## Verification to date

- Python syntax compilation passed after changes.
- A simulated audio source successfully produced a WAV and the FFmpeg mux
  smoke test confirmed an audio stream in the resulting MP4.
- Save and cancel flows were checked: choosing a path moves the temporary
  video; canceling removes it.
- Live capture from an actual Windows playback device was not verified in the
  development environment.

## Follow-up considerations

- Test loopback capture on the target Windows machine and confirm the expected
  playback device is selected when multiple output devices are present.
- If adding microphone support, offer an explicit source selector and keep
  system audio and microphone capture independently optional.
