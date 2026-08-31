"""Configuração de logging do projeto — usado por `src/pipeline.py` para dar
observabilidade mínima à execução (ver `docs/qualidade_dados.md`, seção 6).
"""

import logging

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name):
    """Configura o logging básico do processo e retorna um logger nomeado.

    Chamar mais de uma vez é seguro: `logging.basicConfig` só tem efeito
    na primeira chamada do processo (chamadas seguintes são no-op), então
    todos os loggers do projeto compartilham o mesmo formato/nível.

    Args:
        name: Nome do logger, tipicamente `__name__` do módulo chamador —
            aparece em cada linha de log, identificando a origem.

    Returns:
        Instância de `logging.Logger` configurada com nível `INFO` e
        `LOG_FORMAT` (timestamp, nível, nome do logger, mensagem).
    """
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    return logging.getLogger(name)
