import os, json, urllib.request
from datetime import datetime, timedelta, timezone

MX = timezone(timedelta(hours=-6))  # Torreón, no DST
TOKEN = os.environ["BANXICO_TOKEN"]
NOTIFY_URLS = os.environ["MACRO_NOTIFY_URLS"]
APPRISE = os.getenv("APPRISE_ENDPOINT", "http://apprise:8000/notify/")
SERIES = {"SF61745": "tasa", "SF43718": "fix"}
BANXICO = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{','.join(SERIES)}/datos/oportuno"

def banxico():
    try:
        req = urllib.request.Request(BANXICO, headers={"Bmx-Token": TOKEN, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            series = json.load(r)["bmx"]["series"]
        d = {SERIES[s["idSerie"]]: s["datos"][0] for s in series}
        return [
            f"• Tasa objetivo: {float(d['tasa']['dato']):.2f}% (al {d['tasa']['fecha']})",
            f"• Dólar FIX: ${float(d['fix']['dato']):.4f} MXN (al {d['fix']['fecha']})",
        ]
    except Exception as e:
        return [f"• Error Banxico: {e}"]

def inegi(dia):
    a = []
    if dia in (9, 10, 24, 25):
        a.append("⚠️ Posible INPC quincenal (INEGI)")
    if dia >= 26:
        a.append("⚠️ Monitorear ENOE / desocupación (INEGI)")
    return a or ["• Sin publicaciones previstas hoy"]

def main():
    now = datetime.now(MX)
    body = "\n".join(["[Banxico]", *banxico(), "", "[INEGI]", *inegi(now.day)])
    payload = json.dumps({"urls": NOTIFY_URLS,
                          "title": f"Reporte Macro MX {now:%Y-%m-%d}",
                          "body": body}).encode()
    req = urllib.request.Request(APPRISE, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        resp = r.read().decode(errors="replace")
        print(now.isoformat(), r.status, resp[:200])
        if r.status != 200:
            raise SystemExit(f"Apprise did not send (HTTP {r.status})")

if __name__ == "__main__":
    main()
