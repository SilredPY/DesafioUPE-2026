export function Skeleton({ alto = 96, cantidad = 1 }: { alto?: number; cantidad?: number }) {
  return (
    <div className="pila" aria-busy="true" aria-label="Cargando">
      {Array.from({ length: cantidad }, (_, i) => (
        <div key={i} className="skeleton" style={{ height: alto }} />
      ))}
    </div>
  );
}
