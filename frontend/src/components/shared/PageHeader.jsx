export function PageHeader({ title, description, action }) {
  return (
    <div className="page-header">
      <div>
        <p className="eyebrow">Operations</p>
        <h2>{title}</h2>
        <p className="muted">{description}</p>
      </div>
      {action}
    </div>
  );
}
