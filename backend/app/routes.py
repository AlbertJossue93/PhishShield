from flask import Blueprint, request, jsonify
from datetime import datetime
from app.advanced_analyzer import AdvancedURLAnalyzer  # Importa a classe correta

bp = Blueprint("routes", __name__)

@bp.route("/api/check", methods=["POST"])
def check():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados JSON são obrigatórios"}), 400

        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL é obrigatória"}), 400

        # Timeout mantido para compatibilidade futura
        timeout = data.get("timeout", 10)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            return jsonify({"error": "Timeout deve ser um número positivo"}), 400

        analyzer = AdvancedURLAnalyzer(url)  # Usa AdvancedURLAnalyzer
        resultado = analyzer.analyze()

        return jsonify({
            **resultado,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": f"Falha ao analisar a URL: {str(e)}"}), 500