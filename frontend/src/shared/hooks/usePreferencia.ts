import { useCallback, useState } from 'react';

/** Valor recordado en este celular (ciudad, barrio). Si el almacenamiento falla, funciona en memoria. */
export function usePreferencia(clave: string, inicial: string) {
  const [valor, setValor] = useState(() => {
    try {
      return localStorage.getItem(clave) ?? inicial;
    } catch {
      return inicial;
    }
  });
  const guardar = useCallback((v: string) => {
    setValor(v);
    try {
      localStorage.setItem(clave, v);
    } catch {
      /* sin almacenamiento: queda solo en memoria */
    }
  }, [clave]);
  return [valor, guardar] as const;
}
