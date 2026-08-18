# -*- coding: utf-8 -*-
"""Monte Carlo de los ingresos de Atlas IA en un año (2027).

POR QUE MONTE CARLO Y NO UNA CUENTA. Una sola cuenta ("500 instalaciones x 2
anuncios") da un numero que parece exacto y no lo es: cada pieza -cuantos
instalan, cuantos siguen al mes, cuanto paga el anuncio- es una distribucion,
no un dato. Lo que importa no es la media, es la FORMA: en casi todos estos
escenarios la media esta muy por encima de la mediana, porque la arrastran unos
pocos sorteos afortunados que no le van a pasar a nadie. Por eso aqui se mira la
mediana y el percentil 10, que es lo que de verdad se cobra.

Cada escenario devuelve el ingreso NETO del año, en dolares.

    python montecarlo.py
"""
import json
import numpy as np

N = 200_000
rng = np.random.default_rng(20270101)   # fijo: dos ejecuciones dan lo mismo


# ---------------------------------------------------------------- utilidades
def lognormal_de(mediana, p90):
    """Lognormal descrita como la usa un humano: 'la mitad de las veces por
    debajo de X, y una de cada diez por encima de Y'."""
    mu = np.log(mediana)
    sigma = (np.log(p90) - mu) / 1.2816          # z(0.90)
    return rng.lognormal(mu, sigma, N)


def beta_de(media, concentracion):
    """Beta parametrizada por su media, que es como se piensa una tasa."""
    a = media * concentracion
    b = (1 - media) * concentracion
    return rng.beta(a, b, N)


# ------------------------------------------------------- piezas compartidas
def ingreso_consumo(instalaciones, mult_ecpm=1.0):
    """Anuncios + Atlas Pro. Devuelve (total, anuncios, pro).

    Los anuncios NO son 2 al dia por instalacion: son 2 al dia por usuario que
    sigue abriendo la app. Con una retencion a 30 dias del 5-10%, que es lo
    normal en fitness, la inmensa mayoria de las instalaciones no vale nada.
    """
    d30 = beta_de(0.075, 60)                       # media 7,5%, cola gorda
    dau = instalaciones * d30 * 0.45               # de los que retienen, no todos entran a diario
    dias_medios = 180                              # el que instala en julio no da 365 dias

    ecpm = lognormal_de(2.5, 6.0) * mult_ecpm      # LatAm; Espana sube la mezcla
    imp = dau * 2 * dias_medios                    # 2 intersticiales al dia
    anuncios = imp / 1000 * ecpm
    anuncios = np.where(anuncios < 100, 0.0, anuncios)   # AdMob no paga hasta 100 US$

    ve_muro = instalaciones * 0.60
    conv = beta_de(0.012, 200)                     # 1,2% de los que ven el muro
    pagos = ve_muro * conv
    pro = pagos * 20.0 * 0.85                      # ticket medio 20 US$, Google se lleva 15%
    return anuncios + pro, anuncios, pro


def licencias_b2b(cierres_mes, precio_mes, baja_mes, frac_anual, precio_anual, meses=12):
    """Meses-cliente cobrados a lo largo del año.

    El que cierra en agosto solo paga 5 meses del año, no 12: por eso se recorre
    mes a mes en vez de multiplicar clientes por doce, que es el error clasico
    que infla estas cuentas al doble.
    """
    ingreso = np.zeros(N)
    activos = np.zeros(N)
    for m in range(meses):
        nuevos = rng.poisson(cierres_mes, N)
        anuales = rng.binomial(nuevos, frac_anual)
        mensuales = nuevos - anuales
        ingreso += anuales * precio_anual          # el anual cobra los 12 el dia que firma
        activos = activos * (1 - baja_mes) + mensuales
        ingreso += activos * precio_mes
    return ingreso * 0.971                         # pasarela local ~2,9%


# ------------------------------------------------------------- escenarios
def esc_play_solo():
    """Publicar en Play y ya. Sin marketing, sin contarselo a nadie."""
    inst = lognormal_de(280, 1500)
    total, _, _ = ingreso_consumo(inst)
    return total


def esc_play_conocidos():
    """Play + los ~100 estudiantes y profesores. Tu idea original."""
    directos = rng.binomial(100, beta_de(0.55, 40))          # cuantos instalan de verdad
    boca = directos * rng.gamma(2.0, 1.5, N)                 # cada uno trae algunos
    inst = lognormal_de(280, 1500) + directos + boca
    total, _, _ = ingreso_consumo(inst)
    return total


def esc_tiktok():
    """Contenido sostenido. Casi siempre no pasa nada; a veces pega uno."""
    pega = rng.random(N) < 0.18                              # 18%: un video que funciona
    base = lognormal_de(600, 4000)
    salto = np.where(pega, lognormal_de(9000, 60000), 0.0)
    inst = base + salto
    total, _, _ = ingreso_consumo(inst)
    # el que hace contenido tambien vende algo de Pro mejor: la audiencia es afin
    return total * 1.15


def esc_b2b_entrenadores():
    """El plan del panel: licencia al entrenador que YA cobra, vendida en la web.

    Sin comision de Google, sin necesitar volumen. La incognita no son las
    instalaciones, es cuantos entrenadores cierras al mes con 6 h semanales.
    """
    cierres = rng.gamma(2.2, 1.0, N)                         # media ~2,2 cierres/mes
    lic = licencias_b2b(cierres, precio_mes=19.0, baja_mes=0.12,
                        frac_anual=0.40, precio_anual=168.0)
    talleres = rng.poisson(9, N) * rng.normal(60, 18, N).clip(20, 140)
    inst = lognormal_de(400, 2200)
    consumo, _, _ = ingreso_consumo(inst)
    return lic + talleres + consumo * 0.7                    # el que entra por un coach no ve anuncios


def esc_b2b_gimnasios():
    """Mi idea inicial: vender al gimnasio de barrio."""
    cierres = rng.gamma(1.1, 0.75, N)                        # decide lento y regatea
    lic = licencias_b2b(cierres, precio_mes=48.0, baja_mes=0.09,
                        frac_anual=0.25, precio_anual=430.0)
    inst = lognormal_de(500, 3000)
    consumo, _, _ = ingreso_consumo(inst)
    return lic + consumo * 0.7


def esc_institucional():
    """Una sola venta grande: universidad, caja de compensacion, secretaria."""
    intentos = rng.poisson(3, N)
    exitos = rng.binomial(intentos, 0.11)
    contrato = rng.normal(1800, 550, N).clip(700, 4000)
    grande = exitos * contrato
    inst = lognormal_de(400, 2200)
    consumo, _, _ = ingreso_consumo(inst)
    return grande + consumo


def esc_plan_completo():
    """Entrenadores + talleres + la apuesta institucional de junio + residuo."""
    cierres = rng.gamma(2.2, 1.0, N)
    lic = licencias_b2b(cierres, precio_mes=19.0, baja_mes=0.12,
                        frac_anual=0.40, precio_anual=168.0)
    talleres = rng.poisson(11, N) * rng.normal(62, 18, N).clip(20, 140)
    intentos = rng.poisson(2, N)
    exitos = rng.binomial(intentos, 0.10)
    grande = exitos * rng.normal(1700, 500, N).clip(700, 3500)
    inst = lognormal_de(450, 2500)
    consumo, _, _ = ingreso_consumo(inst)
    return lic + talleres + grande + consumo * 0.7


ESCENARIOS = [
    ("Solo publicar en Play",      esc_play_solo),
    ("Play + tus 100 conocidos",   esc_play_conocidos),
    ("Contenido en TikTok",        esc_tiktok),
    ("Vender a gimnasios",         esc_b2b_gimnasios),
    ("Una venta institucional",    esc_institucional),
    ("Licencia a entrenadores",    esc_b2b_entrenadores),
    ("EL PLAN (todo junto)",       esc_plan_completo),
]


def resumen(x):
    return {
        "p10":   float(np.percentile(x, 10)),
        "p25":   float(np.percentile(x, 25)),
        "media": float(np.mean(x)),
        "p50":   float(np.percentile(x, 50)),
        "p75":   float(np.percentile(x, 75)),
        "p90":   float(np.percentile(x, 90)),
        "p99":   float(np.percentile(x, 99)),
        "p_1k":  float(np.mean(x >= 1000) * 100),
        "p_5k":  float(np.mean(x >= 5000) * 100),
        "p_10k": float(np.mean(x >= 10000) * 100),
        "p_cero": float(np.mean(x < 100) * 100),
    }


if __name__ == "__main__":
    datos, series = {}, {}
    for nombre, fn in ESCENARIOS:
        x = fn()
        datos[nombre] = resumen(x)
        series[nombre] = x

    print(f"{N:,} simulaciones · ingreso NETO del año, en dolares\n")
    cab = f"{'escenario':<26}{'p10':>8}{'mediana':>10}{'media':>9}{'p90':>9}{'>=10k':>8}"
    print(cab); print("-" * len(cab))
    for n, d in datos.items():
        print(f"{n:<26}{d['p10']:>8,.0f}{d['p50']:>10,.0f}{d['media']:>9,.0f}"
              f"{d['p90']:>9,.0f}{d['p_10k']:>7.1f}%")

    with open("montecarlo_datos.json", "w", encoding="utf-8") as f:
        json.dump({"n": N, "escenarios": datos,
                   "hist": {k: np.histogram(np.clip(v, 0, 15000), bins=40,
                                            range=(0, 15000))[0].tolist()
                            for k, v in series.items()}}, f, ensure_ascii=False, indent=1)
    np.save("montecarlo_series.npy", np.array([series[n] for n, _ in ESCENARIOS]))
    print("\ndatos -> montecarlo_datos.json")
