# Тестовое задание для CNord
Реализовать серверное приложение на tornado. Приложение должно слушать на двух tcp-портах (8888 и 8889). По
первому порту оно должно принимать подключения и сообщения от подключенных клиентов ("источников").

Всем подключенным клиентам ("слушателям") на порту 8889 приложение должно отправлять на каждое принятое от
источника сообщение сообщения в текстовом формате следующего вида: "[<идентификатор источника>] <Имя
поля> | <Значение>\r\n" (по одной строке на каждую пару "имя - значение" в сообщении от источника).

При подключении нового слушателя на порт 8889, приложение должно отправить ему список всех подключенных на
данный момент источников в формате:
[<идентификатор источника>] <номер последнего сообщения> | <статус (строка "IDLE", "ACTIVE" или
"RECHARGE")> | <время, прошедшее с момента получения последнего сообщения в целых миллисекундах>\r\n (по
одной строчке на каждый источник)

Для запуска последовательно выполните следующие действия:
*  pip install -r requirements.txt
*  python3 server.py
*  python3 client_source.py
*  python3 client_listener.py

Клиент-источник отправляет тестовое сообщение по нажатию клавиши Enter и ждет сообщения от сервера.
