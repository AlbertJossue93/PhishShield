from urllib.parse import urlparse, urlunparse, quote
import re
import logging

logger = logging.getLogger(__name__)

def sanitize_url(url: str, keep_path: bool = True, keep_query: bool = True) -> str:
    """
    Sanitiza URL mantendo caminho e query, com codificação correta via quote().
    """
    try:
        url = url.strip()
        if not url:
            return ""

        # Adiciona esquema se faltar
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url, re.IGNORECASE):
            url = 'https://' + url

        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return ""

        if not parsed.netloc or not re.match(r'^[a-zA-Z0-9.-]+(:[0-9]+)?$', parsed.netloc):
            return ""

        # Mantém caminho e query
        path = parsed.path if keep_path else ''
        query = parsed.query if keep_query else ''

        # Codifica corretamente com quote()
        safe_path = quote(path, safe='/:@')  # Permite / : @ no caminho
        safe_query = quote(query, safe='=&%?')  # Permite & = % ? na query

        # Monta partes
        clean_parts = (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            safe_path,
            '',  # params (obsoleto)
            safe_query,
            ''   # fragment
        )

        sanitized = urlunparse(clean_parts)

        # Remove caracteres *realmente* perigosos (ex: < > " ' \)
        sanitized = re.sub(r'[<> "\'\\]', '', sanitized)

        return sanitized if len(sanitized) >= 8 else ""

    except Exception as e:
        logger.error(f"Erro na sanitização de URL: {e}", exc_info=True)
        return ""

def is_long_url(url: str, limit: int = 200) -> bool:
    """
    Verifica se a URL COMPLETA é longa (inclui caminho e query).
    """
    try:
        full_url = sanitize_url(url, keep_path=True, keep_query=True)
        return len(full_url) > limit or url.count("&") > 8
    except Exception as e:
        logger.error(f"Erro ao verificar comprimento da URL: {e}", exc_info=True)
        return False