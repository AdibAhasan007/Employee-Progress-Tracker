#!/usr/bin/env bash
set -e

gunicorn -c gunicorn_conf.py app.main:app
