import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

/**
 * Force-refresh the article index after publishing to the bucket:
 *   curl -X POST "https://<site>/api/revalidate?secret=<REVALIDATE_SECRET>"
 * Without it, the gallery refreshes on its own within ~1 hour.
 */
export async function POST(req: NextRequest) {
  const secret =
    req.nextUrl.searchParams.get("secret") ??
    req.headers.get("x-revalidate-secret");

  if (!process.env.REVALIDATE_SECRET || secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ ok: false, error: "Invalid secret" }, { status: 401 });
  }

  revalidateTag("articles", { expire: 0 });
  return NextResponse.json({ ok: true, revalidated: "articles" });
}
