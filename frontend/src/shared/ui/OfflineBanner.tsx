import { useOnline } from '../hooks/useOnline';

export function OfflineBanner() {
  if (useOnline()) return null;
  return (
    <div className="offline" role="status">
      📶 Sin señal: estás viendo los últimos datos guardados. Tus reportes se envían cuando vuelva la conexión.
    </div>
  );
}
