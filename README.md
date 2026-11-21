# Screen Area Recorder

A small Python desktop recorder for Windows. Move the transparent outlined box
over the part of the screen you want to capture, resize it with the lower-right
handle, and use **Start recording**. While recording, a temporary MP4 is stored
in the same folder as the script. After you click **Stop** and the video is
finalized, choose where to save it and what to name it. Canceling the save
dialog deletes the temporary video. The recorder captures audio from the
default Windows audio output and includes it in the MP4. H.264 video and AAC
audio compression keep file sizes modest.

## Run

Install Python 3.9 or later, then from this folder run:

```powershell
py -m pip install -r requirements.txt
py screen_recorder.py
```

Use **Pause** and **Resume** to omit pauses from the recording. The capture area
is fixed while recording and cannot be moved; the outline returns after the
recording is finalized. Use **Set up hotkeys…** to assign global shortcuts for
Start, Pause/Resume, and Stop. By default these are `Ctrl+Shift+F8`,
`Ctrl+Shift+F9`, and `Ctrl+Shift+F10`; settings are saved in the current
Windows user's application data folder.

For implementation notes and development history, see [EXPERIENCE.md](EXPERIENCE.md).
