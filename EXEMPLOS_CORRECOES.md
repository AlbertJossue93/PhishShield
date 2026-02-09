# 🔧 Exemplos Práticos de Correções

## 1. 🔴 BUG CRÍTICO - `advanced_analyzer.py` Linha 42

### ❌ Código Atual (ERRADO)
```python
if domain.startswith('www.'):
    domain = domain[4]  # ❌ Isso retorna apenas 1 caractere!
```

### ✅ Código Corrigido
```python
if domain.startswith('www.'):
    domain = domain[4:]  # ✅ Remove 'www.' corretamente
```

---

## 2. 🔴 BUG CRÍTICO - `advanced_analyzer.py` Linha 56

### ❌ Código Atual (ERRADO)
```python
def check_homograph(self):
    try:
        domain = urlparse(self.url).netloc
        if self.contains_homograph(domain):  # ❌ Método não existe!
            self.score += 2
            self.feedback.append("DOMÍNIO COM CARACTERES SUSPEITOS")
    except: pass
```

### ✅ Código Corrigido
```python
def check_homograph(self):
    try:
        domain = urlparse(self.url).netloc
        if self.has_homograph(domain):  # ✅ Método correto
            self.score += 2
            self.feedback.append("DOMÍNIO COM CARACTERES SUSPEITOS")
    except Exception as e:
        # Log do erro ao invés de ignorar silenciosamente
        pass
```

---

## 3. 🔴 BUG - Retorno de Métodos em `analyze()`

### ❌ Código Atual (ERRADO)
```python
return {
    "resultado": {
        "status": self.get_status(),
        "score": self.score,
        "feedback": self.feedback,
        "subdominios": self.subdomain_count,
        "homografos": self.check_homograph(),  # ❌ Retorna None
        "Topo de domínio suspeito": self.check_suspicious_tld(),  # ❌ Retorna None
        "typosquatting": self.check_typosquatting()  # ❌ Retorna None
    },
    "url_analisada": self.url
}
```

### ✅ Código Corrigido
```python
# Opção 1: Remover (recomendado, pois já está no feedback)
return {
    "resultado": {
        "status": self.get_status(),
        "score": self.score,
        "feedback": self.feedback,
        "subdominios": self.subdomain_count
    },
    "url_analisada": self.url
}

# Opção 2: Criar flags booleanas
has_homograph = self.has_homograph(urlparse(self.url).netloc)
has_suspicious_tld = self.check_suspicious_tld()  # Modificar para retornar bool
has_typosquatting = self.check_typosquatting()  # Modificar para retornar bool

return {
    "resultado": {
        "status": self.get_status(),
        "score": self.score,
        "feedback": self.feedback,
        "subdominios": self.subdomain_count,
        "homografos": has_homograph,
        "tld_suspeito": has_suspicious_tld,
        "typosquatting": has_typosquatting
    },
    "url_analisada": self.url
}
```

---

## 4. 🔒 SEGURANÇA - CORS Configuração

### ❌ Código Atual (PERIGOSO)
```python
# __init__.py
CORS(app, resources={r"/api/*": {"origins": "*"}})  # ❌ Permite qualquer origem
```

### ✅ Código Corrigido
```python
# __init__.py
import os

# Em desenvolvimento, permite localhost e extensões Chrome
# Em produção, apenas extensões Chrome
allowed_origins = [
    "chrome-extension://*",
    "http://localhost:*",
    "http://127.0.0.1:*"
]

if os.getenv('FLASK_ENV') == 'development':
    allowed_origins.append("*")  # Apenas em dev

CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})
```

---

## 5. 🔒 SEGURANÇA - DEBUG Mode

### ❌ Código Atual (PERIGOSO)
```python
# __init__.py
app.config['DEBUG'] = True  # ❌ Sempre True
```

### ✅ Código Corrigido
```python
# __init__.py
import os

app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
app.config['TESTING'] = os.getenv('FLASK_TESTING', 'False').lower() == 'true'
```

E criar `.env.example`:
```bash
# .env.example
FLASK_DEBUG=False
FLASK_ENV=production
FLASK_TESTING=False
API_URL=http://127.0.0.1:5000
```

---

## 6. 📝 LOGGING - Substituir print()

### ❌ Código Atual
```python
# sanitizer.py
except Exception as e:
    print(f"Erro sanitização: {e}")  # ❌ print() não é adequado
    return ""
```

### ✅ Código Corrigido
```python
# sanitizer.py
import logging

logger = logging.getLogger(__name__)

def sanitize_url(url: str, keep_path: bool = True, keep_query: bool = True) -> str:
    try:
        # ... código existente ...
    except Exception as e:
        logger.error(f"Erro na sanitização de URL: {e}", exc_info=True)
        return ""
```

E configurar logging no `__init__.py`:
```python
# __init__.py
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    
    # Configurar logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/phishshield.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('PhishShield startup')
    
    # ... resto do código ...
```

---

## 7. 🎯 VALIDAÇÃO - Usar Pydantic

### ❌ Código Atual
```python
# routes.py
data = request.get_json()
url = data.get("url", "").strip()
if not url:
    return jsonify({"error": "URL é obrigatória"}), 400

timeout = data.get("timeout", 10)
if not isinstance(timeout, (int, float)) or timeout <= 0:
    return jsonify({"error": "Timeout deve ser um número positivo"}), 400
```

### ✅ Código Corrigido (com Pydantic)

Primeiro, adicionar ao `requirements.txt`:
```
pydantic>=2.0.0
```

Depois, criar `app/schemas.py`:
```python
# app/schemas.py
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional

class URLCheckRequest(BaseModel):
    url: str
    timeout: Optional[int] = 10
    
    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL é obrigatória')
        return v.strip()
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v is not None and (not isinstance(v, (int, float)) or v <= 0 or v > 60):
            raise ValueError('Timeout deve ser um número entre 1 e 60 segundos')
        return v
```

E usar em `routes.py`:
```python
# routes.py
from app.schemas import URLCheckRequest
from pydantic import ValidationError

@bp.route("/api/check", methods=["POST"])
def check():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados JSON são obrigatórios"}), 400
        
        # Validação automática com Pydantic
        request_data = URLCheckRequest(**data)
        
        sanitized_url = sanitize_url(request_data.url)
        if not sanitized_url:
            return jsonify({"error": "URL contém caracteres inválidos"}), 400
        
        analyzer = AdvancedURLAnalyzer(sanitized_url)
        resultado = analyzer.analyze()
        
        return jsonify({
            **resultado,
            "timestamp": datetime.now().isoformat()
        })
    
    except ValidationError as e:
        return jsonify({
            "error": "Dados inválidos",
            "details": e.errors()
        }), 400
    except Exception as e:
        app.logger.exception("Erro ao analisar URL")
        return jsonify({"error": f"Falha ao analisar a URL: {str(e)}"}), 500
```

---

## 8. 🧪 TESTES - Exemplo Básico

Criar `tests/` e `tests/test_sanitizer.py`:
```python
# tests/test_sanitizer.py
import pytest
from app.sanitizer import sanitize_url, is_long_url

def test_sanitize_url_valid():
    assert sanitize_url("https://example.com") == "https://example.com"

def test_sanitize_url_adds_https():
    assert sanitize_url("example.com") == "https://example.com"

def test_sanitize_url_removes_javascript():
    assert sanitize_url("javascript:alert(1)") == ""

def test_sanitize_url_empty():
    assert sanitize_url("") == ""

def test_is_long_url():
    assert is_long_url("https://example.com/" + "a" * 300) == True
    assert is_long_url("https://example.com") == False
```

E `tests/test_analyzer.py`:
```python
# tests/test_analyzer.py
import pytest
from app.analyzer import URL_Analyzer

def test_analyzer_https():
    analyzer = URL_Analyzer("https://example.com")
    analyzer.check_https_and_ssl()
    assert "✅ URL usa HTTPS" in analyzer.feedback
    assert analyzer.score == 0

def test_analyzer_http():
    analyzer = URL_Analyzer("http://example.com")
    analyzer.check_https_and_ssl()
    assert "❌ URL não usa HTTPS" in analyzer.feedback
    assert analyzer.score > 0
```

Adicionar ao `requirements.txt`:
```
pytest>=7.0.0
pytest-cov>=4.0.0
```

---

## 9. 📚 README.md - Exemplo Básico

```markdown
# 🛡️ PhishShield

Detector de URLs maliciosas e phishing usando análise heurística.

## 🚀 Instalação

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r app/requirements.txt
```

### Extensão Chrome
1. Abra `chrome://extensions/`
2. Ative "Modo do desenvolvedor"
3. Clique em "Carregar sem compactação"
4. Selecione a pasta `extension/`

## 🏃 Uso

### Iniciar Backend
```bash
cd backend
python run.py
```

### Usar Extensão
1. Clique no ícone da extensão
2. Digite a URL para analisar
3. Clique em "Analisar URL"

## 🧪 Testes
```bash
pytest tests/ -v
```

## 📝 Licença
MIT
```

---

## 10. 🐳 Docker - Dockerfile Básico

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY backend/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

E `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    volumes:
      - ./logs:/app/logs
```

---

## ✅ Checklist de Implementação

Use estes exemplos como referência para implementar as melhorias:

- [ ] Corrigir bug linha 42 (`domain[4]` → `domain[4:]`)
- [ ] Corrigir bug linha 56 (`contains_homograph` → `has_homograph`)
- [ ] Corrigir retorno de métodos em `analyze()`
- [ ] Configurar CORS adequadamente
- [ ] Usar variáveis de ambiente para DEBUG
- [ ] Implementar logging estruturado
- [ ] Adicionar validação com Pydantic (opcional mas recomendado)
- [ ] Criar testes básicos
- [ ] Criar README.md
- [ ] Dockerizar (opcional)

---

**Boa sorte com as implementações! 🚀**
