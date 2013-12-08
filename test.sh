#!/bin/sh
ADDR=1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i
SONG="$HOME/reaper.flac"
rm -f out.wav song.wav clear.wav
python embed.py $ADDR "$SONG" out.wav
EX=$(python extract.py out.wav)
if [ x$ADDR != x$EX ]
then
	echo "extract: expected $ADDR, got $EX" 1>&2
	exit 1
fi
python conv.py "$SONG" song.wav
python clear.py out.wav clear.wav
exec cmp clear.wav song.wav
