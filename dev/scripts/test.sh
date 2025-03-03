#!/bin/bash

dotest() {
    testfile=${1}
    echo "------ TEST ${testfile}"
    python -m unittest "${testfile}"
    if [[ "$?" != "0" ]]; then
        exit 1
    fi
}

for fname in $(git ls-files --others --exclude-standard | grep --color=never -E '.*_test\.py$'); do
    dotest "${fname}"
done

for fname in $(git ls-files | grep --color=never -E '.*_test\.py$'); do
    dotest "${fname}"
done
