
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from urllib.parse import unquote
import re


# ==========================================
# 1. PARÁMETROS DE SEGUIMIENTO GENERALES
# ==========================================

GENERAL_TRACKING = {
    "fbclid",
    "gclid",
    "gclsrc",
    "dclid",
    "gbraid",
    "wbraid",
    "msclkid",
    "yclid",
    "twclid",
    "ttclid",
    "li_fat_id",
    "mc_cid",
    "mc_eid",
}


# ==========================================
# 2. PARÁMETROS ESPECÍFICOS POR PLATAFORMA
# ==========================================

PLATFORM_TRACKING = {

    "instagram": {
        "igsh",
        "igshid",
        "igsi",
        "ig_rid",
        "stkn",
    },

    "facebook": {
        "mibextid",
        "rdid",
        "sfnsn",
        "fb_action_ids",
        "fb_action_types",
        "fb_source",
        "fb_ref",
        "__cft__",
        "__tn__",
    },

    "youtube": {
        "si",
        "pp",
        "feature",
    },

    "tiktok": {
        "_r",
        "_t",
        "is_from_webapp",
        "sender_device",
        "sender_web_id",
        "web_id",
        "share_app_id",
        "share_link_id",
        "share_item_id",
        "social_share_type",
        "tt_from",
        "u_code",
    },

    "pinterest": {
        "epik",
    },

    "linkedin": {
        "rcm",
        "trk",
        "trkinfo",
        "trackingid",
        "lipi",
        "refid",
        "midtoken",
        "midsig",
        "eid",
    },

    "x": {
        "a",
        "s",
        "t",
        "ref_src",
        "ref_url",
    },
}


# ==========================================
# 3. IDENTIFICAR LA PLATAFORMA
# ==========================================

PLATFORMS = {
    "instagram": ["instagram.com"],
    "facebook": ["facebook.com", "fb.com"],
    "youtube": ["youtube.com", "youtu.be"],
    "tiktok": ["tiktok.com", "vm.tiktok.com", "vt.tiktok.com"],
    "pinterest": ["pinterest.com", "pin.it"],
    "linkedin": ["linkedin.com"],
    "x": ["x.com", "twitter.com"],
}


def detect_platform(host):
    host = host.lower().split(":")[0]

    for platform, domains in PLATFORMS.items():
        for domain in domains:
            if host == domain or host.endswith("." + domain):
                return platform

    return None


# ==========================================
# 4. IDENTIFICAR PARÁMETROS INNECESARIOS
# ==========================================

def is_tracking_param(param, platform=None):

    param = unquote(param).lower()

    # Seguimiento general
    if param in GENERAL_TRACKING:
        return True

    # Parámetros UTM
    if param.startswith("utm_"):
        return True

    # Otros parámetros conocidos de analítica
    if param.startswith(("pk_", "_hsenc", "_hsmi")):
        return True

    # Seguimiento específico de cada plataforma
    if platform and param in PLATFORM_TRACKING.get(platform, set()):
        return True

    return False


# ==========================================
# 5. LIMPIAR EL ENLACE
# ==========================================

def clean_url(url):

    url = url.strip()

    # Quitar posibles caracteres de envoltura
    url = url.strip("<>[](){}\"'")

    if not url:
        return None

    # Agregar protocolo si no existe
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    parsed = urlparse(url)

    # Validar estructura básica
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
        return None

    # Identificar plataforma
    platform = detect_platform(parsed.hostname)

    # Obtener parámetros
    params = parse_qsl(
        parsed.query,
        keep_blank_values=True
    )

    # Filtrar parámetros
    clean_params = [
        (key, value)
        for key, value in params
        if not is_tracking_param(key, platform)
    ]

    # Reconstruir consulta
    clean_query = urlencode(clean_params, doseq=True)

    # Reconstruir enlace
    cleaned_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        parsed.fragment
    ))

    return cleaned_url


# ==========================================
# 6. EJECUCIÓN
# ==========================================

if __name__ == "__main__":

    print("\n" + "=" * 50)
    print("           LIMPIADOR DE ENLACES")
    print("=" * 50)

    while True:

        url = input("\nPega un enlace (o escribe 'salir'): ")

        if url.lower().strip() == "salir":
            print("\n¡Hasta luego!")
            break

        resultado = clean_url(url)

        if resultado:

            print("\nEnlace limpio:")
            print(resultado)

            print("\nCopiar resultado:")
            print(resultado)

        else:
            print("\nEl enlace no tiene un formato válido.")

        print("\n" + "-" * 50)