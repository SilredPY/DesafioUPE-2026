// Motor nativo de agrupación de reportes (anti-spam de Tape Ysyry).
// Misma semántica que app/modules/transito/agrupacion.py::asignar_grupos_py, pero con una grilla espacial:
// cada reporte se compara solo con los grupos de las 9 celdas vecinas → ~O(n) en vez de O(n·grupos).
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <unordered_map>
#include <vector>

namespace py = pybind11;

namespace {

constexpr double PI = 3.14159265358979323846;
constexpr double RAD = PI / 180.0;
constexpr double RADIO_TIERRA_M = 6371000.0;              // igual que app/shared/geo.py
constexpr double M_POR_GRADO = RADIO_TIERRA_M * RAD;       // metros por grado de latitud en la esfera

double distancia_m(double lat1, double lon1, double lat2, double lon2) {
    const double dlat = (lat2 - lat1) * RAD, dlon = (lon2 - lon1) * RAD;
    const double s1 = std::sin(dlat / 2), s2 = std::sin(dlon / 2);
    const double h = s1 * s1 + std::cos(lat1 * RAD) * std::cos(lat2 * RAD) * s2 * s2;
    return 2 * RADIO_TIERRA_M * std::asin(std::sqrt(h));
}

std::uint64_t clave(std::int64_t cx, std::int64_t cy) {
    return (static_cast<std::uint64_t>(static_cast<std::uint32_t>(cx)) << 32) | static_cast<std::uint32_t>(cy);
}

struct Ancla {
    double lat, lon;
    int tipo;
};

// Devuelve, para cada reporte (ya ordenado por fecha), el índice de su grupo.
// Un reporte se une al grupo más antiguo del mismo tipo cuyo primer reporte (ancla) esté a <= radio_m.
std::vector<int> asignar_grupos(const std::vector<double>& lat, const std::vector<double>& lon,
                                const std::vector<int>& tipo, double radio_m) {
    const std::size_t n = lat.size();
    if (lon.size() != n || tipo.size() != n) throw std::invalid_argument("lat, lon y tipo deben tener el mismo largo");
    if (!(radio_m > 0)) throw std::invalid_argument("radio_m debe ser positivo");

    std::vector<int> grupo(n);
    if (n == 0) return grupo;

    double max_lat = 0;
    for (double v : lat) max_lat = std::max(max_lat, std::fabs(v));
    // Celdas un 5 % más grandes que el radio: un ancla a <= radio siempre cae en las 9 celdas vecinas.
    const double celda_lat = radio_m / M_POR_GRADO * 1.05;
    const double celda_lon = radio_m / (M_POR_GRADO * std::cos(std::min(89.0, max_lat + 1.0) * RAD)) * 1.05;

    std::vector<Ancla> anclas;
    std::unordered_map<std::uint64_t, std::vector<int>> celdas;
    celdas.reserve(n);

    for (std::size_t i = 0; i < n; ++i) {
        const auto cx = static_cast<std::int64_t>(std::floor(lon[i] / celda_lon));
        const auto cy = static_cast<std::int64_t>(std::floor(lat[i] / celda_lat));
        int mejor = -1;
        for (int dx = -1; dx <= 1; ++dx) {
            for (int dy = -1; dy <= 1; ++dy) {
                const auto it = celdas.find(clave(cx + dx, cy + dy));
                if (it == celdas.end()) continue;
                for (int g : it->second) {
                    if ((mejor == -1 || g < mejor) && anclas[g].tipo == tipo[i] &&
                        distancia_m(anclas[g].lat, anclas[g].lon, lat[i], lon[i]) <= radio_m) {
                        mejor = g;
                    }
                }
            }
        }
        if (mejor == -1) {
            mejor = static_cast<int>(anclas.size());
            anclas.push_back({lat[i], lon[i], tipo[i]});
            celdas[clave(cx, cy)].push_back(mejor);
        }
        grupo[i] = mejor;
    }
    return grupo;
}

}  // namespace

PYBIND11_MODULE(naangareko_nativo, m) {
    m.doc() = "Motor nativo (C++) de Ñangarekó IA";
    m.def("asignar_grupos", &asignar_grupos, py::arg("lat"), py::arg("lon"), py::arg("tipo"), py::arg("radio_m"),
          py::call_guard<py::gil_scoped_release>(),
          "Índice de grupo por reporte (ordenados por fecha), agrupando por tipo dentro de radio_m metros.");
}
