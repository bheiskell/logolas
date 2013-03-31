Logolas
=======

Logolas is a light-weight multi-file log scraper with an accompanying real-time web interface.

Screenshot
----------

.. image:: images/screenshot.png

Design
------

* Logolas utilizes inotify to watch files for updates. This means it will not work on Windows or over NFS.
* Lines are scraped using regular expressions. At a minimum, each line must include a date/time.
* The scraped lines are persisted to a SQL backend. This addresses loss of historical data due to log rotation. However, currently purging is not automatic.
* Web interface performs standard polling at a configurable rate.

Features
--------

* Multi-file logging
* Multi-regular expression scraping per-file
* Real-time streaming of logged events
* Filtering on any matched field
* Access to historical data (admittedly a bit awkward)

Limitations
-----------
* Cannot parse timezones currently.

Why?
----

An administrator of my Minecraft server needed a web interface that provided real-time access to information stored in multiple log files on my server.

This started as a toy project, but I've decided to publish it as I can imagine there is someone out there who would benefit from this work.

Installation
------------

The following instructions assumes a debian based distribution.

Using virtual environments::

  git clone https://github.com/bheiskell/logolas.git
  cd logolas
  sudo aptitude install python-virtualenv
  virtualenv --no-site-packages venv
  . venv/bin/activate
  easy_install .
  cp sample/config.yml .

To start the log scraper::

  cd logolas
  . venv/bin/activate
  logolas config.yml

Alternatively, deploy to the root python installation::

  git clone https://github.com/bheiskell/logolas.git
  cd logolas
  sudo easy_install .
  cp sample/config.yml .
  logolas config.yml

Web
~~~

To launch the web interface, run::

  cd logolas
  . venv/bin/activate
  export LOGOLAS_CONFIG=config.py
  logolas_web

TODO: wsgi

MySQL
~~~~~

If you choose to use MySQL with virtual environments, you'll need to install libmysqlclient-dev and python-dev with aptitude. Then you can easy_install mysql-python.

Alternatively, you should be able to simply install to python-mysqldb if you're not using virtual environments.
