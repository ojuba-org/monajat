#! /bin/bash
xgettext -o "po/monajat.pot" monajat/*.py
pushd po
for i in *.po
do
po=$i
msgmerge "$po" "monajat.pot" > "$po.tmp" && \
mv "$po.tmp" "$po"
done
popd
