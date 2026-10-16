import { useState } from 'react';

/** Valor recordado en este celular (ciudad, barrio). Si el almacenamiento falla, funciona en memoria. */
export function usePreferencia(clave: string, inicial: string) {
  const [valor, setValor] = useState(() => {
    try {
      return localStorage.getItem(clave) ?? inicial;
    } catch {
      return inicial;
    }
  });
  const guardar = (v: string) => {
    setValor(v);
    try {
      localStorage.setItem(clave, v);
    } catch {
      /* sin almacenamiento: queda solo en memoria */
    }
  };
  return [valor, guardar] as const;
}
