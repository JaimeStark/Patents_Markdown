#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
uspatentmd.py

Created by Jaime Stark on 1/30/2021

This script comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to
redistribute it under certain conditions.
See 'LICENSE.txt' for details.

DESCRIPTION
This script generates a summary of a U.S. Patent or Patent Publication
in markdown format based only on the patent or publication number.
The script is intended for easy input into a markdown-based
notetaking program like Obsidian (https://obsidian.md).

The resulting Patent Term Adjustment, Terminal Disclaimer, and
Prosecution History PDF fields have placeholders that are intended to 
be edited manually.

Requires installation of BeautifulSoup4 python package.  To install 
BeautifulSoup4 in python3, type:
pip3 install BeautifulSoup4

USAGE
python3 uspatentmd [PATENT NUMBER] > [FILENAME.md]
"""



import requests
from bs4 import BeautifulSoup
import sys

patent_input = str(sys.argv[1]).upper()
patent_input = patent_input.replace(" ", "")
patent_input = patent_input.replace("/", "")
patent_input = patent_input.replace(",", "")
patent_input = patent_input.replace("US", "")

url_string = f'https://patents.google.com/patent/US{patent_input}'

try:
    page = requests.get(url_string).content
    soup = BeautifulSoup(page, "html.parser")
except:
    sys.stdout.write("Patent Number Not Found")
    sys.exit()

def get_patent_num(soup):
    """Gets the number of the """
    return(soup.find('meta', itemprop='numberWithoutCodes')['content'])

def get_title(soup):
    return(soup.find('span', itemprop="title").text)

def get_abstract(soup):
    func_soup = soup
    for abstract in func_soup.find_all('abstract'):
            for img in abstract('img'):
                img_link = img['src']
                img_text = img['id']
                img_md = "![{}]({})".format(img_text, img_link)
                img.replace_with(img_md)
    abstract = abstract.text
    return(abstract)

def get_inventors(soup):
    inventors = ""
    inventor_list = soup.find_all(itemprop="inventor")
    for count, inventor in enumerate(inventor_list):
        inventors += inventor.text
        if count != len(inventor_list)-1:
            inventors += ", "
    return(inventors)

def get_application_num(soup):
    return(soup.find('dd', itemprop="applicationNumber").text)

def get_app_publication_num(soup):
    associations = soup.find('dd', itemprop="directAssociations")
    try:
        pub_num = associations.find(itemprop="publicationNumber").text
        return(pub_num)
    except:
        return("N/A")
    

def get_priority_date(soup):
    date = "N/A"
    date = soup.find(itemprop="priorityDate").text
    return(date)

def get_filing_date(soup):
    date = "N/A"
    events = soup.find_all(itemprop="events")
    for event in events:
        if event.find('span', itemprop="type").text == "filed":
            date = event.find('time').text
    return(date)

def get_publication_date(soup):
    date = "N/A"
    date = soup.find(itemprop="publicationDate").text
    return(date)


def get_app_publication_date(soup, pub_num):
    date = "N/A"
    pubs = soup.find_all('tr', itemprop="pubs")
    for pub in pubs:
        if pub_num in pub.find(itemprop="publicationNumber").text:
            date = pub.find(itemprop="publicationDate").text
            return(date)
            break
        else:
            continue
    return("N/A")

def get_grant_date(soup):
    date = "N/A"
    events = soup.find_all(itemprop="events")
    for event in events:
        if event.find('span', itemprop="type").text == "granted":
            date = event.find('time').text
    return(date)

def get_expiration_date(soup):
    date = "N/A"
    events = soup.find_all(itemprop="events")
    for event in events:
        if event.find('span', itemprop="title").text == "Anticipated expiration":
            date = event.find('time').text
        elif event.find('span', itemprop="title").text == "Adjusted expiration":
            date = event.find('time').text
    return(date)

def get_original_assignee(soup):
    assignee = "N/A"
    events = soup.find_all(itemprop="events")
    for event in events:
        if event.find('span', itemprop="type").text == "filed":
            assignee = event.find('span', itemprop="assigneeSearch").text.title()
    return(assignee)

def get_pdf_link(soup):
    link = soup.find('a', itemprop="pdfLink")['href']
    return(link)

def get_priority_apps(soup, application_num):
    priority_apps = "N/A"
    apps_list = []
    priority_apps_list = soup.find_all('tr', itemprop="priorityApps")
    for priority_app in priority_apps_list:
        app_num = priority_app.find('span', itemprop="applicationNumber").text
        apps_list.append(app_num)
    try:
        apps_list.remove("US"+application_num)
    except:
        pass
    for count, num in enumerate(apps_list):
        priority_apps = priority_apps.replace("N/A", "")
        priority_apps += num
        if count != len(apps_list)-1:
            priority_apps += "; "
    return(priority_apps)

def get_claim_count(soup):
    claim_count = "0"
    headings = soup.find_all('h2')
    for heading in headings:
        if "Claims (" in heading.text:
            claim_count = heading.find('span', itemprop="count").text
    return(claim_count)

def get_claims(soup):
    func_soup = soup
    claims_text = []
    claims_soup = func_soup.find_all('div', class_="claim", id=None)
    for claim_soup in claims_soup:
        for div_list in claim_soup.select('div', class_='claim-text'):
            for img in div_list('img'):
                img_link = img['src']
                img_text = img['id']
                img_md = "![{}]({})".format(img_text, img_link)
                img.replace_with(img_md)
        claim = claim_soup.text
        claim = claim.rstrip().lstrip()
        claim = claim.replace(": \n", ":\n")
        claim = claim.replace("; and", ";and")
        claim = claim.replace("; ", ";\n")
        claim = claim.replace(";and ", "; and\n")
        claim = claim.replace(";and", "; and")
        claim = claim.replace("\n\n", "\n")
        claim = claim.replace("\n", "\n\t- ")
        claim = claim.replace("\t- \n", "")
        claim = claim.replace("\t-  \n", "")
        claim = "### Claim " + claim
        claim = claim.replace(". ", "\n- ", 1)
        claims_text.append(claim)
    return(claims_text)

def if_application(num):
    if len(num) >8:
        return(True)
    else:
        return(False)


patent_num_only = get_patent_num(soup)
is_application = if_application(patent_num_only)
patent_num_comma = str(f'{int(patent_num_only):,}')
patent_num_slash = patent_num_only[:4] + "/" + patent_num_only[4:]
patent_num_end = "’" + str(patent_num_only)[-3:]
title = get_title(soup).replace("\t", "").replace("\n", "").rstrip()
abstract = get_abstract(soup)
inventors = get_inventors(soup)
app_num_comma = get_application_num(soup).replace("US", "")
app_num_only = app_num_comma.replace(",", "")
app_num_noslash = app_num_only.replace("/", "")
app_num_us = "US" + app_num_only
app_pub_num_full = get_app_publication_num(soup)
if app_pub_num_full == "N/A":
    app_pub_num = "N/A"
    app_pub_num_us = "N/A"
    app_pub_num_slash = "N/A"
else:
    app_pub_num = app_pub_num_full[2:-2]
    app_pub_num_slash = app_pub_num[:4] + "/" + app_pub_num[4:]
    app_pub_num_us = "US" + app_pub_num_slash
priority_date = get_priority_date(soup)
filed_date = get_filing_date(soup)
publication_date = get_publication_date(soup)
app_publication_date = get_app_publication_date(soup, app_pub_num)
grant_date = get_grant_date(soup)
expiration_date = get_expiration_date(soup)
assignee = get_original_assignee(soup)
pdf = get_pdf_link(soup)
priority_apps = get_priority_apps(soup, app_num_comma)
total_claims = get_claim_count(soup)
claims = get_claims(soup)
ind_claims_count = str(len(claims))
if is_application & (grant_date != "N/A"):
    issued_patent = "US" + app_pub_num 
else:
    issued_patent = "N/A"

claim_text = ""	
for claim in claims:
    claim_text += claim + "\n"
if is_application:
    uspto_pdf_num = patent_num_only[-2:] + "/" + patent_num_only[:4] + "/" + patent_num_only[-4:-2] + "/" + patent_num_only[-7:-4] + "/0.pdf"
else:
    pdf_num = patent_num_only
    while len(pdf_num) < 8:
        pdf_num = "0" + pdf_num
    uspto_pdf_num = pdf_num[-2:] + "/" + pdf_num[-5:-2] + "/" + pdf_num[-8:-5] + "/0.pdf"


if is_application:
    note1 = f"""---
title: U.S. Pat. App. No. {patent_num_only}
aliases: ["US{patent_num_only}", "US {patent_num_only}", "US{patent_num_slash}", "US {patent_num_slash}", "{patent_num_end}", "{patent_num_end} Application", "{app_num_comma}", "US{app_num_only}", "US{app_num_comma}", "US {app_num_only}", "US {app_num_comma}"]
tags: [Legal/Patents/US_Application]
---
# U.S. Patent Application No. {patent_num_slash}
- **Type**: U.S. Patent Application
- **Title**: {title}
- **Inventors**: {inventors}
- **Original Assignee**: {assignee}
- **Application No.**: US{app_num_only}
- **App. Publication No.**: US{patent_num_slash}
- **App. Publication Date**: {publication_date}
- **Priority Date**: {priority_date}
- **Filing Date**: {filed_date}
- **Issued Patent**: {issued_patent}
- **Issue Date**: {grant_date}
- **Priority Documents**: {priority_apps}
- **Links**: [Google Patents](https://patents.google.com/patent/US{patent_num_only}) |  [USPTO AppFT](http://appft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&Sect2=HITOFF&p=1&u=/netahtml/PTO/srchnum.html&r=1&f=G&l=50&d=PG01&s1={patent_num_only}.PGNR.) | [USPTO Patent Center](https://patentcenter.uspto.gov/#!/applications/{app_num_noslash}) | [USPTO Assignment](https://assignment.uspto.gov/patent/index.html#/patent/search/resultAbstract?id={patent_num_only}&type=patNum)
- **Publication PDF**: [Google Patents]({pdf}) | [USPTO](https://pdfaiw.uspto.gov/fdd/{uspto_pdf_num})
- **Prosecution History PDF**: ---

## Abstract
{abstract}

##  Claims
- **Total Claims**: {total_claims}
- **Independent Claims**: {ind_claims_count}

{claim_text}
## Notes
### Prosecution History Notes
- N/A

### Assignment History Note
- N/A

### Additional Notes
- N/A
"""
else:
    note1 = f"""---
title: U.S. Pat. No. {patent_num_comma}
aliases: ["{patent_num_comma}", "US {patent_num_comma}", "US{patent_num_only}", "US {patent_num_only}", "{patent_num_end}", "{patent_num_end} Patent", "{app_num_comma}", "US{app_num_only}", "US{app_num_comma}", "US {app_num_only}", "US {app_num_comma}"]
tags: [Legal/Patents/US_Patent]
---
# U.S. Patent No. {patent_num_comma}
- **Type**: U.S. Patent
- **Title**: {title}
- **Inventors**: {inventors}
- **Original Assignee**: {assignee}
- **Application No.**: US{app_num_only}
- **App. Publication No.**: US{app_pub_num_slash}
- **App. Publication Date**: {publication_date}
- **Priority Date**: {priority_date}
- **Filing Date**: {filed_date}
- **Issued Patent**: US{patent_num_only}
- **Issue Date**: {grant_date}
- **Anticipated Expiration**: {expiration_date}
- **Patent Term Adjustment**: ==X== days
- **Terminal Disclaimer**: ==Yes/No==
- **Priority Documents**: {priority_apps}
- **Links**: [Google Patents](https://patents.google.com/patent/US{patent_num_only}) | [USPTO PatFT](https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&Sect2=HITOFF&p=1&u=/netahtml/PTO/srchnum.html&r=1&f=G&l=50&d=PALL&s1={patent_num_only}.PN.) | [USPTO Patent Center](https://patentcenter.uspto.gov/#!/applications/{app_num_noslash}) | [USPTO Assignment](https://assignment.uspto.gov/patent/index.html#/patent/search/resultAbstract?id={patent_num_only}&type=patNum)
- **Publication PDF**: [Google Patents]({pdf}) | [USPTO](https:/pimg-fpiw.uspto.gov/fdd/{uspto_pdf_num})
- **Prosecution History PDF**: ---

## Abstract
{abstract}

##  Claims
- **Total Claims**: {total_claims}
- **Independent Claims**: {ind_claims_count}

{claim_text}
## Notes
### Prosecution History Notes
- N/A

### Assignment History Note
- N/A

### Additional Notes
- N/A
"""

sys.stdout.write(note1)