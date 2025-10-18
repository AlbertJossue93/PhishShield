from urllib.parse import urlparse
import re
class URL_Analyzer:
    def __init__(self, url):
        self.url = url.strip() if isinstance(url, str) else ""
        self.score = 0
        self.feedback = []

    def check_https_and_ssl(self):
        """Verifica se a URL usa HTTPS e analisa padrões suspeitos"""
        if not self.url:
            self.score += 1
            self.feedback.append("URL inválida ou vazia")
            return

        parsed_url = urlparse(self.url)
        scheme = parsed_url.scheme.lower()
        netloc = parsed_url.netloc

        #  Validação inicial
        if not scheme or not netloc:
            self.score += 1
            self.feedback.append("URL malformada (sem protocolo ou domínio)")
            return

        # Checa protocolo HTTPS
        if scheme != "https":
            self.score += 1
            self.feedback.append(f"❌ URL não usa HTTPS (esquema: {scheme or 'nenhum'})")
        else:
            self.feedback.append("✅ URL usa HTTPS")

        # Padrões suspeitos com feedback específico
        suspicious_patterns = [
            (re.search(r'@', self.url), "⚠️ Presença de '@' (técnica de phishing)"),
            (re.search(r'//.*//', self.url), "⚠️ Múltiplos '//' (ofuscação)"),
            (re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', netloc), "⚠️ Domínio usa endereço IP"),
            (re.search(r'(?:\%25|%[0-9a-fA-F]{2})', self.url), "⚠️ Codificação suspeita (ex.: %25)"),
            (any(keyword in self.url.lower() for keyword in ['login', 'secure', 'bank', 'update', 'confirm']), 
             "⚠️ Palavras associadas a phishing detectadas")
        ]
        
        for pattern, message in suspicious_patterns:
            if pattern:
                self.score += 1
                self.feedback.append(message)
       

   
   
    def check_length(self):
        if len(self.url) > 100:
            self.score += 2
            self.feedback.append("URL muito longa")
        elif len(self.url) > 50:
            self.score += 1
            self.feedback.append("URL relativamente longa")
        else:
            self.feedback.append("URL de tamanho normal")

    def check_hifen(self):
        if "-" in self.url:
            self.score += 1
            self.feedback.append("URL contém hífen")

    def get_status(self):
        if self.score == 0:
            return "Seguro"
        elif self.score <= 2:
            return "Suspeito" 
        else:
            return "Perigoso"

    def analyze(self):
        self.check_https_and_ssl()
        self.check_length()
        self.check_hifen()
        


        # Estrutura compatível com o popup.js
        return {
            "resultado": {
                "status": self.get_status(),
                "score": self.score,
                "feedback": self.feedback
            },
            "url_analisada": self.url
        }