# The Well-Being Atlas

A Next.js 16 gallery for standalone HTML data-journalism articles stored in a
public [Tigris](https://www.tigrisdata.com/) bucket. The bucket is the single
source of truth — new articles appear in the gallery without a redeploy.

## How it works

- **Discovery** — the server lists the bucket with the S3 API
  (`ListObjectsV2`, paginated), filters to `*.html`, and derives stable slugs
  from object keys. Anonymous bucket listing is disabled, so listing uses
  read credentials; the article files themselves are public.
- **Enrichment** — each article's HTML is fetched and parsed with cheerio
  (`<title>`, meta description, `.dek` paragraph, word count → reading time),
  merged with the curated `gallery.json` manifest at the bucket root when an
  entry matches. Newer revisions of the same article (same title) are
  deduplicated, keeping the most recent upload. One malformed file never
  breaks the gallery — it falls back to a filename-derived title.
- **Caching** — both data functions are wrapped in `'use cache'` with
  `cacheLife('hours')` and `cacheTag('articles')`. New uploads appear within
  ~1 hour, or immediately via the revalidation endpoint:

  ```bash
  curl -X POST "https://<site>/api/revalidate?secret=$REVALIDATE_SECRET"
  ```

- **Article view** — `/articles/[slug]` renders the original file untouched in
  a sandboxed iframe served straight from the bucket, under a slim chrome bar
  with sharing controls. Known slugs are prerendered
  (`generateStaticParams`); new ones render on demand.
- **Sharing** — per-article Open Graph metadata plus a generated 1200×630 OG
  card (`next/og`). The card features the article's *sparkmark*: a
  deterministic miniature chart glyph seeded by the slug and shaped by the
  article's visualization type.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Tigris read credentials for bucket listing (server-side only) |
| `AWS_ENDPOINT_URL_S3` | `https://t3.storage.dev` |
| `AWS_REGION` | `auto` |
| `ARTICLE_BUCKET` | Bucket name (default `happy`) |
| `NEXT_PUBLIC_ARTICLE_BUCKET_URL` | Public bucket URL (default `https://happy.t3.tigrisfiles.io`) |
| `REVALIDATE_SECRET` | Secret for `POST /api/revalidate` |
| `NEXT_PUBLIC_SITE_URL` | Canonical site URL (optional; falls back to Vercel URLs) |

Copy them into `.env.local` for local development. **Never commit credentials.**

## Develop

```bash
npm install
npm run dev
```

## Deploy

Deploy to Vercel and set the environment variables above in the project
settings. No other infrastructure is required.

## Dependencies

Beyond the Next.js/Tailwind scaffold: `@aws-sdk/client-s3` (bucket listing),
`cheerio` (metadata extraction), `server-only` (keeps bucket logic out of the
client bundle).
