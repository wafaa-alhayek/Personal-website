# wafaalhayek.com

Personal site: digital collage and drawing, writing, data analysis. One page,
no build step, no framework. Deployed as static files to Cloudflare Pages.

---

## Files

```
index.html     the entire site — markup, CSS, and the canvas generators
dither.py      pipeline: masters -> duotone plates + optimised web exports
img/           generated output (not yet created)
```

## Run it

Open `index.html` in a browser. There is no build step and no dependencies.
Keep it that way unless there's a strong reason not to.

---

## Design system

Three values, fixed:

| token      | value     | role                                    |
|------------|-----------|-----------------------------------------|
| `--ground` | `#15121C` | page background, near-black             |
| `--paper`  | `#E6E2D6` | inverted content panels, plate grounds  |
| `--accent` | `#D6177A` | the only chromatic colour on the page   |

The swatch row in the header is a **development control** for trying other
accents. Remove it before launch.

Type: **Bodoni Moda** for display, **IBM Plex Mono** for everything else.
Small text is uppercase with wide letter-spacing throughout.

### The screen

Every piece of generated art on the page — hero, side plate, footer band, the
three charts — goes through one function, `screen()` / `plateFull()`:

1. a `tone(u, v, aspect)` function returns greyscale 0–1 for any point
2. it's evaluated at up to **4× display resolution**
3. thresholded against an 8×8 ordered Bayer matrix into exactly two colours
4. drawn down to display size with `imageSmoothingEnabled = true`

Step 4 is the important one. The dither cells end up smaller than a screen
pixel, so the browser averages them and the moiré reads as fine continuous
texture. Rendering 1:1 produces coarse pixel noise instead — this was tried and
looked wrong.

Tone functions use **hard edges**, not smooth gradients. `hatch()` draws ruled
lines at a 30% duty cycle; `rings()` draws concentric lines over a solid fill.
Hard edges are what beat against the dither grid to produce the ringing.
Sine-based tone fields were tried and read as mush.

`dither.py` uses the same Bayer matrix, so generated art and processed
photographs belong to the same visual system.

---

## Decisions already made — don't undo without asking

**The works are untitled, permanently.** They're addressed by the capture
number iOS assigned (`IMG_1055`) and ordered by it. This is a stated position,
not an oversight. Precedents: Gonzalez-Torres, On Kawara. The About section
says so explicitly.

**Index shows two-colour plates; full colour only on open.** The collages are
polychrome and the colour is load-bearing, so duotoning all of them would
destroy the work. Duotone is the site's voice; colour is the reveal.

**Static, not Framer.** Framer was considered and rejected — the canvas
generators would have become code components, meaning code maintenance inside
someone else's editor, plus a paid plan for the custom domain.

**Source material is public domain.** Mostly the British Library's Flickr
Commons release (the Mechanical Curator collection, 1M+ images from digitised
17th–19th century books). No attribution required; the About section offers it
anyway. Earlier work used Pinterest saves — those are not on the site.

---

## Outstanding

- [ ] **Run the image pipeline.** 46 masters, ~600 MB total, largest 38 MB.
      Nothing is web-ready yet.
      ```
      python3 dither.py ./masters ./img --ink "#D6177A" --paper "#15121C"
      ```
      Then wire `img/duo/` into the ledger rows and `img/web/` into the plate
      overlay, replacing the placeholder text.
- [ ] **Alt text per work.** Description, not title — describing what's visible
      doesn't violate the untitled position. Required for screen readers.
- [ ] **Real content.** Everything in Data and Writing is placeholder, written
      to demonstrate what the sections hold. The metadata project (reading
      working rhythm out of capture timestamps) is a genuinely good idea worth
      actually doing.
- [ ] Replace `hello@example.com` and the `#` links.
- [ ] Remove the accent swatch row.
- [ ] Favicon and social preview image.

---

## Deploy — Cloudflare Pages

The domain is already registered at Cloudflare, so DNS is handled internally
and no records need copying anywhere.

Manual:
1. Dashboard → Workers & Pages → Create → Pages → Upload assets
2. Drag the folder containing `index.html` and `img/`
3. Custom domains tab → add the domain → Cloudflare wires it up

Or with wrangler:
```
npm install -g wrangler
wrangler login
wrangler pages deploy . --project-name wafaalhayek
```

Connecting a GitHub repo makes every push deploy automatically. Worth doing.

---

## Notes

- `image-rendering: pixelated` must stay off. The smoothing is the effect.
- Drift only re-renders the rows the hero disc occupies; a full 4× re-render
  per frame is too expensive. The motion toggle re-renders at full quality.
- `prefers-reduced-motion` disables drift.
- Ring pitch (`pitch` in `composeHero`) is the main dial for how fine the
  interference reads. Higher is finer.
