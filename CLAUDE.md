# wafaalhayek.com

Personal site: digital collage and drawing, writing, data analysis. One page,
no build step, no framework. Deployed as static files to Cloudflare Pages.
Content is edited through Pages CMS (pagescms.org), which commits JSON to this
repo.

---

## Files

```
index.html               the whole site: markup, CSS, rendering JS
content/*.json           all content (works, writing, data, decorations, site)
.pages.yml               Pages CMS schema for those JSON files
img/uploads/             masters uploaded through the CMS
img/works/               generated: <ref>-1600.webp and <ref>-640.webp
img/deco/                decoration cut-outs (transparent WebP)
scripts/process_images.py  masters -> img/works + width/height into works.json
.github/workflows/images.yml  runs process_images.py on every CMS save
scripts/make_scraps.py   generated the starter torn-paper scraps
dither.py                original duotone pipeline (not used by the site now)
```

## Run it

The page fetches `content/*.json`, so it needs a local server:

```
python3 -m http.server   # then open http://localhost:8000
```

No build step and no dependencies. Keep it that way unless there's a strong
reason not to.

---

## Design system

| token      | value     | role                                    |
|------------|-----------|-----------------------------------------|
| `--ground` | `#15121C` | page background, near-black             |
| `--paper`  | `#E6E2D6` | inverted content panels                 |
| `--accent` | `#D6177A` | the only chromatic colour; overridable from site settings |

Type: **Bodoni Moda** display, **IBM Plex Mono** body, **Caveat** for the
handwritten notes. Small text is uppercase with wide letter-spacing.

Layout follows the first inspiration mockup: dark hero (featured work, mini
gallery, exhibition note), paper archive, then two checkerboard rows
(game | writing, data | about).

### Archive puzzle

Works keep their true proportions and are never cropped. `buildRows()` packs
them into justified rows (each row scaled to fill the width exactly). When the
next work would squash a row below ~74% of the target height, or the final row
is short, a **balance tile** (pink dot, count, handwritten note, scrap from
the decoration library) is slotted in instead. Rows are grouped into pages
(`archive.rowsPerPage`), navigated by the rail on the right / arrows on phone.
Widths and heights come from works.json so layout never waits on images.

### Decorations

Per work, set in the CMS and drawn by `decorate()`: tape label, torn edge
(clip-path), scribble (SVG), texture (grain / halftone overlay). Section
decorations (writing edge, about, exhibition note) are images from
`content/decorations.json`.

### Draw a plate (the game)

Three face-down cards. Each back is the work screened to two colours with the
same 8x8 Bayer matrix as `dither.py`, rendered at 2x and smoothed down (the
original "screen" idea: keep `imageSmoothingEnabled` on). Picking one flips it
to full colour with a line from `site.game.lines`.

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

- [ ] **British Library cut-outs.** Botanical engravings with background
      removed, for the decoration library. Blocked: this environment's network
      denies flickr.com / wikimedia. Engravings on plain paper can be cut out
      locally by mapping luminance to alpha; no API needed.
- [ ] **Remaining works.** 9 of 46 are online. Add the rest through the CMS.
- [ ] IMG_1230 and IMG_1237 were not in the original 46-work list (which has
      IMG_1239). Confirm with Wafa.
- [ ] **Alt text per work.** Description, not title. IMG_1070, IMG_1157 and
      IMG_1175 have it.
- [ ] **Real content.** Writing and Data entries are marked as samples.
- [ ] Contact email and social links (site settings in the CMS).
- [ ] Exhibition "learn more" link to the Pulp Stiction page on
      lovelybutdead.com once it is live.
- [ ] Social preview image is IMG_1175; replace with a purpose-made one.

---

## Deploy — Cloudflare Workers (static assets)

The site is served by the `wafaalhayek-com` Worker, connected to this repo
under Settings → Builds (branch `main`, no build command, deploy command
`npx wrangler deploy`). Every push to `main` deploys. Builds only start on a
push made after the repo is connected.

- `wrangler.jsonc` serves the repo root as static assets; its `name` must
  match the Worker or the build fails.
- `.assetsignore` keeps repo internals and `img/uploads` (masters, can exceed
  the 25 MiB per-file limit) off the site.
- The domain should be attached as a Custom Domain (Settings → Domains &
  Routes), for both `wafaalhayek.com` and `www.wafaalhayek.com`.

---

## Notes

- `image-rendering: pixelated` must stay off. The smoothing is the effect.
- `prefers-reduced-motion` disables the card flip and page animations.
