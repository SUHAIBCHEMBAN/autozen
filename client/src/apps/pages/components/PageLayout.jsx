function PageLayout({ title, subtitle, badge, children }) {
  return (
    <article className="page">
      <div className="page-hero">
        {badge && <span className="pill pill--soft">{badge}</span>}
        <h2>{title}</h2>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      <div className="page-body">{children}</div>
    </article>
  )
}

export default PageLayout

