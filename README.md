# gno_parser
## Консонльный интерфейс
python gn_parser.py -h
## Пример запуска (cmd):
gn_parser.py -u https://news.google.com/news/?ned=de_at^&hl=de-AT
## Также есть два варианта вывода:
1. Вывод всех ссылок на источник
2. Вывод по одной ссылке на источник в каждой секции, в которой есть даный источник
>Для этого меняем зачение переменной all_links на True/False соответственно (по-умолчанию True)
