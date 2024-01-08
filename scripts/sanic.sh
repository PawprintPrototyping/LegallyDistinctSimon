#!/bin/bash

MAX_PENGS=100
MIN_WAIT=1
MAX_WAIT=3

export DISPLAY=:0

for i in $(seq 0 "$MAX_PENGS") ; do
  echo "Dispatching sanic $i"
  xpenguins --theme 'Sonic the Hedgehog' >/dev/null 2>&1 &
  sleep "$(shuf -i "${MIN_WAIT}-${MAX_WAIT}" -n 1)"
  #sleep 0.1
done
