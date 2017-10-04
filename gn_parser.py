import urllib.request
import re
import argparse
import csv

# Configuration
# Country page
section_url_re = re.compile('(/headlines/section/topic/[^?]+\?ned=[^"]*)')
section_name_re = re.compile('(?:/topic/)(\w+)')
country_id_re = re.compile('<content class="vRMGwf">([^&]*)')
# Section page
full_coverage_url_re = re.compile('href="(story/[^?]+\?ned=[^"]*)')
# Full Coverage page
origin_name_re = re.compile('<span class="IH8C7b Pc0Wt"[^>]*>([^<]*)')
origin_url_re = re.compile('<a class="nuEeue hzdq5d ME7ew" target="_blank" href="([^"]*)')

all_links = True
# End of configuration

country_id = None
# Extra functions
def purify_list(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# Functions for each step of parsing

def fetch_sections(page_link): # returns dictionary of 'sectiona name' : 'url'

    response = urllib.request.urlopen(page_link)
    if response.status != 200:
        print('Bad HTTP response status. Exiting...')
        exit(-1)

    response_html = response.read()

    # with open('test.html', 'w', encoding='utf-8') as file:
    #    file.write(response_html.decode('utf-8', 'ignore'))
    #    file.close()
    section_urls = list(map(lambda url: 'http://news.google.com/news' + url, purify_list(section_url_re.findall(response_html.decode('utf-8', 'ignore')))))
    sections = dict()
    for url in section_urls:
        sections[section_name_re.search(url).group(1)] = url
    global country_id
    country_id = str(country_id_re.search(response_html.decode('utf-8', 'ignore')).group(1))
    print(country_id)

    return sections


def fetch_vfc_urls(section_url):
    sec_response = urllib.request.urlopen(section_url)
    if sec_response.status != 200:
        print('Bad HTTP response status. Exiting...')
        exit(-1)

    sec_html = sec_response.read()
    vfc_urls = list(set(full_coverage_url_re.findall(sec_html.decode('utf-8', 'ignore'))))
    vfc_urls = list(map(lambda url: 'http://news.google.com/' + url, list(vfc_urls)))
    # print('For:\n', sec_dict[sec_name],'\nView Full Coverage:')
    return vfc_urls

def fetch_origins(vfc_url):
    response = urllib.request.urlopen(vfc_url)
    if response.status != 200:
        print('Bad HTTP response status. Exiting...')
        exit(-1)

    response_html = response.read()

    origin_names = list(origin_name_re.findall(response_html.decode('utf-8', 'ignore')))
    origin_urls = list(origin_url_re.findall(response_html.decode('utf-8', 'ignore')))
    print(len(origin_names), len(origin_urls))
    # input()
    origins = dict()
    i = 0
    # print(len(origin_names), len(origin_urls))
    for name in origin_names:
        if all_links:
            if name not in origins:
                origins[name] = list()
            origins[name].append(origin_urls[i])
        else:
            origins[name] = origin_urls[i]
        i += 1
    return origins


# Main code
origins = dict() # list of all origins and all their links

# Kind of interface
parser = argparse.ArgumentParser(description='Parses origins from google news.')
parser.add_argument('-u', help='URL of country page in google news')
parser.add_argument('-c', help='Country name')
args = parser.parse_args()
if args.u is None:
    # print('No (-u)rl mentioned.')
    parser.print_help()
    exit(-1)

# Step 1. Parse sections names and urls.
country_page_url = args.u



sections = fetch_sections(country_page_url)

if args.c is not None:
    country_id = args.c

# User output.
print('Found', len(sections),'sections:')
for name in sections:
    print(name)


csv_file = open('origins_' + country_id + '.cvs', 'w', encoding='utf-8')
csv_writer = csv.writer(csv_file)
# csv_writer.writerow(['Origin Name', 'Url', 'Section', 'Country'])
# csv_file.close()
# exit()

# Steps 2-3. Parse 'View Full Coverage' links for each event in each section. Fetch origins info from each VFC page.
for section_name in sections:
        # Step 2.
        vfc_links = fetch_vfc_urls(sections[section_name])

        # User output.
        print('In section', section_name, 'found', len(vfc_links), 'urls:')
        for url in vfc_links:
            print(url)

        # Step 3.
        for url in vfc_links:
            new_origins = fetch_origins(url)
            for origin in new_origins:
                if all_links:
                    if origin not in origins:
                        origins[origin] = list()
                    origins[origin]+=(new_origins[origin])
                else:
                    if origin not in origins:
                        origins[origin] = new_origins[origin]
                
        # for item in origins:
        #    print(item)
        # input()
        for item in origins:
            if all_links:
                for i in range(0,len(origins[item])):
                    csv_writer.writerow([item, origins[item][i], country_id, section_name])
            else:
                csv_writer.writerow([item, origins[item], country_id, section_name])

csv_file.close()
print('Done!')
