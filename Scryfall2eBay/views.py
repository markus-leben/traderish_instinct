from django.shortcuts import render, redirect
import requests
import time
from .forms import CardForm
import urllib
import csv
import datetime
from django.http import HttpResponse

# Todo: Add full art to names, fix dfc bug
# Todo: can you just pass the information from the initial scryfall search in and not bother looking it up again in the save function?

FOILDICT = {
                    "foil": "Foil ",
                    "nonfoil": "",
                    "etched": "Etched Foil ",
                    "glossy": "Glossy Foil ",
                }


def index(request):

    card_search_arr = []

    if request.method == 'POST':
        form = CardForm(request.POST)
    else:
        form = CardForm()
    print(form.is_valid())
    if form.has_changed():
        url = "https://api.scryfall.com/cards/search?q={}"
        if form.cleaned_data['name'] != "":
            r = requests.get(url.format(form.cleaned_data['name'])).json()
        else:
            r = {} # blank dict becuase success also serves a dict
        # print(r)
        time.sleep(.1)
        r_arr = []
        if 'data' in r:
            for i in r['data']:
                for j in requests.get(i["prints_search_uri"]).json()['data']:
                    r_arr.append(j)
                    time.sleep(.1)

            for i in r_arr:
                if not('paper' in i['games']):
                    continue
                # print(i)
                if 'promo_types' in i:
                    promo_types = i['promo_types']
                else:
                    promo_types = {}
                promo_dir = {'prerelease':'Prerelease Promo ',
                             'promopack': 'Promo Pack ',}
                promo_str = ""
                for j in promo_dir:
                    if j in promo_types:
                        promo_str += promo_dir[j]
                if promo_str == "" and i['promo']:
                    promo_str = "Promo "

                if "card_faces" in i:
                    card_text = "%s // %s" % (i['card_faces'][0]['oracle_text'], i['card_faces'][1]['oracle_text'])
                    small_img = i['card_faces'][0]['image_uris']['small']
                    large_img = i['card_faces'][0]['image_uris']['large']
                else:
                    card_text = i['oracle_text']
                    small_img = i['image_uris']['small']
                    large_img = i['image_uris']['large']

                full_art_str = ""
                if i['full_art']:
                    full_art_str = "Full Art "

                for j in i["finishes"]:
                    curr_card = {
                        'name': "%s%s%s " % (full_art_str, FOILDICT[j], i['name']),
                        'set': "%s%s" % (promo_str, i['set_name'].replace(' Promos','')),
                        'text': card_text,
                        'small_img': small_img,
                        'large_img': large_img,
                        'url': urllib.parse.quote(i['uri']),
                        'foil': j,
                        'scryf_data': i,
                    }
                    card_search_arr.append(curr_card)

    saved_card_arr = []
    if 'saved_card_arr' in request.session:
        for i in request.session['saved_card_arr']:
            saved_card_arr.append(i)
    #         r = requests.get(urllib.parse.unquote(i)).json()
    #         # print(r)
    #         if 'promo_types' in r:
    #             promo_types = r['promo_types']
    #         else:
    #             promo_types = {}
    #         promo_dir = {'prerelease':'Prerelease Promo ', 'promopack': 'Promo Pack '}
    #         promo_str = ""
    #         for j in promo_dir:
    #             if j in promo_types:
    #                 promo_str += promo_dir[j]
    #         if promo_str == "" and r['promo']:
    #             promo_str = "Promo "
    #
    #         saved_card = {
    #             'name': r['name'],
    #             'set': "%s%s" % (promo_str, r['set_name'].replace(' Promos','')),
    #             'text': r['oracle_text'],
    #             'small_img': r['image_uris']['small'],
    #             'large_img': r['image_uris']['large'],
    #             'url': urllib.parse.quote(r['uri']),
    #             'scryf_data': i,
    #         }
    #         saved_card_arr.append(saved_card)
    #         pass

    context = {"card_search_arr": card_search_arr, 'form': form, "saved_card_arr": saved_card_arr}
    response = render(request, "Scryfall2eBay/Scryfall2eBay.html", context)

    return response


def save_card(request, card_url, foil_value):

    r = requests.get(urllib.parse.unquote(card_url)).json()
    print(r)

    if 'promo_types' in r:
        promo_types = r['promo_types']
    else:
        promo_types = {}
    promo_dir = {'prerelease':'Prerelease Promo ', 'promopack': 'Promo Pack '}
    promo_str = ""
    for j in promo_dir:
        if j in promo_types:
            promo_str += promo_dir[j]
    if promo_str == "" and r['promo']:
        promo_str = "Promo "

    if "card_faces" in r:
        card_text = "%s // %s" % (r['card_faces'][0]['oracle_text'], r['card_faces'][1]['oracle_text'])
        small_img = r['card_faces'][0]['image_uris']['small']
        large_img = r['card_faces'][0]['image_uris']['large']
    else:
        card_text = r['oracle_text']
        small_img = r['image_uris']['small']
        large_img = r['image_uris']['large']
    full_art_str = ""
    if r['full_art']:
        full_art_str = "Full Art "

    saved_card = {
        'name': "%s%s%s" % (full_art_str, FOILDICT[foil_value], r['name']),
        'set': "%s%s" % (promo_str, r['set_name'].replace(' Promos','')),
        'text': card_text,
        'small_img': small_img,
        'large_img': large_img,
        'url': urllib.parse.quote(r['uri']),
        'foil': foil_value,
        'scryf_data': r,
    }

    if 'saved_card_arr' in request.session:
        old_sesh = request.session['saved_card_arr']
        old_sesh.append(saved_card)
        request.session['saved_card_arr'] = old_sesh
    else:
        request.session['saved_card_arr'] = [saved_card]

    # print(request.session['url_arr'])
    return redirect('home')


def del_nth_row(request, row_index):
    old_sesh = request.session['saved_card_arr']
    del old_sesh[int(row_index)]
    request.session['saved_card_arr'] = old_sesh
    return redirect('home')


def del_all_rows(request):
    request.session['saved_card_arr'] = []
    return redirect('home')


def send_ebay_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="ebay_csv%s.csv"' % datetime.datetime.now()},
    )

    writer = csv.writer(response)
    writer.writerow(['Info', 'Version=1.0.0', 'Template=fx_category_template_EBAY_US'])
    firstrow = ['*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)',
                'ScheduleTime',
                '*Location',

                '*Title',
                '*StartPrice',
                '*Description',

                '*Category',
                '*Format',
                '*Duration',
                '*Quantity',
                '*ReturnsAcceptedOption',
                'PicURL',

                'ShippingType',
                'ShippingService-1:Option',
                'ShippingService-1:Cost',
                '*DispatchTimeMax',

                '*ConditionID',
                '*C:Game',
                '*C:Graded',
                '*C:Card Name',
                '*C:Card Type',
                '*C:Character',
                '*C:Set',
                '*C:Features',
                '*C:Attribute/MTG:Color',
                '*C:Grade',
                '*C:Finish',
                '*C:Rarity',
                '*C:Manufacturer',
                '*C:Creature/Monster Type',
                '*C:Professional Grader',
                '*C:Card Condition',
                '*C:Autographed',
                '*C:Card Number',
                '*C:Certification Number',
                'C:Attack/Power',
                'C:Defense/Toughness'
                ]
    writer.writerow(firstrow)
    if 'saved_card_arr' in request.session:
        for i in request.session['saved_card_arr']:
            write_arr = []
            row_dict = {}

            # Stuff to write into excel goes here
            row_dict['*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)'] = "Add"
            row_dict['ScheduleTime'] = \
                (datetime.datetime.now() + datetime.timedelta(days=21)).strftime("%Y-%m-%d %H:%M:%S")
            row_dict['*Location'] = 'United States'

            row_dict['*Title'] = '%s %s NM' % (i['name'], i['set'])
            if len(row_dict['*Title']) > 80:
                row_dict['*Title'] = row_dict['*Title'][:79]
            row_dict['*StartPrice'] = '0.01'
            row_dict['*Description'] = "Listed automatically using Traderish Instinct and Scryfall's API. \n" \
                                       "Please note that the card images are stock images. \n" \
                                       "More images available on request. \n"

            row_dict['*Category'] = "183454"
            row_dict['*Format'] = 'FixedPrice'
            row_dict['*Duration'] = 'GTC'
            row_dict['*Quantity'] = '1'
            row_dict['*ReturnsAcceptedOption'] = 'ReturnsAccepted'
            row_dict['PicURL'] = i['large_img']

            row_dict['ShippingType'] = 'Flat'
            row_dict['ShippingService-1:Option'] = 'USPSFirstClass'
            row_dict['ShippingService-1:Cost'] = '1.00'
            row_dict['*DispatchTimeMax'] = '3'

            row_dict['*ConditionID'] = 3000
            row_dict['*C:Game'] = 'Magic: The Gathering'
            row_dict['*C:Graded'] = 'No'
            row_dict['*C:Card Name'] = i['scryf_data']['name']
            row_dict['*C:Card Type'] = i['scryf_data']['type_line'].split("—")[0]
            row_dict['*C:Character'] = ""
            row_dict['*C:Set'] = i['scryf_data']['set_name']
            row_dict['*C:Features'] = ""

            color_dict = {
                'W': 'white',
                'U': 'blue',
                'B': 'black',
                'R': 'red',
                'G': 'green',
            }
            if "card_faces" in i['scryf_data']:
                color_arr = []
                for face in i['scryf_data']["card_faces"]:
                    for color in face['colors']:
                        if not color in color_arr:
                            color_arr.append(color)
            else:
                color_arr = i['scryf_data']['colors']
            if len(color_arr) == 0:
                row_dict['*C:Attribute/MTG:Color'] = 'Colorless'
            elif len(color_arr) == 1:
                row_dict['*C:Attribute/MTG:Color'] = color_dict[color_arr[0]]
            else:
                row_dict['*C:Attribute/MTG:Color'] = 'multicolor'

            row_dict['*C:Grade'] = "N/A"
            row_dict['*C:Finish'] = i['foil']
            row_dict['*C:Rarity'] = i['scryf_data']['rarity']
            row_dict['*C:Manufacturer'] = "Wizards of the Coast"
            if len(i['scryf_data']['type_line'].split("—")) > 1:
                row_dict['*C:Creature/Monster Type'] = i['scryf_data']['type_line'].split("—")[1]
            row_dict['*C:Professional Grader'] = "N/A"
            row_dict['*C:Card Condition'] = "Near Mint or Better"
            row_dict['*C:Autographed'] = "No"
            row_dict['*C:Card Number'] = i['scryf_data']['collector_number']
            row_dict['*C:Certification Number'] = "N/A"

            for head_name in firstrow:
                arr_appender = ""
                for val in row_dict:
                    if val == head_name:
                        arr_appender = row_dict[val]
                write_arr.append(arr_appender)
            writer.writerow(write_arr)

    return response

