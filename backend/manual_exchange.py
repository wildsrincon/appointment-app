#!/usr/bin/env python3
"""
Intercambio manual de código por refresh token
"""

import urllib.parse
import urllib.request
import json

# Configura tus datos
CLIENT_ID = "TU_CLIENT_ID_AQUI"
CLIENT_SECRET = "TU_CLIENT_SECRET_AQUI"

def exchange_code_for_refresh_token(auth_code):
    """Intercambia código de autorización por refresh token"""

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost'  # Importante: debe coincidir
    }

    try:
        # Codificar datos
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')

        # Crear solicitud
        req = urllib.request.Request(
            'https://oauth2.googleapis.com/token',
            data=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        # Enviar solicitud
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result

    except Exception as e:
        return {'error': str(e)}

def main():
    print("🔑 INTERCAMBIO MANUAL - CÓDIGO POR REFRESH TOKEN")
    print("=" * 50)

    if CLIENT_ID == "TU_CLIENT_ID_AQUI":
        print("❌ Configura CLIENT_ID y CLIENT_SECRET en el script")
        return

    # Obtener código del usuario
    auth_code = input("\n📝 Pega aquí el código de autorización (todo después de 'code='): ").strip()

    if not auth_code:
        print("❌ No se proporcionó código")
        return

    print(f"\n🔄 Intercambiando código por refresh token...")

    # Intercambiar código
    result = exchange_code_for_refresh_token(auth_code)

    if 'refresh_token' in result:
        print(f"\n🎉 ¡ÉXITO!")
        print(f"\n🔑 REFRESH TOKEN:")
        print(f"{result['refresh_token']}")

        # Crear configuración para .env
        env_config = f"""
# Google Calendar Configuration
GOOGLE_CALENDAR_CLIENT_ID={CLIENT_ID}
GOOGLE_CALENDAR_CLIENT_SECRET={CLIENT_SECRET}
GOOGLE_CALENDAR_REFRESH_TOKEN={result['refresh_token']}
"""

        # Guardar en archivo
        with open('google_config.txt', 'w') as f:
            f.write(env_config)

        print(f"\n📁 Configuración guardada en: google_config.txt")
        print(f"✅ Ahora puedes copiar GOOGLE_CALENDAR_REFRESH_TOKEN a tu archivo .env")

    else:
        print(f"\n❌ Error en el intercambio:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()