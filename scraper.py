import urllib2, re, csv
from bs4 import BeautifulSoup

scraped_file = 'scrapings.csv'
base_url = 'http://www.photolib.noaa.gov/brs/'

page = 'rfind%s.htm' # % page_no


page_no = 1
while True:
    url = base_url + page % page_no
    print "scraping %s ---------->" % url
    page_no = page_no + 1

    try:
        soup = BeautifulSoup(urllib2.urlopen(url).read())
    except urllib2.HTTPError:
        print "no more pages! "
    
    all_images = soup.find_all('img', src=True)[9:]  # first 9 links are nav

    for image in all_images:
        src = image.attrs['src']
        img_id = src.split('/')[-1].split('.')[0]

        # with img_id we know some urls..
        hi_res = 'http://www.photolib.noaa.gov/bigs/%s.jpg' % img_id
        modest = 'http://www.photolib.noaa.gov/700s/%s.jpg' % img_id
        detail_url = 'http://www.photolib.noaa.gov/htmls/%s.htm' % img_id

        print detail_url
        # script eh image's detail page to get the photo credit, title
        detail_soup = BeautifulSoup(urllib2.urlopen(detail_url).read())
        title = detail_soup.find_all('p')[2].get_text().strip()

        if not title:
            try:
                m = re.search('Location:(.*)', detail_soup.get_text())
                title = m.group(1).strip()
            except AttributeError:
                title = "Image from NOAA's Coral Kingdom Collection"

        try:
            m = re.search('Photographer:(.*)', detail_soup.get_text())
            credit = m.group(1).strip()
        except AttributeError:
            try:
                m = re.search('Credit:(.*)', detail_soup.get_text())
                credit = m.group(1).strip()
            except AttributeError:
                credit = 'NOAA'

        # remove commas that will mess with the csv
        title = title.replace(',',' ')
        credit = credit.replace(',',' ')

        image_info = (img_id, title, credit, detail_url, hi_res, modest)

        with open(scraped_file, 'a') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(list(image_info))
