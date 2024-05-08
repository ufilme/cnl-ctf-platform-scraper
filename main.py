import sys
from Scraper import Scraper

if __name__ == "__main__":
    runner = Scraper(sys.argv[1])
    runner.login()
    runner.get_challenges()
