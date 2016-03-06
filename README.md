# phones

Простой телефонный справочник для группы компаний на базе tornado web framework.

Главная страница - список команий группы.
По клику на компанию открывается телефонный справочник данной компании.
При вводе фрагмента ФИО в поисковую форму и отправке данных осуществляется поиск по фрагменту ФИО по всем компаниям группы, а найденные совпадения выводятся списком, отформатированным в соответствии с иерархией структурных подразделений.   

Работает с БД Postgresql.

## Установка и развертывание

### Предварительные требования

TODO

### Сервер приложений

1. Скопировать файлы в папку на сервере
2. Выполнить 
{{{ python phones_app.py}}}
3. Если необходимо, на фаеволле открыть порт 8888.

### База данных

TODO

## Описание файлов

settings.py - файл настроек, содержит словарь параметров соединения с БД по умолчанию и альтернативной БД.
dbutils.py - инструменты для обращения к БД - базовая модель, соединение, вспомогательные элементы.
models.py - модели и итераторы для работы с БД.
phones_app.py - собственно веб-приложение с обработчиками запросов.
units_page.html - шаблон для списка компаний группы.
list_unit_page.html - шаблон списка контактов.


