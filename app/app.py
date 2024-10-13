import os
import logging

from flask import Flask, jsonify

from pytracelog.base import PyTraceLog

app = Flask(__name__)


os.environ['LOGSTASH_HOST'] = 'logstash'
os.environ['LOGSTASH_PORT'] = '5044'
os.environ['OTEL_EXPORTER_JAEGER_AGENT_HOST'] = 'logstash'


logger = logging.getLogger(__name__)
PyTraceLog.init_root_logger(level='INFO')
PyTraceLog.init_logstash_logger(level='INFO', message_type='python', index_name='python')
PyTraceLog.init_tracer(service='test_service')
PyTraceLog.init_tracer_logger(level='INFO')


def main():
    # тестовые логи
    logger.info("INFO")
    logger.warning("WARNING")
    logger.error("ERROR")


@app.route('/')
def hello():
    main()
    return jsonify(message="test")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
