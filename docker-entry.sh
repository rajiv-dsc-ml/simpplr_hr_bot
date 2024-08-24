#!/bin/bash
gunicorn -b 0.0.0.0:8087 -t 300 -c gunicornConfig.py api:app --log-level debug
