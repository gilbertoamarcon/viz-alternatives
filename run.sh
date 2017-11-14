#!/bin/bash
## Commit

rm svg/* png/*
python plot.py
mogrify -density 100 -format png svg/*.svg
mv svg/*.png png/