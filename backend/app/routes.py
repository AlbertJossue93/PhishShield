from flask import Blueprint, request, jsonify
from app.advanced_analyzer import AdvancedURLAnalyzer

bp = Blueprint("routes", __name__)

@bp.route("/api/check", methods=["POST"])
def check():
    data = request.get_json()
    
    # Verificar se data não é None
    if not data:
        return jsonify({"error": "Dados JSON são obrigatórios"}), 400
        
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL é obrigatória"}), 400
    
    try:
        analyzer = AdvancedURLAnalyzer(url)
        resultado = analyzer.analyze()
        
        return jsonify(resultado)
        
    except Exception as e:
        # CORREÇÃO: Removendo o 'e' extra do retorno 500
        return jsonify({"error": f"Erro ao analisar URL: {str(e)}"}), 500 