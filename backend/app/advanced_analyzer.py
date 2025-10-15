from urllib.parse import urlparse
import tldextract
from app.analyzer import URL_Analyzer # Assumindo que URL_Analyzer está no mesmo pacote

class AdvancedURLAnalyzer(URL_Analyzer):
    def __init__(self, url):
        super().__init__(url)  # reaproveita construtor da classe base
        # Inicializa o atributo que será usado e retornado,  ASSIM evitando AttributeError
        self.subdomain_count = 0 

    def check_subdomains(self):
        
        try:
            parsed_url = urlparse(self.url)
            domains_parts = parsed_url.hostname.split('.')
            extracted = tldextract.extract(self.url)

            common_subdomains = [
    'www', 'mail', 'ftp', 'blog', 'shop', 'store', 
    'support', 'ajuda', 'help',      # Suporte e Ajuda
    'api', 'cdn', 'dev', 'test',     # Técnico e Infraestrutura
    'm', 'mobile',                   # Móvel
    'app', 'panel', 'painel', 'admin', # Aplicações e Painéis
    'secure', 'sso',                 # Segurança e Login Único
    'br', 'us', 'uk', 'es', 'fr'     # Localização (códigos de país comuns)
                                  ]
                    
            subdomains = extracted.subdomain.split('.') if extracted.subdomain else []
            
            subdomains_suspeitos = [sub for sub in subdomains if sub not in common_subdomains]

            self.subdomain_count = len(subdomains_suspeitos)
            total_subdomains = len(subdomains)
            
            if self.subdomain_count > 2:
                self.score +=2
                self.feedback.append("Muitos subdomínios (possível ofuscação).")
    
            elif self.subdomain_count == 2: 
                self.score +=1
                self.feedback.append(f"Dois subdomínios suspeitos ({', '.join(subdomains_suspeitos)})")
            elif self.subdomain_count == 1:
                self.feedback.append("Um subdominio presente")
            else:
                if total_subdomains > 0:
                    self.feedback.append(f"Apenas subdominios comuns({', '.join(subdomains)})")
        
        except Exception as e:
            self.feedback.append(f"Erro ao analisar os subdomínios: {str(e)}")


    def analyze(self):
        #Adicionando parênteses para chamar o método da classe pai
        super().analyze() 
        
        self.check_subdomains() 

        #Retorna resultado atualizado
        return {
            "resultado": {
                "status": self.get_status(),
                "score": self.score,
                "feedback": self.feedback,
                "subdominio ": self.subdomain_count 
            },
            "url_analisada": self.url
        }