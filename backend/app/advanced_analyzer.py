from app.sanitizer import sanitize_url, is_long_url
from urllib.parse import urlparse
import tldextract
from difflib import SequenceMatcher
from app.analyzer import URL_Analyzer

class AdvancedURLAnalyzer(URL_Analyzer):
    def __init__(self, url: str):
        sanitized = sanitize_url(url, keep_path=True)
        if not sanitized:
            raise ValueError("URL inválida")
        super().__init__(sanitized)
        self.subdomain_count = 0
        # Garanta que existam
        self.score = getattr(self, 'score', 0)
        self.feedback = getattr(self, 'feedback', [])
 
        # Configurações
        self.known_brands = {
            'paypal.com', 'google.com', 'gmail.com', 'facebook.com', 'instagram.com',
            'apple.com', 'microsoft.com', 'amazon.com', 'netflix.com', 'spotify.com',
            'nubank.com.br', 'itau.com.br', 'bradesco.com.br', 'caixa.gov.br',
            'bancodobrasil.com.br', 'santander.com.br', 'mercadolivre.com.br'
        }
        self.suspicious_tlds = {
            '.xyz', '.top', '.club', '.online', '.site', '.info', '.work',
            '.cfd', '.cam', '.rest', '.monster', '.quest', '.bond', '.lat'
        }
        self.phishing_keywords = {
            'login', 'secure', 'verify', 'account', 'update', 'password',
            'reset', 'auth', 'signin', 'sign-in', 'banking', 'payment',
            'confirm', 'access', 'session', 'recover', 'support'
        }
    def has_homograph(self, domain:str) -> bool:
        return any(ord(chard) > 127 for chard in  domain)
    

    def check_typosquatting(self):
        try:
            domain =  urlparse(self.url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]


            for brand in self.known_brands:
                if SequenceMatcher(None, domain, brand).ratio() > 0.8 and domain != brand:
                    self.score +=2
                    self.feedback.append(f"DOMINIO SIMILAR A UNA MARCA CONHECIDA: {brand}")
                    return

        except: pass

    def check_homograph(self):
            try:
                domain = urlparse(self.url).netloc
                if self.has_homograph(domain):
                    self.score += 2
                    self.feedback.append("DOMÍNIO COM CARACTERES SUSPEITOS")
            except: pass

    def check_suspicious_tld(self):
        try:
            extracted = tldextract.extract(self.url)
            tld = f".{extracted.suffix.split('.')[-1]}"
            if tld in self.suspicious_tlds:
                self.score += 1
                self.feedback.append(f"TLD suspeito: {tld} (comum em phishing)")
        except: pass

    def check_phishing_path(self):
        try:
            path = urlparse(self.url).path.lower()
            for keyword in self.phishing_keywords:
                if keyword in path:
                    self.score += 1
                    self.feedback.append(f"Palavra-chave de phishing no caminho: '{keyword}'")
                    break  # só conta uma vez
        except: pass

    def check_subdomains(self):
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
                self.feedback.append(f"⚠️ Um subdomínio incomum: {subdomains_suspeitos[0]}")
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
        Executa a análise avançada de URL, aproveitando as regras básicas da classe
        base (`URL_Analyzer`) e adicionando checagens extras de phishing.
        """
        # Sanitiza novamente por segurança (caso a instância seja reutilizada)
        self.url = sanitize_url(self.url, keep_path=True)
        if not self.url:
            self.score += 1
            self.feedback.append("URL inválida após sanitização")
            return {
                "resultado": {
                    "status": self.get_status(),
                    "score": self.score,
                    "feedback": self.feedback,
                    "subdominios": self.subdomain_count,
                },
                "url_analisada": "",
            }

        # Regras básicas (HTTPS, tamanho, hífen, etc.)
        super().analyze()

        # Regras avançadas
        if is_long_url(self.url):
            self.score += 1
            self.feedback.append("URL muito longa, possivelmente maliciosa")
        else:
            self.check_subdomains()
            self.check_typosquatting()
            self.check_homograph()
            self.check_suspicious_tld()
            self.check_phishing_path()

        return {
            "resultado": {
                "status": self.get_status(),
                "score": self.score,
                "feedback": self.feedback,
                "subdominios": self.subdomain_count,
            },
            "url_analisada": self.url,
        }



   


