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
    
    """
    Calculate the probability distribuition of the pages by the links
    """
    prob_dist = {}
    pages = corpus.keys()
    num_pages = len(pages)

    links = corpus[page] if corpus[page] else pages
    num_links = len(links)

    for p in pages:
        prob_dist[p] = (1 - damping_factor) / num_pages

    for linked_page in links:
        prob_dist[linked_page] += damping_factor / num_links

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    visit_count = {page: 0 for page in corpus}
    
    current_page = random.choice(list(corpus.keys()))
    
    for _ in range(n):
        visit_count[current_page] += 1
        
        prob_dist = transition_model(corpus, current_page, damping_factor)
        
        current_page = random.choices(list(prob_dist.keys()), weights=prob_dist.values())[0]
    
    total_visits = sum(visit_count.values())
    pagerank = {page: visit_count[page] / total_visits for page in corpus}

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pagerank = {page:1 / N for page in corpus}
    threshold = 0.001

    while True:
        new_pagerank = {}
        max_change = 0

        for page in corpus:
            new_rank = (1-damping_factor)/N

            for linking_page in corpus:
                links = corpus[linking_page]
                
                if len(links) == 0:
                    links = corpus.keys()
                
                if page in links:
                    new_rank += damping_factor * (pagerank[linking_page]/len(links))

            new_pagerank[page] = new_rank
            max_change = max(max_change,abs(new_pagerank[page] - pagerank[page]))

        pagerank = new_pagerank

        if max_change < threshold:
            break
    return pagerank


if __name__ == "__main__":
    main()
