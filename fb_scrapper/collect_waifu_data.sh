PAGES=(1445665322420220 mamiandkyoko 7deadlysinsfmab)

for i in ${PAGES[*]}
do
    nohup python3 scrap.py $i &
done
