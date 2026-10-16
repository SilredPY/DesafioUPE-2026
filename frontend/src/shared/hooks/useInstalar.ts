import { useEffect, useState } from 'react';

type EventoInstalar = Event & { prompt: () => Promise<void> };

/** Botón "Instalar app": Chrome/Android avisa cuando la PWA se puede instalar. */
export function useInstalar() {
  const [evento, setEvento] = useState<EventoInstalar | null>(null);

  useEffect(() => {
    const guardar = (e: Event) => {
      e.preventDefault();
      setEvento(e as EventoInstalar);
    };
    const instalada = () => setEvento(null);
    window.addEventListener('beforeinstallprompt', guardar);
    window.addEventListener('appinstalled', instalada);
    return () => {
      window.removeEventListener('beforeinstallprompt', guardar);
      window.removeEventListener('appinstalled', instalada);
    };
  }, []);

  return evento ? () => evento.prompt().finally(() => setEvento(null)) : null;
}
