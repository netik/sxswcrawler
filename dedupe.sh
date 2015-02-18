cat download_queue.txt  | awk '{print $NF}' |  sort | uniq 
