# O logger é configurado em utils/console.py junto com o output Rich.
# Importe aqui apenas se precisar fazer log direto em módulos internos.
import logging

logger = logging.getLogger("youtube_scraper")
