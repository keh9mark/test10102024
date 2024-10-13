import unittest
import logging
from io import StringIO

from opentelemetry.trace import (
    get_current_span,
    StatusCode,
)
from opentelemetry import trace

from pytracelog.pytracelog_logging.handlers import StdoutHandler, StderrHandler, TracerHandler


class TestStdoutHandler(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.handler = StdoutHandler(stream=self.stream)
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.stream.close()

    def test_info_log(self):
        text = 'This is an info message'
        self.logger.info(text)
        self.assertIn(text, self.stream.getvalue())

    def test_error_log(self):
        text = 'This is an error message'
        self.logger.error(text)
        self.assertNotIn(text, self.stream.getvalue())

    def test_debug_log(self):
        text = 'This is a debug message'
        self.logger.debug(text)
        self.assertIn(text, self.stream.getvalue())

    def test_warning_log(self):
        text = 'This is a warning message'
        self.logger.warning(text)
        self.assertIn(text, self.stream.getvalue())

    def test_critical_log(self):
        text = 'This is a critical message'
        self.logger.critical(text)
        self.assertNotIn(text, self.stream.getvalue())


class TestStderrHandler(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.handler = StderrHandler(stream=self.stream)
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.stream.close()

    def test_info_log(self):
        text = 'This is an info message'
        self.logger.info(text)
        self.assertNotIn(text, self.stream.getvalue())

    def test_error_log(self):
        text = 'This is an error message'
        self.logger.error(text)
        self.assertIn(text, self.stream.getvalue())

    def test_debug_log(self):
        text = 'This is a debug message'
        self.logger.debug(text)
        self.assertNotIn(text, self.stream.getvalue())

    def test_warning_log(self):
        text = 'This is a warning message'
        self.logger.warning(text)
        self.assertNotIn(text, self.stream.getvalue())

    def test_critical_log(self):
        text = 'This is a critical message'
        self.logger.critical(text)
        self.assertIn(text, self.stream.getvalue())


class TestTracerHandler(unittest.TestCase):
    def setUp(self):
        self.record = logging.LogRecord(
            name='test_logger',
            level=logging.ERROR,
            pathname='',
            lineno=0,
            msg='This is a test message',
            args=(),
            exc_info=None
        )

    def test_get_record_attrs_remove_msg(self):
        attrs = TracerHandler.get_record_attrs(self.record, remove_msg=True)
        self.assertNotIn('msg', attrs)
        self.assertNotIn('name', attrs)
        self.assertNotIn('exc_info', attrs)
        self.assertNotIn('exc_text', attrs)
        self.assertNotIn('msecs', attrs)
        self.assertNotIn('relativeCreated', attrs)
        self.assertNotIn('otelSpanID', attrs)
        self.assertNotIn('otelTraceID', attrs)
        self.assertNotIn('otelServiceName', attrs)

    def test_get_record_attrs_keep_msg(self):
        attrs = TracerHandler.get_record_attrs(self.record, remove_msg=False)
        self.assertIn('original.message', attrs)
        self.assertEqual(attrs['original.message'], 'This is a test message')
        self.assertNotIn('msg', attrs)
        self.assertNotIn('name', attrs)
        self.assertNotIn('exc_info', attrs)
        self.assertNotIn('exc_text', attrs)
        self.assertNotIn('msecs', attrs)
        self.assertNotIn('relativeCreated', attrs)
        self.assertNotIn('otelSpanID', attrs)
        self.assertNotIn('otelTraceID', attrs)
        self.assertNotIn('otelServiceName', attrs)

    def test_get_record_attrs_custom_message_attr_name(self):
        attrs = TracerHandler.get_record_attrs(self.record, remove_msg=False, message_attr_name='custom.message')
        self.assertIn('custom.message', attrs)
        self.assertEqual(attrs['custom.message'], 'This is a test message')
        self.assertNotIn('msg', attrs)
        self.assertNotIn('name', attrs)
        self.assertNotIn('exc_info', attrs)
        self.assertNotIn('exc_text', attrs)
        self.assertNotIn('msecs', attrs)
        self.assertNotIn('relativeCreated', attrs)
        self.assertNotIn('otelSpanID', attrs)
        self.assertNotIn('otelTraceID', attrs)
        self.assertNotIn('otelServiceName', attrs)

class TestTracerHandler2(unittest.TestCase):

    def setUp(self):
        # Создание трассировщика
        self.tracer = trace.get_tracer(__name__)
        # Настройка логгера
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.handler = TracerHandler()
        self.logger.addHandler(self.handler)

    def test_emit(self):
        # проверим без ошибок статус INFO
        with self.tracer.start_as_current_span("test-span"):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test",
                args=(),
                exc_info=None
            )
            self.handler.emit(record)
            span = get_current_span()
            self.assertEqual(span.status.status_code, StatusCode.UNSET)
            self.assertEqual(len(span.events), 1)


    def test_emit_with_error(self):
        # проверим со статусом ERROR
        with self.tracer.start_as_current_span("test-span"):
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Test",
                args=(),
                exc_info=None
            )
            self.handler.emit(record)
            span = get_current_span()
            self.assertEqual(span.status.status_code, StatusCode.ERROR)
            self.assertEqual(len(span.events), 1)
            self.assertEqual(span.events[0].name, 'Test')


    def test_emit_with_exception(self):
        #Проверим с исключением и статус ERROR
        try:
            1 / 0
        except ZeroDivisionError as e:
            exc_info = (type(e), e, e.__traceback__)

        with self.tracer.start_as_current_span("test-span"):
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Test",
                args=(),
                exc_info=exc_info
            )
            self.handler.emit(record)
            span = get_current_span()
            self.assertEqual(span.status.status_code, StatusCode.ERROR)
            self.assertEqual(len(span.events), 1)
            self.assertEqual(span.events[0].name, 'exception')


if __name__ == '__main__':
    unittest.main()
