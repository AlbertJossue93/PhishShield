from urllib.parse import urlparse, urlunparse
import re

def sanitize_url(url: str, keep_path: bool = False) -> str:
    """
    Sanitiza uma URL, normalizando o formato, removendo parâmetros desnecessários e, opcionalmente, o caminho.
    
    Args:
        url (str): URL a ser sanitizada.
        keep_path (bool): Se True, mantém o caminho; se False, remove o caminho (padrão: False).
        
    Returns:
        str: URL sanitizada ou string vazia se inválida.
    """
    try:
        # Remove espaços em branco e caracteres de controle
        url = url.strip()
        if not url:
            return ""

        # Adiciona esquema 'https://' se não houver um esquema válido
        if not re.match(r'^[a-zA-Z]+://', url, re.IGNORECASE):
            url = 'https://' + url

        # Faz o parse da URL
        parsed = urlparse(url)

        # Verifica se o hostname é válido
        if not parsed.netloc or not re.match(
            r'^[a-zA-Z0-9][a-zA-Z0-9\-]*(?:\.[a-zA-Z0-9\-]+)+$', 
            parsed.netloc, 
            re.IGNORECASE
        ):
            return ""
        path = parsed.path.rstrip('/') if keep_path else ''

        # Reconstrói a URL sem params, query ou fragment
        clean_parts = (
            parsed.scheme.lower() if parsed.scheme in ['http', 'https'] else 'https',
            parsed.netloc.lower(),
            path,
            '',  # params
            '',  # query
            ''   # fragment
        )

        # Codifica caracteres especiais e remove caracteres indesejados
        clean_url = urlunparse(clean_parts)
        clean_url = re.sub(r'[^\w\-./?=&%:@]', '', clean_url)

        # Verifica se a URL resultante é válida
        if not clean_url or len(clean_url) < 8:  # Mínimo razoável (ex.: https://a.b)
            return ""

        return clean_url

    except Exception:
        return ""

def is_long_url(url: str, limit: int = 200) -> bool:
    """
    Verifica se a URL sanitizada excede o limite de comprimento, indicando possível malícia.
    
    Args:
        url (str): URL a ser verificada.
        limit (int): Limite de comprimento (padrão: 200).
        
    Returns:
        bool: True se a URL sanitizada for longa, False caso contrário.
    """
    try:
        sanitized_url = sanitize_url(url, keep_path=False)
        if not sanitized_url:
            return False
        return len(sanitized_url) > limit or url.count('&') > 5
    except Exception:
        return False