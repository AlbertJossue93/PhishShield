from urllib.parse import urlparse
import tldextract
from app.analyzer import URL_Analyzer # Assumindo que URL_Analyzer está no mesmo pacote

class AdvancedURLAnalyzer(URL_Analyzer):
    def __init__(self, url):
        super().__init__(url)  # reaproveita construtor da classe base
        # Inicializa o atributo que será usado e retornado,  ASSIM evitando AttributeError
        self.subdomain_count = 0 

    def check_subdomains(self):
        """Verifica subdomínios suspeitos usando tldextract"""
        try:
            parsed_url = urlparse(self.url)
            if not parsed_url.hostname:
                self.feedback.append("❌ Sem hostname para analisar subdomínios")
                return  

            extracted = tldextract.extract(self.url)
            common_subdomains = [
                'www', 'mail', 'ftp', 'blog', 'shop', 'store', 'login', # 'login' adicionado
                'support', 'ajuda', 'help', 'api', 'cdn', 'dev', 'test',
                'm', 'mobile', 'app', 'panel', 'painel', 'admin',
                'secure', 'sso', 'br', 'us', 'uk', 'es', 'fr', 'staging', 
                'preprod', 'teste', 'sistema', 'portal' # Adicionei alguns subdomínios comuns de ambiente/sistema
            ]

            subdomains = extracted.subdomain.split('.') if extracted.subdomain else []
            subdomains_suspeitos = [sub for sub in subdomains if sub not in common_subdomains]
            self.subdomain_count = len(subdomains_suspeitos)

            if self.subdomain_count > 2:
                self.score += 2
                self.feedback.append(f"⚠️ Muitos subdomínios suspeitos ({self.subdomain_count}): {', '.join(subdomains_suspeitos)}")
            elif self.subdomain_count == 2:
                self.score += 1
                self.feedback.append(f"⚠️ Dois subdomínios suspeitos: {', '.join(subdomains_suspeitos)}")
            elif self.subdomain_count == 1:
                self.feedback.append(f"⚠️ Um subdomínio incomum, mas pode ser nome de plataform: {subdomains_suspeitos[0]}")
            else:
                if subdomains:
                    self.feedback.append(f"✅ Apenas subdomínios comuns: {', '.join(subdomains)}")
                else:
                    self.feedback.append("✅ Sem subdomínios")

        except Exception as e:
            self.feedback.append(f"❌ Erro ao analisar subdomínios: {str(e)}")

    def analyze(self):
        """Executa verificações da classe base e adiciona análise de subdomínios"""
        super().analyze()  # Chama analyze da classe base
        self.check_subdomains()

        return {
            "resultado": {
                "status": self.get_status(),
                "score": self.score,
                "feedback": self.feedback,
                "subdomain_count": self.subdomain_count  # Campo renomeado
            },
            "url_analisada": self.url
        }