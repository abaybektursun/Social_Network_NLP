PAGES=(HomuxMado GlassesHomura sayachan KyootChan eromanga.anime EromangaSenseiUSA eromanga.ala Fuck-mariwana-legalize-anime-waifu-marieg EcchiFederation LoliRepublic LoliconUnion teaisalolicon 1430134157272350 LoliHunters2 TBoLolicons EveryonesOneeChan UnlimitedMoe MWMMisery Anotherpagewithanimucontent RealLifeIsntEvenSugoi2 LyntesHappyPlace Bimouto MeganekkoBestGirl ltelk1 570265806464345 InTheMoodForALewd WaifuLove ponkotsuposting weeabooty 580878808676318)
 
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



