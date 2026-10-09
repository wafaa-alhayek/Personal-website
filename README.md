# Wafa Alhayek

Collage, writing and data. A static site with a GitHub-based CMS.

## Editing content

1. Go to https://app.pagescms.org and sign in with GitHub.
2. Open this repository. You'll see **Works**, **Writing**, **Data projects**,
   **Decoration library** and **Site settings**.
3. To add a work: Works → add an entry → upload the image, fill in what you
   like → Save. About a minute later the web-sized versions are made
   automatically and the archive puzzle includes it.

Every save is a commit to this repo, and Cloudflare Pages republishes the site.

## Running locally

```
python3 -m http.server
```

Then open http://localhost:8000. (Opening `index.html` directly won't work,
because the page loads its content from `content/*.json`.)

## Deploy

Cloudflare Pages → connect this GitHub repo. No build command; output
directory is the repository root.
