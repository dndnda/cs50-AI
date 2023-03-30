import os
import random
import re
import sys


DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    
    #print(transition_model(corpus, "1.html", 0.8))
    
    #print(corpus)

def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    if len(corpus[page]) == 0:
        prob_dictribution = dict.fromkeys(corpus.keys(), 1/len(corpus))
    else:
        prob_dictribution = dict.fromkeys(corpus.keys(), (1 - damping_factor)/len(corpus))
        for p in corpus[page]:
            prob_dictribution[p] += damping_factor/len(corpus[page])
    return prob_dictribution





def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    


    pagerank = dict.fromkeys(corpus, 0)
    nextpage = random.choice(list(corpus.keys()))
    pagerank[nextpage] += 1
    for _ in range(n - 1):
        dist = transition_model(corpus, nextpage, damping_factor)
        dist_list = list(dist.keys())
        dist_weights = [dist[i] for i in dist]
        nextpage = random.choices(dist_list, dist_weights, k=1)[0]
        pagerank[nextpage] += 1
    for item in pagerank:
        pagerank[item] /= n
    
    return pagerank

def can_stop(pagerank1, pagerank2):
    for p in pagerank1:
        if abs(pagerank1[p] - pagerank2[p]) > 0.001:
            return False
    
    return True


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict.fromkeys(corpus.keys(), 1/len(corpus))
    page_num = len(corpus)

    def PR(page, pagerank_):
        tmp = (1 - damping_factor)/page_num
        
        for p in corpus:
            if len(corpus[p]) == 0:
                tmp += damping_factor * pagerank_[p]/len(corpus)
            elif page in corpus[p]:
                tmp += damping_factor * pagerank_[p]/len(corpus[p])
        pagerank_[page] = tmp

    while 1:
        pagerank_copy = pagerank.copy()
        for page in pagerank_copy:
            PR(page, pagerank_copy)
        if can_stop(pagerank, pagerank_copy):
            return pagerank
        else:
            pagerank = pagerank_copy 
    




if __name__ == "__main__":
    main()
