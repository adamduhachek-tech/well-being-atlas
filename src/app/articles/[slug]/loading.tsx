export default function ArticleLoading() {
  return (
    <main>
      <header className="article-chrome" aria-busy="true">
        <span className="back-link">
          <span aria-hidden="true">←</span> Index
        </span>
      </header>
      <div className="article-frame" />
    </main>
  );
}
