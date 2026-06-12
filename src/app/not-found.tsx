import Link from "next/link";

export default function NotFound() {
  return (
    <main id="content" className="notfound">
      <p className="masthead-kicker">
        <span>The Well-Being Atlas</span>
      </p>
      <h1>Not in the index.</h1>
      <p>
        No reading lives at this address — it may have been renamed or never
        existed.
      </p>
      <Link href="/" className="back-link">
        <span aria-hidden="true">←</span> Back to the index
      </Link>
    </main>
  );
}
