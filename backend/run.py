import os
from app import create_app  # Importa a FUNÇÃO create_app

app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", "5000"))

    print(f"🚀 Servidor iniciando na porta {port} (debug={debug})...")
    app.run(host="0.0.0.0", port=port, debug=debug)