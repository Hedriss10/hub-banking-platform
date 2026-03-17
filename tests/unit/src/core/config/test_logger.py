import logging

from src.core.config import logger as logger_module

# ---------------------------------------------------------------------------
# Logger - instância e atributos
# ---------------------------------------------------------------------------


def test_logger_is_logging_logger():
    """O logger exportado deve ser uma instância de logging.Logger."""
    assert isinstance(logger_module.logger, logging.Logger)


def test_logger_name():
    """O logger deve ter o nome do módulo (caminho de importação)."""
    assert logger_module.logger.name == 'src.core.config.logger'


def test_logger_has_standard_methods():
    """O logger deve expor os métodos padrão de logging."""
    logger = logger_module.logger
    assert callable(logger.debug)
    assert callable(logger.info)
    assert callable(logger.warning)
    assert callable(logger.error)
    assert callable(logger.critical)
    assert callable(logger.exception)


# ---------------------------------------------------------------------------
# Logger - emissão de mensagens
# ---------------------------------------------------------------------------


def test_logger_info_emits_message(caplog):
    """logger.info() deve emitir mensagem no nível INFO."""
    with caplog.at_level(logging.INFO):
        logger_module.logger.info('mensagem de teste')
    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'mensagem de teste'
    assert caplog.records[0].levelname == 'INFO'


def test_logger_warning_emits_message(caplog):
    """logger.warning() deve emitir mensagem no nível WARNING."""
    with caplog.at_level(logging.WARNING):
        logger_module.logger.warning('aviso de teste')
    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'aviso de teste'
    assert caplog.records[0].levelname == 'WARNING'


def test_logger_error_emits_message(caplog):
    """logger.error() deve emitir mensagem no nível ERROR."""
    with caplog.at_level(logging.ERROR):
        logger_module.logger.error('erro de teste')
    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'erro de teste'
    assert caplog.records[0].levelname == 'ERROR'


def test_logger_debug_emits_when_level_debug(caplog):
    """logger.debug() emite quando nível está em DEBUG."""
    with caplog.at_level(logging.DEBUG):
        logger_module.logger.debug('debug de teste')
    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'debug de teste'
    assert caplog.records[0].levelname == 'DEBUG'


# ---------------------------------------------------------------------------
# Configuração (basicConfig)
# ---------------------------------------------------------------------------


def test_root_logger_has_handler():
    """O root logger deve ter pelo menos um handler após basicConfig."""
    assert len(logging.root.handlers) >= 1
