"""
=======================================================================
                            MÓDULO DE LOGS
=======================================================================


Descrição:
O logging registra eventos, avisos e falhas durante a execução. Isso ajuda a identificar problemas sem depender exclusivamente do 
terminal ou de mensagens exibidas ao usuário.


Responsabilidades:
Responsável por configurar os logs no terminal e em arquivo, com rotação automática para limitar o tamanho dos arquivos.

"""

import logging
from logging.handlers import RotatingFileHandler
from config.settings import settings


def configuracoes_logging() -> None:
    root_logger = logging.getLogger()

    if getattr(root_logger, "_configured_by_app", False):
        return

    log_level = getattr(logging, settings.LOG_LEVEL, None)

    if not isinstance(log_level, int):
        log_level = logging.INFO

    root_logger.setLevel(log_level)

    formato_log = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato_log)
    root_logger.addHandler(console_handler)

    log_path = settings.log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formato_log)
    root_logger.addHandler(file_handler)

    root_logger._configured_by_app = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)