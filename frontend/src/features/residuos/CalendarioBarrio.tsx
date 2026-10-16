import { useQuery } from '@tanstack/react-query';
import { getJson } from '../../shared/api/client';
import { usePreferencia } from '../../shared/hooks/usePreferencia';
import { ErrorState } from '../../shared/ui/ErrorState';
import { Skeleton } from '../../shared/ui/Skeleton';

type Recorrido = { barrio: string; ciudad: string; dias: string[]; hora: string; proximo_paso: string };

const clave = (r: Recorrido) => `${r.ciudad}|${r.barrio}`;
const HORAS_AVISO = 12;

export function CalendarioBarrio() {
  const [elegido, setElegido] = usePreferencia('barrio', '');
  const q = useQuery({
    queryKey: ['calendario'],
    queryFn: () => getJson<Recorrido[]>('/residuos/calendario'),
    refetchInterval: 30 * 60_000,
  });

  if (q.isPending) return <Skeleton alto={80} />;
  if (q.isError) return <ErrorState error={q.error} reintentar={() => q.refetch()} />;

  const r = q.data.find((x) => clave(x) === elegido);
  const paso = r && new Date(r.proximo_paso);
  const pronto = paso && paso.getTime() - Date.now() < HORAS_AVISO * 3600_000;

  return (
    <div className="pila">
      <label className="sr-only" htmlFor="barrio">Tu barrio</label>
      <select id="barrio" value={elegido} onChange={(e) => setElegido(e.target.value)}>
        <option value="">Elegí tu barrio…</option>
        {q.data.map((x) => (
          <option key={clave(x)} value={clave(x)}>{x.barrio} — {x.ciudad}</option>
        ))}
      </select>
      {r && paso && (
        <div className={pronto ? 'aviso' : 'tarjeta'}>
          {pronto && <strong>⏰ ¡Sacá la basura! </strong>}
          Próximo paso: <strong>
            {paso.toLocaleString('es-PY', { weekday: 'long', hour: '2-digit', minute: '2-digit', timeZone: 'America/Asuncion' })}
          </strong>
          <p>Pasa los {r.dias.join(', ')} a las {r.hora}.</p>
        </div>
      )}
    </div>
  );
}
