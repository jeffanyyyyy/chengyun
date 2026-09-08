# Budarina — portfolio hero

A single-screen dark hero page for a designer's portfolio. No framework, no build
step: `index.html` contains the markup, CSS and JS.

## Layout

- Full-viewport black canvas that never scrolls (`100dvh`, `overflow: hidden`).
- Top bar: wordmark left, `Home / Work / About / Contact` centre, `See My Work`
  and `Say Hello` right.
- Diamond tag line, then the headline — the last line set in big italic serif.
- Bottom left: the subtitle paragraph and the white `View My Work →` pill.
- Right: the showreel panel, mirrored horizontally, looping.
- A floating camera window: drag it by its title bar, resize it from the corner.

## Showreel

The reel plays `assets/reel.mp4`. Drop your own file in at that path; nothing
else needs changing.

The panel takes its shape from the file. A portrait reel fills the tall column
down the right-hand side; a landscape one becomes a wide card centred on the
right, so a 16:9 video is not cropped down to its middle third. That is read
from `videoWidth`/`videoHeight` once the metadata loads, so it follows whatever
you put there. Below 861px wide the reel becomes a dimmed full-screen backdrop
instead, and the copy sits over it.

Until that file exists the page renders a generated monochrome reel on a canvas
instead, so nothing looks broken on a fresh checkout. The generated reel honours
the same play/pause control as a real video.

## Hand control

The camera window runs [MediaPipe Hand Landmarker][mp] on the webcam feed and
draws the 21-point skeleton over it:

- **open hand** → the reel plays
- **closed fist** → the reel pauses

A finger counts as extended when its tip sits further from the wrist than its
middle joint. Three or more extended reads as open, one or fewer as a fist, and
anything between holds the current state. A gesture has to hold for four frames
before it takes effect, so a blurred frame can't flip the reel.

The library and the model are vendored under `vendor/`, so the page fetches
nothing from a third party at runtime — it works offline, and it can't break
because a CDN moved a URL. That costs about 17 MB in the repository:

```
vendor/mediapipe/vision_bundle.mjs            136 KB   MediaPipe tasks-vision 0.10.14 (npm)
vendor/mediapipe/wasm/vision_wasm_internal.*  9.2 MB   the SIMD wasm runtime
vendor/models/hand_landmarker.task            7.5 MB   the hand landmark model
```

None of it is downloaded until the camera window actually starts, so a visitor
who never enables the camera pays nothing for it.

If you would rather keep the repository small, delete `vendor/` — `SOURCES` in
`index.html` already falls back to the jsDelivr CDN when the local copies are
missing. Either way, if neither can be reached the webcam still shows and the
reel keeps playing; only the gesture control drops out.

Only the SIMD build of the wasm runtime is vendored. Browsers without wasm SIMD
(Safari before 16.4) fall through to the CDN, then to the graceful message.

[mp]: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker

## Running it

`getUserMedia` needs a secure context, so opening the file over `file://` will
not get you a camera. Serve it instead:

```bash
cd budarina && python3 serve.py
```

Then open http://localhost:8080/ and allow camera access.

Use `serve.py` rather than `python3 -m http.server`. The stock module answers
every Range request with the whole file and a plain 200, and Safari treats that
as a broken source and refuses to play the reel at all — the page falls back to
the generated canvas and looks like the video is missing. `serve.py` is the same
static server with the 206 responses video playback needs, and it threads, since
a video element opens several connections at once.
