class URL_Analyzer:
    def __init__(self, url):
        self.url = url
        self.score = 0
        self.feedback = []

    def check_http(self):
        if not self.url.startswith("https"):
            self.score += 1
            self.feedback.append("URL não usa HTTPS")
        else:
            self.feedback.append("URL usa HTTPS corretamente")

   
   
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
        self.check_http()
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