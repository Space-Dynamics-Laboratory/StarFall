#!/usr/bin/env bash

ln -s $(pwd)/Data /mnt/Data

# find all the package.json files
declare -a pids
paths=($(find . -type d -name "node_modules" -prune -o -type f -name 'package.json' -print))
for i in "${!paths[@]}"; do
 # remove /package.json to get the directory
 dir=${paths[$i]%/package.json}
 pushd $dir
 npm install &
 pids[${i}]=$!
 popd
done

for pid in ${pids[*]}; do
 wait $pid
done



[ -f .ssh/keycopy.sh ] && cd .ssh && ./keycopy.sh; cd ..
# echo '[ -f ~/.ssh/id_rsa ] && eval "$(ssh-agent -s)" &>/dev/null && ssh-add ~/.ssh/id_rsa &>/dev/null' >> ~/.bashrc
# echo 'alias nrs="npm run serve"' >> ~/.bashrc

exit 0
