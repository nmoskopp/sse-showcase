#!/bin/sh
set -eu

npm install extended-eventsource
npm install esbuild

./server.py
