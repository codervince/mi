#!/bin/bash

NAME=investment
HOMEDIR=/mi/django/lucky78
DJANGODIR=${HOMEDIR}/${NAME}
SOCKFILE=/mi/django/lucky78/socket/${NAME}.sock
# Три рабочих процесса на 1 ядро процессора
NUM_WORKERS=3
DJANGO_WSGI_MODULE=${NAME}.wsgi
GUNICORN=${HOMEDIR}/env/bin/gunicorn

cd $DJANGODIR
source ${HOMEDIR}/env/bin/activate

# Если по какой-то причине директории с SOCKFILE не существует -- создаем её
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Запускаем наш Django-проект
# Опционально можем записывать Debug в лог файлы (или другие файлы)
exec ${GUNICORN} ${DJANGO_WSGI_MODULE}:application \
  --workers $NUM_WORKERS \
    --bind unix:${SOCKFILE} \
    # добавляем если настройки проекта хранятся в не стандартном модуле
    # --env DJANGO_SETTINGS_MODULE=settings.production \
    # --log-level=debug \
    # --log-file=-
    
