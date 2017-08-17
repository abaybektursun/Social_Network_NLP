PAGES=(WeAreKWGB KDNAnime ReWaifuProject)

for i in ${PAGES[*]}
do
    nohup python3 scrap.py $i &
done
