PAGES=(KawaiiSenpai cuteanimegirls13 RealitySuckedCuzFantasyIsBetter KusoTTK2.0 6969dokidoki6969 wouldloliagain VisonOfLolis LoliCentralTwoPointO loliconmasa LoliconsUniteUncensored2 LoliRaptors Unlimited.Loli.Works BestWaifuClub InfiniteStratos.Official KurumuKuronosDeliciousBoobs edgy.weeb.memes memehugs WDYMISTPALOAD 235791193222581 707108439433429 otherlewdness osugame CuddlesAndPatpats zenkichi91)
 
#add 50 page run 2 pages same time
pids=""
for ((i = 0; i < ${#PAGES[@]}; i++))
do
    #nohup python3 scrap.py $i &
    #nohup echo ${PAGES[i]} &
    #nohup echo ${PAGES[i+1]} &
    nohup python3 scrap.py ${PAGES[i]} &
    pids+=" $!"
    nohup python3 scrap.py ${PAGES[i+1]} &
    pids+=" $!"
    nohup python3 scrap.py ${PAGES[i+2]} &
    pids+=" $!"
    let "i++"
    let "i++"
    wait $pids || { echo "there were errors" >&2; }
    echo "next"
done



