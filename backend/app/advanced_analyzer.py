from urllib.parse import urlparse
from app.analyzer import URL_Analyzer # Assumindo que URL_Analyzer está no mesmo pacote

class AdvancedURLAnalyzer(URL_Analyzer):
    def __init__(self, url):
        super().__init__(url)  # reaproveita construtor da classe base
        # Inicializa o atributo que será usado e retornado, evitando AttributeError
        self.subdomain_count = 0 

    def check_subdomains(self):
        
        try:
            parsed_url = urlparse(self.url)
            domains_parts = parsed_url.hostname.split('.') 

            # CORREÇÃO: Usando consistentemente self.subdomain_count
            # Ex: www.google.com -> 3 partes. O domínio base e TLD são 2.
            # O número de subdomínios é a contagem de partes - 2 (base + tld).
            self.subdomain_count = len(domains_parts) - 2 

            if self.subdomain_count > 2:
                self.score +=2
                self.feedback.append("Muitos subdomínios (possível ofuscação).")
                
            # Usando consistentemente self.subdomain_count
            elif self.subdomain_count > 0: # Corrigindo para > 0, pois > 1 já é pego acima.
                self.score +=1
                self.feedback.append("Subdomínios presentes.")
            else:
                self.feedback.append("Número normal de subdomínios.")
        
        except Exception as e:
            self.feedback.append(f"Erro ao analisar os subdomínios: {str(e)}")


    def analyze(self):
        # CORREÇÃO: Adicionando parênteses para chamar o método da classe pai
        super().analyze() 
        
        self.check_subdomains() 

        #Retorna resultado atualizado
        return {
            "resultado": {
                "status": self.get_status(),
                "score": self.score,
                "feedback": self.feedback,
                "subdomain_count": self.subdomain_count 
            },
            "url_analisada": self.url
        }