#!/bin/bash

MAX_PENGS=100
#MIN_WAIT=1
#MAX_WAIT=3

export DISPLAY=:0

function exit_handler {
  echo 'Signal caught! Killing everyone!'
  sleep 1
  killall xpenguins 2>/dev/null
  exit
}

trap exit_handler SIGTERM SIGINT

for i in $(seq 0 "$MAX_PENGS") ; do
  echo "Dispatching sanic $i"
  xpenguins --theme 'Sonic the Hedgehog' >/dev/null 2>&1 &
  #sleep "$(shuf -i "${MIN_WAIT}-${MAX_WAIT}" -n 1)"
  sleep 1
done
wait
