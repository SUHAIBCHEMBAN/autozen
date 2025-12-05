function InfoCard({ title, items, body, highlight }) {
  return (
    <div className="info-card">
      <div className="info-card__header">
        <h3>{title}</h3>
        {highlight && <span className="pill pill--outline">{highlight}</span>}
      </div>
      {body && <p className="info-card__body">{body}</p>}
      {items?.length > 0 && (
        <ul className="info-card__list">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default InfoCard

