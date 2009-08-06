#! /bin/bash
pushd po
for i in *.po
do
po=$i
msgmerge "$po" "monajat.pot" > "$po.tmp" && \
mv "$po.tmp" "$po"
mkdir -p "../locale/${po/.po/}/LC_MESSAGES/"
msgfmt -o "../locale/${po/.po/}/LC_MESSAGES/monajat.mo" "$po"
done
popd

