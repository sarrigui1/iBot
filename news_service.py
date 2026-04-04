"""
NewsService — Datos fundamentales para el bot de trading.

Fuentes:
  CALENDARIO: https://nfs.faireconomy.media/ff_calendar_thisweek.json
    - Feed público de Forex Factory (las famosas "Carpetas Rojas")
    - Sin API key, sin límites, ~100 eventos semanales
    - Campos: title, country, date (ISO8601), impact (Low/Medium/High/Holiday)

  SENTIMIENTO / NOTICIAS: Finnhub API (plan gratuito)
    GET /news?category=forex    — noticias forex
    GET /news?category=general  — noticias generales (más volumen)
    Requiere FINNHUB_API_KEY en .env. Sin key = sentimiento N/A (no bloquea).

Diseño:
  - @staticmethod puras; nunca lanzan excepción al caller
  - El caché lo gestiona Streamlit (st.cache_data) en app.py (TTL 30 min)
"""

import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

_FINNHUB_BASE = "https://finnhub.io/api/v1"
_FF_CALENDAR  = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
_TIMEOUT      = 8   # segundos máximos por request

# Forex Factory impact strings → nivel numérico interno
_FF_IMPACT = {"High": 3, "Medium": 2, "Low": 1, "Holiday": 0}
_HIGH_IMPACT = {3}
_MED_IMPACT  = {2}

# Palabras clave para sentimiento derivado de titulares (free plan)
_BULL_WORDS = {"rises", "rally", "gains", "bullish", "strong", "surges",
               "breakout", "recovery", "positive", "up", "high", "boost"}
_BEAR_WORDS = {"falls", "drop", "decline", "bearish", "weak", "plunges",
               "breakdown", "selloff", "negative", "down", "low", "slump"}


class NewsService:

    # =========================================================================
    # API KEY
    # =========================================================================

    @staticmethod
    def _key() -> str:
        return os.getenv("FINNHUB_API_KEY", "").strip()

    @staticmethod
    def is_configured() -> bool:
        return bool(NewsService._key())

    # =========================================================================
    # 1. CALENDARIO ECONÓMICO  (free endpoint)
    # =========================================================================

    @staticmethod
    def get_economic_calendar(currencies: list) -> dict:
        """
        Obtiene los eventos económicos de la semana desde el feed público de
        Forex Factory (sin API key, sin límites de rate).

        URL: https://nfs.faireconomy.media/ff_calendar_thisweek.json

        Filtra por las monedas del símbolo y enriquece con tiempo relativo.

        Returns:
            {
              "events":          list[dict],   # eventos del día para las monedas
              "high_impact":     list[dict],   # solo impacto High (Carpetas Rojas)
              "next_high":       dict | None,  # próximo evento High
              "minutes_to_next": int,          # minutos hasta el próximo High
              "error":           str | None,
            }
        """
        empty = {
            "events": [], "high_impact": [], "next_high": None,
            "minutes_to_next": 999, "error": None,
        }

        try:
            now_utc = datetime.now(timezone.utc)
            today_date = now_utc.date()

            resp = requests.get(
                _FF_CALENDAR,
                headers={"User-Agent": "Mozilla/5.0 (compatible; TradingBot/1.0)"},
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            raw_events = resp.json()   # lista directa, no envuelto en objeto

            currencies_upper = {c.upper() for c in currencies}

            enriched = []
            for e in raw_events:
                country = e.get("country", "").upper()
                if country not in currencies_upper:
                    continue

                # Parsear fecha ISO con offset de zona horaria → UTC
                date_str = e.get("date", "")
                try:
                    event_dt = datetime.fromisoformat(date_str).astimezone(timezone.utc)
                except (ValueError, TypeError):
                    continue

                # Filtrar solo eventos de hoy (en UTC)
                if event_dt.date() != today_date:
                    continue

                mins_away = int((event_dt - now_utc).total_seconds() / 60)
                impact_str = e.get("impact", "Low")
                impact_num = _FF_IMPACT.get(impact_str, 1)

                enriched.append({
                    "time":      event_dt.strftime("%H:%M"),
                    "datetime":  event_dt,
                    "mins_away": mins_away,
                    "country":   country,
                    "currency":  country,
                    "event":     e.get("title", "—"),
                    "impact":    impact_num,
                    "actual":    "",
                    "estimate":  e.get("forecast", ""),
                    "prev":      e.get("previous", ""),
                })

            enriched.sort(key=lambda x: x["mins_away"])

            high_impact = [e for e in enriched if e["impact"] in _HIGH_IMPACT]
            # Próximo evento High que aún no ha pasado más de 15 min
            future_high = [e for e in high_impact if e["mins_away"] >= -15]
            next_high    = future_high[0] if future_high else None
            mins_to_next = next_high["mins_away"] if next_high else 999

            return {
                "events":          enriched,
                "high_impact":     high_impact,
                "next_high":       next_high,
                "minutes_to_next": mins_to_next,
                "error":           None,
            }

        except requests.exceptions.ConnectionError:
            empty["error"] = "CONNECTION_ERROR"
            return empty
        except requests.exceptions.Timeout:
            empty["error"] = "TIMEOUT"
            return empty
        except requests.exceptions.HTTPError as e:
            empty["error"] = f"HTTP_{e.response.status_code}"
            return empty
        except Exception as e:
            empty["error"] = f"UNKNOWN: {type(e).__name__}"
            return empty

    # =========================================================================
    # 2. SENTIMIENTO DERIVADO DE NOTICIAS FOREX  (free endpoint)
    # =========================================================================

    @staticmethod
    def get_market_sentiment(symbol: str) -> dict:
        """
        Calcula sentimiento simple a partir de titulares de /news?category=forex.
        (Reemplaza el endpoint premium /news-sentiment que devuelve 403 en plan free.)

        Returns:
            {
              "bullish_pct": float,
              "bearish_pct": float,
              "neutral_pct": float,
              "label":       str,   "BULLISH" | "BEARISH" | "NEUTRAL"
              "score":       float, -1.0 a +1.0
              "buzz":        int,   articulos encontrados
              "error":       str | None,
            }
        """
        neutral = {
            "bullish_pct": 0.33, "bearish_pct": 0.33, "neutral_pct": 0.34,
            "label": "NEUTRAL", "score": 0.0, "buzz": 0, "error": None,
        }

        if not NewsService.is_configured():
            neutral["error"] = "NO_API_KEY"
            return neutral

        try:
            # /news?category=general devuelve ~100 artículos en plan free
            # /news?category=forex devuelve muy pocos (1-3); lo usamos como complemento
            resp_gen = requests.get(
                f"{_FINNHUB_BASE}/news",
                params={"category": "general", "token": NewsService._key()},
                timeout=_TIMEOUT,
            )
            resp_gen.raise_for_status()
            items = resp_gen.json()

            resp_fx = requests.get(
                f"{_FINNHUB_BASE}/news",
                params={"category": "forex", "token": NewsService._key()},
                timeout=_TIMEOUT,
            )
            if resp_fx.status_code == 200:
                items = resp_fx.json() + items   # forex primero, luego general

            # Filtrar noticias que mencionan las monedas del símbolo
            sym_upper = symbol.upper()
            related = set()
            if len(sym_upper) >= 6:
                related.add(sym_upper[:3])
                related.add(sym_upper[3:6])
            related.add(sym_upper)

            relevant = [
                item for item in items
                if any(
                    kw in item.get("headline", "").upper()
                    or kw in item.get("summary", "").upper()
                    for kw in related
                )
            ]
            # Fallback: si no hay noticias relacionadas, usar las primeras 30
            if not relevant:
                relevant = items[:30]

            bull_count = 0
            bear_count = 0
            for item in relevant:
                words = set((item.get("headline", "") + " " + item.get("summary", "")).lower().split())
                if words & _BULL_WORDS:
                    bull_count += 1
                elif words & _BEAR_WORDS:
                    bear_count += 1

            total = len(relevant)
            if total == 0:
                return neutral

            bull_pct = round(bull_count / total, 3)
            bear_pct = round(bear_count / total, 3)
            neut_pct = round(max(0.0, 1.0 - bull_pct - bear_pct), 3)
            score    = round(bull_pct - bear_pct, 3)

            if bull_pct > bear_pct + 0.1:
                label = "BULLISH"
            elif bear_pct > bull_pct + 0.1:
                label = "BEARISH"
            else:
                label = "NEUTRAL"

            return {
                "bullish_pct": bull_pct,
                "bearish_pct": bear_pct,
                "neutral_pct": neut_pct,
                "label":       label,
                "score":       score,
                "buzz":        total,
                "error":       None,
            }

        except requests.exceptions.HTTPError as e:
            neutral["error"] = f"HTTP_{e.response.status_code}"
            return neutral
        except Exception as e:
            neutral["error"] = f"UNKNOWN: {type(e).__name__}"
            return neutral

    # =========================================================================
    # 3. NEWS SHIELD GATE  (sin llamada API — solo procesa el calendario)
    # =========================================================================

    @staticmethod
    def check_news_shield(calendar: dict, shield_minutes: int) -> dict:
        """
        Evalúa si debe activarse el News Shield Gate basándose en el calendario.
        No hace ninguna llamada HTTP — procesa el resultado de get_economic_calendar().
        """
        no_block = {
            "blocking": False, "reason": "", "event_name": "", "mins_away": 999, "currency": "",
        }

        # Si el calendario falló (error de red, etc.) no bloqueamos por seguridad
        if calendar.get("error"):
            return no_block

        next_high = calendar.get("next_high")
        if not next_high:
            return no_block

        mins = next_high.get("mins_away", 999)

        if -15 <= mins <= shield_minutes:
            return {
                "blocking":   True,
                "reason":     f"High-impact event in {mins} min",
                "event_name": next_high.get("event", "—"),
                "mins_away":  mins,
                "currency":   next_high.get("currency", ""),
            }

        return no_block

    # =========================================================================
    # 4. NOTICIAS RECIENTES PARA MARQUESINA  (free endpoint)
    # =========================================================================

    @staticmethod
    def get_recent_news(symbol: str, limit: int = 5) -> list:
        """
        Retorna las últimas noticias forex relacionadas con el símbolo.
        Usa /news?category=forex (free) en lugar de /company-news (premium).

        Returns: list[dict] con keys: headline, source, datetime, url
        """
        if not NewsService.is_configured():
            return []

        try:
            # Combinar forex + general para tener más titulares disponibles
            items = []
            for category in ("forex", "general"):
                r = requests.get(
                    f"{_FINNHUB_BASE}/news",
                    params={"category": category, "token": NewsService._key()},
                    timeout=_TIMEOUT,
                )
                if r.status_code == 200:
                    items.extend(r.json())

            # Filtrar por relevancia al símbolo
            sym_upper = symbol.upper()
            related = set()
            if len(sym_upper) >= 6:
                related.add(sym_upper[:3])
                related.add(sym_upper[3:6])
            related.add(sym_upper)

            relevant = [
                item for item in items
                if any(
                    kw in item.get("headline", "").upper()
                    for kw in related
                )
            ]
            # Fallback: primeras noticias disponibles
            if not relevant:
                relevant = items[:limit]

            result = []
            for item in relevant[:limit]:
                ts = item.get("datetime", 0)
                dt = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None
                result.append({
                    "headline": item.get("headline", ""),
                    "source":   item.get("source", ""),
                    "datetime": dt,
                    "url":      item.get("url", ""),
                    "sentiment": "",
                })
            return result

        except Exception:
            return []

    # =========================================================================
    # HELPERS PRIVADOS
    # =========================================================================

    @staticmethod
    def _parse_event_time(time_str: str, date_str: str):
        """Parsea el tiempo del evento en UTC."""
        if not time_str:
            return None
        try:
            if len(time_str) <= 5 and ":" in time_str:
                dt_str = f"{date_str}T{time_str}:00Z"
                return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(time_str, fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        except Exception:
            pass
        return None
