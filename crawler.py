import requests
from bs4 import BeautifulSoup
import re
import collections, heapq
from urllib.parse import urlparse, urljoin
import time
import pickle

def extract_links(url, maxLinks=100):
    print("Visiting url", url[:30], end="...", flush=True)
    try:
        # add headers to pretend human user
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',}
        page = requests.get(url, headers=headers, timeout=5)
    except:
        print("\trequest error")
        return []
    # print("OK", end="\t", flush=True)
    soup = BeautifulSoup(page.text, "html.parser")

    if (not soup.body) or (not soup.body.find(string=re.compile("nobel", re.I))):
        print("\tcannot find 'nobel'")
        return []

    links = set()
    
    for link in soup.find_all('a'):
        new_link = link.get('href')
        if not new_link:
            continue
        
        # join new_link with root url
        new_link = urljoin(url, new_link)

        # normalize link: <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
        res = urlparse(new_link)
        if res.scheme not in ["http", "https", "mailto"]:
            continue
        new_link = res.scheme+"://" + res.netloc + res.path
        links.add(new_link)
        if len(links) >= maxLinks:
            break

    print("\toutgoing links:", len(links))
    return list(links)


def crawl(seeds, link_limit, max_depth=5):
    """
    Return: link_dict
    {url: {
        "incoming": int
        "outgoing": int
        "depth": int
        "type": string
        }
    }
    """
    start_time = time.time()
    task_queue = collections.deque(seeds[:])
    link_dict = {} # all info for links
  
    curr_depth = 0
    count = 0
    done = False
    while not done and task_queue:
        curr_depth += 1
        print("\ndepth =", curr_depth, "|  number of links in queue:", len(task_queue))

        for _ in range(len(task_queue)):
            url = task_queue.popleft()
            count += 1
            if url in link_dict:
                link_dict[url]['incoming'] += 1
            else:
                link_dict[url] = {
                    "incoming": 1,
                    "outgoing": 0,
                    "depth": curr_depth,
                    "type": get_link_type(url)
                }
                
                # if curr_depth==1:
                #     links = extract_links(url, 1000)
                # elif "wikipedia" in urlparse(url).netloc:
                #     links=[]
                # else:
                #     links = extract_links(url)
                
                links = extract_links(url)
                link_dict[url]["outgoing"] = len(links)
                task_queue.extend(links)

                if count+len(task_queue) >= link_limit:
                    print("Total links reached limit:", link_limit)
                    print("Total visited links:", len(link_dict))
                    clear_task_queue(task_queue, curr_depth, link_dict)
                    done = True
                    break
       
        if curr_depth >= max_depth:
            done = True
        
        print_time_elapsed(start_time)
            
    
    print("Crawling completed. Total number of unique links:", len(link_dict))
    print_time_elapsed(start_time)
    return link_dict

def clear_task_queue(task_queue, curr_depth, link_dict):
    print("Adding remaining links to link_dict...")
    for url in task_queue:
        if url in link_dict:
            link_dict[url]['incoming'] += 1
        else:
            link_dict[url] = {
                "incoming": 1,
                "outgoing": 0,
                "depth": curr_depth,
                "type": get_link_type(url)
            }
    return None

def get_link_type(url):
    
    parse = urlparse(url)
    tail = parse.path.split("/")[-1]

    if "http" not in parse.scheme:
        return "non-http"
    
    domain_suffix = parse.netloc.split(".")[-1]
    if domain_suffix in ['se', 'es', 'jp', 'cn', 'br', 'au', 'uk']:
            return "foreign"

    if "." not in tail:
        return "html"
    
    suffix = tail.split(".")[-1]
    if suffix in ['html', 'htm', 'shtml', 'php', 'com', 'org', 'edu', 'gov']:
        return "html"
    elif suffix in ['jpg','gif','png','svg','PNG']:
        return "image"
    elif suffix in ['mp3','wav','wma','ogg']:
        return "audio"
    elif suffix in ['mp4', 'mkv', 'ogv', 'webm']:
        return "video"
    elif suffix in ['pdf', 'doc', 'docx', 'txt']:
        return "document"
    elif suffix in ['asp', 'aspx']:
        return "asp"
    elif "wikipedia" in url:
        return "html"
    else:
        return "other"


def print_time_elapsed(start_time):
    curr_time = time.time()
    total_time = (curr_time - start_time)/60  # minutes
    
    if total_time < 1:  # convert to seconds
        total_time *= 60
        print('Time Elapsed: ' + str(total_time)[:6] + ' sec\n')
    else:
        print('Time Elapsed: ' + str(total_time)[:6] + ' min\n')

def save_data(data, file_path):
    f = open(file_path,"wb")
    pickle.dump(data, f)
    f.close()   

def load_data(file_path):
    f = open(file_path,"rb")
    data = pickle.load(f)
    f.close()
    return data

if __name__ == '__main__':
    seeds = ['https://www.nobelprize.org', 
    'https://en.wikipedia.org/wiki/Nobel_Prize', 
    'https://www.britannica.com/topic/Nobel-Prize', 
    'https://www.facebook.com/nobelprize/', 
    'https://www.nytimes.com/topic/subject/nobel-prizes']
    
    N = 20000
    link_dict = crawl(seeds, N)

    file_path = "link_dict_20k.pickle"
    save_data(link_dict, file_path)
    print("Results saved to file:", file_path)

    # extract_links('https://www.youtube.com/watch')
   

    # print (get_link_type("https://upload.wikimedia.org/wikipedia/commons/b/be/Announcement_Nobelprize_Literature_2009-1.ogv"))
    # print(extract_links("https://en.wikipedia.org/wiki/File:Worldmapnobellaureatesbycountry2.PNG")[0])
    