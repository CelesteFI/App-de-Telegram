# 08. Seguridad: validación de `initData`

> Regla #1 de las Mini Apps: **NUNCA confiar** en `initDataUnsafe` (el objeto
> parseado en el navegador). El usuario puede manipularlo. Toda decisión
> importante (identidad, pagos, privilegios) debe validarse en el backend.

## 8.1 Por qué importa

La Mini App corre en el navegador del usuario y recibe `window.Telegram.WebApp.initData`,
una cadena de pares `clave=valor` que Telegram firma. Cualquiera puede abrir la
URL en un navegador y falsificar datos. Por eso:

1. Usa `initData` (crudo) para validar.
2. Solo después de validar, USA los valores en tu servidor.
3. Nunca tomes decisiones con `initDataUnsafe`.

## 8.2 Validación HMAC-SHA256 (método clásico)

El token del bot es el secreto compartido:

```
secret_key = HMAC_SHA256(clave = "WebAppData", mensaje = <BOT_TOKEN>)
en hex

data_check_string = todas las claves ordenadas alfabéticamente
                    como "clave=valor" unidas con "\n"
                    (sin el campo hash)

hash_calculado = hex( HMAC_SHA256(clave = secret_key,
                                  mensaje = data_check_string) )

VÁLIDO  si  hash_calculado == initData["hash"]
```

Ejemplo en Python (con la librería estándar):

```python
import hashlib, hmac, urllib.parse

def validate_init_data(token: str, init_data: str, max_age: int = 86400) -> dict | None:
    """Devuelve dict con los datos si son válidos, o None."""
    params = dict(urllib.parse.parse_qsl(init_data, strict_parsing=True))
    if "hash" not in params:
        return None
    received_hash = params.pop("hash")

    # data-check-string: pares ordenados alfabéticamente, unidos por \n
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )

    secret_key = hmac.new(key=b"WebAppData", msg=token.encode(),
                          digestmod=hashlib.sha256).digest()
    computed = hmac.new(key=secret_key, msg=data_check_string.encode(),
                        digestmod=hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, received_hash):
        return None

    # (opcional) verificar frescura: auth_date no debe ser viejo
    import time
    if int(params.get("auth_date", 0)) < time.time() - max_age:
        return None
    return params
```

> Algunas librerías ya lo hacen: `aiogram.utils.web_app.check_webapp_signature`.

## 8.3 Validación por terceros (Ed25519, Bot API 8.0+)

Si alguien más (un SDK, un build externo) valida datos **sin conocer tu token**:

- `initData` incluye ahora `signature`, una firma **Ed25519 base64url** del
  data-check-string `bot_id:WebAppData\nauth_date=...\nuser=...\n...`.
- Llaves públicas de Telegram:
  - **Test:** `40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec`
  - **Producción:** `e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d`

## 8.4 Buenas prácticas

| Práctica | Detalle |
|---|---|
| Validar en el backend | No validar solo en JS del navegador |
| Verificar `auth_date` | Rechazar datos viejos (por ejemplo, >24 h) |
| HTTPS siempre en producción | El token viaja en la web; nunca exponer el token del bot en la Mini App / frontend |
| No configurar el bot token en el frontend | Un `VITE_BOT_TOKEN` / variable de cliente queda pública — guardar el token solo en el servidor |
| CORS restringido | Si haces API, permitir solo tu origen |
| Límites | `sendData` max. **4096 bytes**; validar tamaño e inyectar datos con cuidado (es texto JSON) |
| Pagos | Esperar `successful_payment` antes de entregar bienes (nunca confiar en el `pre_checkout_query`) |

## 8.5 Ejemplo de flujo completo (Mini App → bot)

```
[Telegram]  --abre--->  Mini App (HTTPS)
   |  initData firmada con el token del bot
   v
Mini App (frontend)  --(initData + acción)-->  Bot backend (FastAPI/Flask)
   |  validate_init_data(token, initData)  -> OK/FAIL
   v
Backend: usa user.id, start_param, query_id  -> responde / llama al RAG
```

## 8.6 Nota extra: no dar de alta tu token en el repositorio

- Usar variables de entorno (`$env:BOT_TOKEN`/`.env`).
- No subir `.env` ni `token` al git.
- Si se filtra un token: en `@BotFather` → `/revoke` y crear uno nuevo.