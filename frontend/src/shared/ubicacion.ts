export type Coordenadas = { lat: number; lon: number };

export function ubicacionActual(): Promise<Coordenadas> {
  return new Promise((ok, mal) => {
    if (!navigator.geolocation) return mal(new Error('Tu navegador no permite obtener la ubicación.'));
    navigator.geolocation.getCurrentPosition(
      (p) => ok({ lat: p.coords.latitude, lon: p.coords.longitude }),
      (e) =>
        mal(new Error(e.code === e.PERMISSION_DENIED
          ? 'Necesitamos permiso de ubicación para marcar el reporte en el mapa.'
          : 'No pudimos obtener tu ubicación. Probá al aire libre o de nuevo en unos segundos.')),
      { enableHighAccuracy: true, timeout: 15_000, maximumAge: 30_000 },
    );
  });
}
