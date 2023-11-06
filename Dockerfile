# какую версию поставим в контейнер
FROM python:3.9.18-slim-bookworm

# Если нам надо запустить только промаркированные тесты, то:
# AVG run_env=test_env  # у меня есть такое окружение для примера
# env $run_env

# подпишем наш контейнер
LABEL "Educatoin"="PyTest"
LABEL "creator"="Serpent TRK"

# указатель на директорию внутри контейнера. Слеши наоборот!
# хотя не знаю зачем я прописал. В настройках контейнера уже указал
WORKDIR ./send_request_me

#  для отчетов
VOLUME /allureResult

# фиксим возможноые ошибки на шаге RUN pip3 install -r requirements.txt
# COPY requirements.txt .
# устанавливаем наши зависимости
# RUN pip3 install -r requirements.txt


# перенос проекта в контейнер. Первая точка - откуда (мы находимся локально в проекте.
# Вторая - куда класть. У нас путь указан выше
COPY . .

# доустанавливаем необходимое для работы проекта в контейнере
# тут еще могут быть какие-то логи, которые можно удалить, добавив в строку еще что-то,
# но я не нашел пока что добавить. Оставим так.
#RUN apk update && apk upgrade && apk add bash
RUN cd /tmp \
&& apt-get update \
&& apt-get install -y curl apt-utils wget unzip\
&& rm -rf /var/lib/apt/lists/*

# устанавливаем наши зависимости
RUN pip3 install -r requirements.txt

## Что будет сложено в контейнер:
# тут мы показываем какие тесты собираемся упаковывать в контейнер
# CMD pytest -s -v send_request_me/users/*

# В случае, когда надо запустить только промаркированные тесты, команда будет следующей:
# CMD pytest -m "$env" -s -v tests/*       # это как раз для примера наверху

# А это сразу с отчетом allure (надо установить):
CMD pytest -s -v send_request_me/* --alluredir=allureResult


# если Dockerfile находится локально (у нас этот фаил локальный) и придумали ему имя :
# docker build -t send_request_me_tests .

# команда на запуск контейнера из терминала c указанием пути до контейнера:
# docker build -t automapion-tests -f F:/ОБУЧЕНИЕ/DOCKER/USERS/Dockerfile
# если собираем контейнер с определенным окружением, то:
# docker build --build-arg -t придумать_название_контейнеру .
# test_env - у меня есть подобное окружение, потому как пример
# docker build --build-arg env=companies -t send_request_me_tests .

# Если хочется собрать контейнер без раннее сохраненных кешей.
# docker build --no-cache=True --build-arg env=companies -t send_request_me_tests .

# Запуск из консоли docker run _название файла_
# docker run send_request_me_tests

# посмотреть данные последнего созданного контейнера
# docker ps -l
# 66c0cbae555e  66c0cbae555e7f0ce390b9ac07c8be08b0b33a051bd998d37f8847ac305eabd1

## Это чтобы доставть отчеты должно работать так:
# # docker cp 66c0cbae555e7f0ce390b9ac07c8be08b0b33a051bd998d37f8847ac305eabd1:/send_request_me/allureesult .
# возможно у меня не работает из-за больших букв в названии файла, я не знаю...

