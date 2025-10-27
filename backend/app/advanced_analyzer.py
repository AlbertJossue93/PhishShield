from app.sanitizer import sanitize_url, is_long_url
from urllib.parse import urlparse
import tldextract
from app.analyzer import URL_Analyzer

class AdvancedURLAnalyzer(URL_Analyzer):
    def __init__(self, url: str):
        """
        Inicializa o analisador de URLs avançado com uma URL sanitizada.
        
        Args:
            url (str): URL a ser analisada.
        """
        sanitized_url = sanitize_url(url, keep_path=False)
        if not sanitized_url:
            raise ValueError("URL inválida após sanitização")
        super().__init__(sanitized_url)
        self.subdomain_count = 0

    def check_subdomains(self):
        """
        Verifica subdomínios suspeitos usando tldextract.
        Atualiza o score e feedback com base na análise.
        """
        try:
            parsed_url = urlparse(self.url)
            if not parsed_url.hostname:
                self.feedback.append("❌ Sem hostname para analisar subdomínios")
                return

            extracted = tldextract.extract(self.url)
            common_subdomains = {
                'www', 'mail', 'ftp', 'blog', 'shop', 'store', 'login',
                'support', 'ajuda', 'help', 'api', 'cdn', 'dev', 'test',
                'm', 'mobile', 'app', 'panel', 'painel', 'admin',
                'secure', 'sso', 'br', 'us', 'uk', 'es', 'fr', 'staging',
                'preprod', 'teste', 'sistema', 'portal'
            }

            subdomains = extracted.subdomain.split('.') if extracted.subdomain else []
            subdomains_suspeitos = [sub for sub in subdomains if sub.lower() not in common_subdomains]
            self.subdomain_count = len(subdomains_suspeitos)

            if self.subdomain_count > 2:
                self.score += 2
                self.feedback.append(
                    f"⚠️ Muitos subdomínios suspeitos ({self.subdomain_count}): {', '.join(subdomains_suspeitos)}"
                )
            elif self.subdomain_count == 2:
                self.score += 1
                self.feedback.append(f"⚠️ Dois subdomínios suspeitos: {', '.join(subdomains_suspeitos)}")
            elif self.subdomain_count == 1:
                self.feedback.append(f"⚠️ Um subdomínio incomum, mas pode ser nome de plataforma: {subdomains_suspeitos[0]}")
            else:
                if subdomains:
                    self.feedback.append(f"✅ Apenas subdomínios comuns: {', '.join(subdomains)}")
                else:
                    self.feedback.append("✅ Sem subdomínios")

        except Exception as e:
            self.feedback.append(f"❌ Erro ao analisar subdomínios: {str(e)}")
            self.score += 1

    def analyze(self):
        """
        Executa a análise completa da URL sanitizada, incluindo verificações da classe base e subdomínios.
        
        Returns:
            dict: Resultado da análise com status, score, feedback e contagem de subdomínios.
        """
        self.url = sanitize_url(self.url, keep_path=False)
        if not self.url:
            self.feedback.append("❌ URL inválida após sanitização")
            return {
                "resultado": {
                    "status": "inválido",
                    "score": self.score,
                    "feedback": self.feedback,
                    "subdomain_count": self.subdomain_count
                },
                "url_analisada": self.url
            }

        # Verifica se a URL sanitizada é longa
        if is_long_url(self.url):
            self.score += 1
            self.feedback.append("⚠️ URL muito longa, possivelmente maliciosa")

        # Chama a análise da classe base
        super().analyze()

        # Analisa subdomínios
        self.check_subdomains()

        return {
            "resultado": {
                "status": self.get_status(),
                "score": self.score,
                "feedback": self.feedback,
                "subdomain_count": self.subdomain_count
            },
            "url_analisada": self.url
        }