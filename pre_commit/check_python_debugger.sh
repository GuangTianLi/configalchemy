#!/usr/bin/env bash

pdb_check=$(git grep -E -n 'import i?pdb')
if [ ${#pdb_check} -gt 0 ]
then
        echo "COMMIT REJECTED: commit contains code with break points. Please remove before commiting."
        echo $pdb_check
        exit 1
else
        echo "Code contains no break points"
fi

exit 0
