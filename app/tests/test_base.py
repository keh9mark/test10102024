import logging
from os import environ

import unittest
from unittest.mock import patch
from logstash_async.handler import AsynchronousLogstashHandler
from opentelemetry.trace import get_tracer_provider, ProxyTracerProvider
from opentelemetry.sdk.trace import TracerProvider 

from pytracelog.base import PyTraceLog, LOGSTASH_HOST, LOGSTASH_PORT
from pytracelog.pytracelog_logging.handlers import StdoutHandler, StderrHandler, TracerHandler



class TestPyTraceLog(unittest.TestCase):
    """Тесты для класса PyTraceLog"""

    def setUp(self):
        PyTraceLog.reset()

    def tearDown(self):
        environ.pop('OTEL_EXPORTER_JAEGER_AGENT_HOST', None)

    def test_init_root_logger_set_level(self):
        #  проверим корректность выставления уровня логгирования
        PyTraceLog.init_root_logger(level='inFO')
        root_logger = logging.getLogger()
        current_level = root_logger.getEffectiveLevel()
        level_name = logging.getLevelName(current_level)
        self.assertEqual(level_name, 'INFO')

    def test_init_root_logger_already_initialized(self):
        # Проверим, что инициализация не происходит повторно
        PyTraceLog.init_root_logger(level='INFO')
        initial_handlers_count = len(logging.getLogger().handlers)
        # попробуем второй раз инициализировать с другим level
        PyTraceLog.init_root_logger(level='DEBUG')
        self.assertEqual(initial_handlers_count, len(logging.getLogger().handlers))


    def test_init_root_logger_handlers(self):
        # проверим, что зарегалось 2 обработчика
        PyTraceLog.init_root_logger(level=logging.INFO)
        root_logger = logging.getLogger()
        self.assertEqual(len(root_logger.handlers), 2)
        self.assertIsInstance(root_logger.handlers[0], StdoutHandler)
        self.assertIsInstance(root_logger.handlers[1], StderrHandler)

    def test_extend_log_record(self):
        # Проверим расширение записи лога статическими атрибутами
        PyTraceLog.extend_log_record(custom_attr='value')
        record = logging.getLogRecordFactory()(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='',
            args=(),
            exc_info=None
        )
        self.assertEqual(record.custom_attr, 'value')

    @patch.dict(environ, {LOGSTASH_HOST: 'localhost', LOGSTASH_PORT: '5044'})
    def test_init_logstash_logger(self):
        # Проверим инициализацию Logstash логгера
        PyTraceLog.init_logstash_logger(level='INFO', message_type='python', index_name='python')
        root_logger = logging.getLogger()
        self.assertEqual(len(root_logger.handlers), 1)
        self.assertIsInstance(root_logger.handlers[0], AsynchronousLogstashHandler)

    @patch.dict(environ, {LOGSTASH_HOST: 'localhost', LOGSTASH_PORT: '5044'})
    def test_init_logstash_logger_already_initialized(self):
        # Проверим, что инициализация не идет повторно Logstash логгера
        PyTraceLog.init_logstash_logger(level='INFO', message_type='python', index_name='python')
        initial_handlers_count = len(logging.getLogger().handlers)
        PyTraceLog.init_logstash_logger(level='INFO', message_type='python', index_name='python')
        self.assertEqual(initial_handlers_count, len(logging.getLogger().handlers))

    @patch.dict(environ, {LOGSTASH_HOST: 'localhost', LOGSTASH_PORT: '5044'})
    def test_init_root_and_logstash_logger(self):
        # проверка того, что root_logger и logstash_logger инициализируются вместе
        PyTraceLog.init_root_logger(level=logging.INFO)
        PyTraceLog.init_logstash_logger(level='INFO', message_type='python', index_name='python')
        self.assertEqual(3, len(logging.getLogger().handlers))

    @patch.dict(environ, {})
    def test_init_tracer(self):
        # Проверим, что инициализация не проходит без переменной окружения
        PyTraceLog.init_tracer(service='test_service')
        tracer_provider_proxy = get_tracer_provider()
        self.assertIsInstance(tracer_provider_proxy, ProxyTracerProvider)
        # с переменной проходит
        environ['OTEL_EXPORTER_JAEGER_AGENT_HOST'] = "localhost"
        PyTraceLog.init_tracer(service='test_tracer')
        tracer_provider = get_tracer_provider()
        self.assertIsInstance(tracer_provider, TracerProvider)
        self.assertEqual(tracer_provider.resource.attributes['service.name'], 'test_tracer')


    def test_init_tracer_logger(self):
        # Проверим инициализацию обработчика для экспорта записей журнала в систему трассировки
        PyTraceLog.init_tracer_logger(level='INFO')
        root_logger = logging.getLogger()
        self.assertEqual(len(root_logger.handlers), 1)
        self.assertIsInstance(root_logger.handlers[0], TracerHandler)

    def test_init_tracer_logger_already_initialized(self):
        # Проверим инициализацию обработчика для экспорта записей журнала в систему трассировки
        PyTraceLog.init_tracer_logger(level='INFO')
        initial_handlers_count = len(logging.getLogger().handlers)
        PyTraceLog.init_tracer_logger(level='INFO')
        self.assertEqual(initial_handlers_count, len(logging.getLogger().handlers))

    def test_init_root_and_tracer_logger(self):
        # Проверим инициализацию обработчика для экспорта записей журнала в систему трассировки
        PyTraceLog.init_root_logger(level=logging.INFO)
        PyTraceLog.init_tracer_logger(level='INFO')
        self.assertEqual(3, len(logging.getLogger().handlers))

    def test_reset(self):
        # Проверим сброс настроек
        PyTraceLog.init_root_logger(level='INFO')
        PyTraceLog.reset()
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.getEffectiveLevel(), logging.WARNING)
        self.assertEqual(len(root_logger.handlers), 0)

if __name__ == '__main__':
    unittest.main()
