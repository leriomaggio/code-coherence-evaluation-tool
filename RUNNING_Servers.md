
# HOW to start Servers

Many servers are required to start before running Django Dev-server:

* [PostgreSQL](#postgres)
* [rabbitMQ server](#rabitmq)
* [Celery Worker Server](#celery)
* [Django Server](#django)

## <a name="postgres">PostgreSQL</a>

`postgres -D /usr/local/var/postgres`

## <a name="rabbbitmq">rabbitMQ Server</a>

`sudo rabbitmq-server`

## <a name="celery">Celery Worker Server</a>

`celery worker --loglevel=info`

## <a name="django">Django Server</a>

`python manage.py runserver`
