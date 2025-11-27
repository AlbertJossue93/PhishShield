from flask import Blueprint, request, jsonify
from datetime import datetime
from app.advanced_analyzer import AdvancedURLAnalyzer
from app.sanitizer import sanitize_url  

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

        #Sanitização backend – usando sua função existente
        sanitized_url = sanitize_url(url)
        if not sanitized_url:
            return jsonify({"error": "URL contém caracteres inválidos"}), 400

        timeout = data.get("timeout", 10)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            return jsonify({"error": "Timeout deve ser um número positivo"}), 400

        # Usa a URL já sanitizada
        analyzer = AdvancedURLAnalyzer(sanitized_url)
        resultado = analyzer.analyze()

        return jsonify({
            **resultado,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": f"Falha ao analisar a URL: {str(e)}"}), 500
