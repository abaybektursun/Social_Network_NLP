PAGES=()
TOPIC=""

pids=""
for ((i = 0; i < ${#PAGES[@]}; i++))
do
    #nohup python3 scrap.py $i &
    #nohup echo ${PAGES[i]} &
    #nohup echo ${PAGES[i+1]} &
    nohup python3 scrap.py ${PAGES[i]} $TOPIC &
    pids+=" $!"
    nohup python3 scrap.py ${PAGES[i+1]} $TOPIC &
    pids+=" $!"
    nohup python3 scrap.py ${PAGES[i+2]} $TOPIC &
    pids+=" $!"
    let "i++"
    let "i++"
    wait $pids || { echo "there were errors" >&2; }
    echo "next"
done



