export function ErrorState({ error, reintentar }: { error: unknown; reintentar?: () => void }) {
  const mensaje = error instanceof Error ? error.message : 'Algo salió mal.';
  return (
    <div className="aviso error pila" role="alert">
      <span>{navigator.onLine ? mensaje : 'Sin conexión y sin datos guardados todavía.'}</span>
      {reintentar && (
        <button className="boton secundario" onClick={reintentar}>
          Reintentar
        </button>
      )}
    </div>
  );
}
