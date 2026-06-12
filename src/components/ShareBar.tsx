"use client";

import { useState, useSyncExternalStore } from "react";

const noopSubscribe = () => () => {};

export function ShareBar({
  title,
  description,
}: {
  title: string;
  description: string | null;
}) {
  const canNativeShare = useSyncExternalStore(
    noopSubscribe,
    () => typeof navigator.share === "function",
    () => false
  );
  const [copied, setCopied] = useState(false);

  const shareText = description ? `${title} — ${description}` : title;
  // The shared link is always this app's article URL (it carries the OG
  // metadata), never the raw bucket URL.
  const pageUrl = () => window.location.href;

  const open = (href: string) =>
    window.open(href, "_blank", "noopener,noreferrer");

  const nativeShare = async () => {
    try {
      await navigator.share({ title, text: shareText, url: pageUrl() });
    } catch {
      // User dismissed the sheet; nothing to do.
    }
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(pageUrl());
    } catch {
      const input = document.createElement("input");
      input.value = pageUrl();
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      input.remove();
    }
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  const enc = encodeURIComponent;

  return (
    <div className="share-bar">
      {copied && (
        <span className="copied-note" role="status">
          Copied
        </span>
      )}
      {canNativeShare && (
        <button
          type="button"
          className="share-btn"
          onClick={nativeShare}
          aria-label="Share"
          title="Share"
        >
          <ShareIcon />
        </button>
      )}
      <button
        type="button"
        className="share-btn"
        onClick={() =>
          open(`https://twitter.com/intent/tweet?text=${enc(title)}&url=${enc(pageUrl())}`)
        }
        aria-label="Share on X"
        title="Share on X"
      >
        <XIcon />
      </button>
      <button
        type="button"
        className="share-btn"
        onClick={() =>
          open(`https://bsky.app/intent/compose?text=${enc(`${title} ${pageUrl()}`)}`)
        }
        aria-label="Share on Bluesky"
        title="Share on Bluesky"
      >
        <BlueskyIcon />
      </button>
      <button
        type="button"
        className="share-btn"
        onClick={() =>
          open(`https://www.linkedin.com/sharing/share-offsite/?url=${enc(pageUrl())}`)
        }
        aria-label="Share on LinkedIn"
        title="Share on LinkedIn"
      >
        <LinkedInIcon />
      </button>
      <button
        type="button"
        className="share-btn"
        onClick={() =>
          open(`https://www.facebook.com/sharer/sharer.php?u=${enc(pageUrl())}`)
        }
        aria-label="Share on Facebook"
        title="Share on Facebook"
      >
        <FacebookIcon />
      </button>
      <button
        type="button"
        className={copied ? "share-btn share-btn--copied" : "share-btn"}
        onClick={copyLink}
        aria-label="Copy link"
        title="Copy link"
      >
        <LinkIcon />
      </button>
    </div>
  );
}

function ShareIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M18.9 2H22l-6.8 7.8L23.2 22h-6.3l-4.9-6.4L6.4 22H3.3l7.3-8.3L2.8 2h6.4l4.4 5.9L18.9 2zm-1.1 18h1.7L7.1 3.9H5.3L17.8 20z" />
    </svg>
  );
}

function BlueskyIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 10.8C10.9 8.6 7.9 4.6 5.1 2.6 2.4.7 1.4 1 .8 1.3.1 1.7 0 2.8 0 3.5s.4 5.7.6 6.5c.8 2.6 3.6 3.5 6.2 3.2-3.8.6-7.2 2-2.7 6.9 4.9 5.1 6.7-1.1 7.9-4.2 1.2 3.1 2.6 9 7.8 4.2 4-4.2 1.1-6.3-2.7-6.9 2.6.3 5.4-.6 6.2-3.2.2-.8.7-5.8.7-6.5s-.1-1.8-.8-2.2c-.6-.3-1.6-.6-4.3 1.3C16.1 4.6 13.1 8.6 12 10.8z" />
    </svg>
  );
}

function LinkedInIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.9-3-1.8 0-2.1 1.4-2.1 2.9v5.7H9.3V9h3.4v1.6h.1c.5-.9 1.7-1.9 3.4-1.9 3.6 0 4.3 2.4 4.3 5.5v6.3zM5.3 7.4a2.1 2.1 0 1 1 0-4.2 2.1 2.1 0 0 1 0 4.2zM7.1 20.5H3.5V9h3.6v11.5z" />
    </svg>
  );
}

function FacebookIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12z" />
    </svg>
  );
}

function LinkIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7" />
      <path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7" />
    </svg>
  );
}
