homework_bot
## Python telegram bot
#### Telegram-бот, который обращается к API сервису Практикум.Домашка и узнаваёт статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.
- бот раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
- при обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram;
- логирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.

## Используемые технологии:
- python
- requests
- logging
- telegram

### Автор: 
[Балахонова Марина](https://github.com/margoloko)
