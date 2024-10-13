# test10102024

Unittest

1. Создать python окружение и установить туда зависимости app/requirements.txt

python3 -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt

2. Запустить тесты

coverage run -m unittest discover -s tests

3. Получить отчет

coverage report

pytracelog/__init__.py                          3      0   100%
pytracelog/base.py                             83      0   100%
pytracelog/pytracelog_logging/__init__.py       0      0   100%
pytracelog/pytracelog_logging/handlers.py      52      0   100%
tests/test_base.py                             84      1    99%
tests/test_handlers.py                        142      1    99%
---------------------------------------------------------------
TOTAL                                         364      2    99%


4. Чтобы получить полный html результат

coverage html


Docker

1. В корне проекта выполнить команду

docker-compose up --build -d

2.1 http://localhost:5000/ - flask приложение, для выполнения тестовых логов 

2.2 http://localhost:5601/ - elastic

См скрины