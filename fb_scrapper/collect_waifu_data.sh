PAGES=(AlexWavvesLovesYouLosers Circumcision.ThePage)

for i in ${PAGES[*]}
do
    python3 scrap.py $i &
done
