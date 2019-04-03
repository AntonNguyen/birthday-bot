# -*- coding: utf-8 -*-
import datetime
from icalendar import Calendar
import os
import random
import re
import requests

def convert_name(name):
    name = name.strip()
    name_mapping = [
        ('Caitlin Stewart', 'Cait Stewart'),
        ('Dan Li', 'Danni Li'),
        ('Dave Cosgrave', 'David Cosgrave'),
        ('Douglas Lawson', 'Doug Lawson'),
        ('Francisco Arizmendi', 'Paco Arizmendi'),
        ('Geoff Oakham', 'Geoffrey Oakham'),
        ('Gwendolyn Myall', 'Gwen Myall'),
        ('John Johnston', 'Marshall Johnston'),
        ('Josh McStay-Cooney', 'Josh Cooney'),
        ('Joshua Brinksman', 'Josh Brinksman'),
        ('Kriscel Natividad', 'Kae Natividad'),
        ('Kyungjoo Lee', 'KJ Lee'),
        ('Matthew Barnes', 'Matt Barnes'),
        ('Minh To', 'Victor To'),
        ('Oloruntobi Ogunbiyi', 'Tobi Ogunbiyi'),
        ('Oluwatobiloba Abiodun', 'Tobi Abiodun'),
        ('Philip Decelis', 'Phil Decelis'),
        ('Philip Yager', 'Hunter Yager'),
        ('Robert Przybyla', 'Bob Przybyla'),
        (u'Sherwyn Peña', 'Sherwyn Pena'),
        ('Steve Freudenthaler', 'Stephen Freudenthaler'),
        ('Sze Chit Wesley Ng', 'Wesley Ng'),
        ('Tanzibur Rahman', 'Tanzi Rahman'),
        ('Wayne Woo-Yam-Tung', 'Wayne Woo'),
        ('Ying Hao Xu', 'Andrew Xu'),
        ('Zach Solly', 'Zachary Solly')
    ]
    for old, new in name_mapping:
        name = name.replace(old, new)
    return name

def fetch_birthdays(cal, day):
    birthdays = []
    blacklist = [
        'John Stinson'
    ]

    for component in cal.walk('VEVENT'):
        day_string = component.get('DTSTART').dt.strftime('%m/%d')
        if day_string == day:
            summary = component.get('SUMMARY')
            name = summary.replace(' - Birthday', '')
            name = convert_name(name)
            if name not in blacklist:
                birthdays.append(name)

    return birthdays

def fetch_freshiversaries(cal, day):
    freshiversaries = []
    blacklist = [
        'Mike McDerment',
        'Levi Cooperman',
        'Joe Sawada',
        'John Stinson'
    ]

    for component in cal.walk('VEVENT'):
        day_string = component.get('DTSTART').dt.strftime('%m/%d')
        if day_string == day:
            summary = component.get('SUMMARY')
            matches = re.search('(.*) \((\d+) ', summary)
            if matches:
                name = convert_name(matches.group(1))
                years = matches.group(2)

                if name not in blacklist:
                    freshiversaries.append({
                        'name': name,
                        'years': years
                    })

    return freshiversaries

def get_image_for_name(image_list, name):
    for image, image_name in image_list:
        image_name = image_name.strip()
        if image_name == name:
            return image
    return ''

def get_shortened_name(name):
    return name.split(' ')[0]

def summarize_names(names):
    if len(names) == 1:
        return names[0]
    else:
        return ', '.join(names[:-1]) + ' and ' + names[-1]

def get_day_summary(day, birthdays, freshiversaries, question):
    summary = day + ' is '

    if len(birthdays) > 0:
        summary += summarize_names(birthdays)
        summary += '\'s birthday'
        if len(freshiversaries) > 0:
            summary += ' and '

    if len(freshiversaries) > 0:
        names = [freshiversary['name'] for freshiversary in freshiversaries]
        summary += summarize_names(names)
        summary += '\'s Freshiversary'

    summary += '. '
    summary += question

    return summary

def output_photos(birthdays, freshiversaries, images):
    output = ''

    if len(birthdays) > 0:
        output += '<div class="photoSection">'
        output += '<b>Birthdays</b>\n'
        for name in birthdays:
            output += '<div class="person">'
            output += '<img src="' + get_image_for_name(images, name) + '"><br />'
            output += get_shortened_name(name)
            output += '</div>'
        output += '</div>'
        output += '<div style="clear: both"></div><br />'

    if len(freshiversaries) > 0:
        output += '<div class="photoSection">'
        output += '<b>Freshiversaries</b>\n'
        for freshiversary in freshiversaries:
            output += '<div class="person">'
            output += '<img src="' + get_image_for_name(images, freshiversary['name']) + '"><br />'
            output += get_shortened_name(freshiversary['name']) + '<br />'
            output += '<span style="color: rgb(160, 160, 160)">'
            output += freshiversary['years'] + ' year'
            if freshiversary['years'] != '1':
                output += 's'
            output += '</span>'
            output += '</div>'
        output += '</div>'
        output += '<div style="clear: both"></div><br />'

    return output

def get_email_content(is_debug=False):
    output = ''

    random.seed(datetime.date.today().strftime('%j'))

    today = datetime.date.today().strftime('%m/%d')
    saturday = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%m/%d')
    sunday = (datetime.date.today() + datetime.timedelta(days=2)).strftime('%m/%d')

    day_of_week = datetime.date.today().strftime('%a')
    is_friday = (day_of_week == 'Fri')
    is_saturday = (day_of_week == 'Sat')
    is_sunday = (day_of_week == 'Sun')

    if is_debug:
        today = '09/22'
        saturday = ''
        sunday = ''

        is_friday = False
        is_saturday = False
        is_sunday = False

    if is_saturday or is_sunday:
        return ''

    response = requests.get(os.environ['BIRTHDAY_URL'])
    birthday_cal = Calendar.from_ical(response.text)

    response = requests.get(os.environ['FRESHIVERSARY_URL'])
    freshiversary_cal = Calendar.from_ical(response.text)

    today_birthdays = fetch_birthdays(birthday_cal, today)
    today_freshiversaries = fetch_freshiversaries(freshiversary_cal, today)

    saturday_birthdays = []
    saturday_freshiversaries = []

    sunday_birthdays = []
    sunday_freshiversaries = []

    if is_friday:
        saturday_birthdays = fetch_birthdays(birthday_cal, saturday)
        saturday_freshiversaries = fetch_freshiversaries(freshiversary_cal, saturday)

        sunday_birthdays = fetch_birthdays(birthday_cal, sunday)
        sunday_freshiversaries = fetch_freshiversaries(freshiversary_cal, sunday)

    show_today = (len(today_birthdays) > 0 or len(today_freshiversaries) > 0)
    show_saturday = (len(saturday_birthdays) > 0 or len(saturday_freshiversaries) > 0)
    show_sunday = (len(sunday_birthdays) > 0 or len(sunday_freshiversaries) > 0)

    if show_today or show_saturday or show_sunday:
        team_page = requests.get('https://www.freshbooks.com/about/team')
        team_page.encoding = 'utf-8'
        team_page_text = team_page.text.replace('Emmanuel &quot;Mio&quot; Ricafort', 'Mio Ricafort')
        execs = re.findall('<img data-src=([^ ]*) src="" id=".*?" class="lazy executive-image" alt="(.*?)"', team_page_text, flags=re.DOTALL)
        normals = re.findall('<div class="freshbooker.*?<img src="(.*?)" alt="(.*?)"', team_page_text, flags=re.DOTALL)
        images = execs + normals

        today_question, saturday_question, sunday_question = get_random_questions()

        output += '<style type="text/css">'
        output += 'h2 { font-size: 1.4em; margin: 10px 0 0 }'
        output += '.greeting { margin-bottom: 15px }'
        output += '.greeting + h2 { margin-top: 30px }'
        output += '.person { text-align: center; float: left; padding: 10px 8px 5px 0; }'
        output += '.person img { border-radius: 10px; padding-bottom: 6px; }'
        output += '.person, .person img { width: 85px }'
        output += '.goodbye { margin-top: 10px }'
        output += '.about { margin: 30px 0 15px; font-style: italic; color: rgb(175, 175, 175) }'
        output += '</style>'

        output += '<div class="greeting"><b>Morning FreshBookers!</b></div>'

        if show_today:
            if show_saturday or show_sunday:
                output += '<h2>Today</h2>\n'
            output += get_day_summary('Today', today_birthdays, today_freshiversaries, today_question)
            output += '\n\n\n'
            output += output_photos(today_birthdays, today_freshiversaries, images)

        if show_saturday:
            output += '<h2>Saturday</h2>\n'
            output += get_day_summary('Saturday', saturday_birthdays, saturday_freshiversaries, saturday_question)
            output += '\n\n\n'
            output += output_photos(saturday_birthdays, saturday_freshiversaries, images)

        if show_sunday:
            output += '<h2>Sunday</h2>\n'
            output += get_day_summary('Sunday', sunday_birthdays, sunday_freshiversaries, sunday_question)
            output += '\n\n\n'
            output += output_photos(sunday_birthdays, sunday_freshiversaries, images)

        output += '<div class="goodbye">'
        output += 'Much <3,\n'
        output += '\n'
        output += 'TimBot'
        output += '</div>'
        output += '<div class="about">'
        output += 'TimBot is an automated version of Timbo brought to life by Calvin.'
        output += '</div>'

        output = output.replace('\n', '<br />\n')

    return output

def get_random_questions():
    return random.sample([
        'Ask them what their favourite brand of toothbrush is!',
        'Ask them if they prefer waxed or unwaxed floss!',
        'Ask them if they own a pair of jean shorts!',
        'Ask them if they prefer hot or room temperature yoga!',
        'Ask them what they think about this weather we\'ve been having lately!',
        'Ask them if they\'d rather be the first time traveler or the first person on Mars!',
        'Ask them if they think that name brand Kleenex is worth it!',
        'Ask them if they prefer 2 or 3 ply toilet paper!',
        'Ask them if they would eat the moon if it was made of cheese!',
        'Ask them what their favourite boy band is!',
        'Ask them if they have any vacations planned!',
        # 'Ask them if they have any plans for the weekend!',
        'Ask them to compare apples and oranges!',
        'Ask them what their favourite fruit is!',
        # 'Give them the world\'s biggest high five!',
        'Ask them to tell you their best joke!',
        'Ask them to do long division!',
        'Ask them if they\'ve ever been to Moose Jaw!',
        'Ask them if they know any magic tricks!',
        'Ask them to show you their best dance move!',
        'Ask them if they believe in ghosts!',
        # 'Ask them what their favourite Toronto sports team is!',
        'Ask them what their favourite planet is!',
        'Ask them how long they can hold their breath!',
        'Ask them what their favourite karaoke song is!',
        'Ask them if they ever owned a Tamagotchi!',
        'Ask them what they\'re watching on Netflix!',
        'Ask them if they\'re afraid of heights!',
        'Ask them if they have any superpowers!',
        'Ask them to estimate the airspeed velocity of an unladen swallow!',
        'Ask them what their favourite candy is!',
        'Challenge them to a staring contest!',
        'Challenge them to a game of rock-paper-scissors!',
        'Ask them if they think that cilantro tastes like soap!',
        'Ask them if they\'ve been to any good concerts lately!',
        'Ask them if they prefer decaf or regular coffee!',
        'Ask them what their favourite kind of soup is!',
        'Ask them to name all 50 U.S. states!',
        'Ask them if they know the capital of Wyoming!',
        'Ask them if they had any nicknames as a kid!',
        'Ask them what their favourite animal is!',
        'Ask them how fast they can solve a Rubik\'s Cube!',
        'Ask them if they know anyone famous!',
        'Ask them if they believe in any conspiracy theories!',
        'Ask them if they\'ve played any good video games lately!',
        'Ask them if they know the best way to survive a zombie apocalypse!',
        'Ask them to name all of the elements in the periodic table!',
        # 'Ask them what their favourite restaurant in Toronto is!',
        'Ask them if they prefer bar or liquid soap!',
        'Ask them if they\'ve ever been an extra in a Hollywood movie!',
        'Ask them if they\'ve ever been to space!',
        'Ask them what their favourite 90\'s TV show is!',
        'Ask them how many of the 7 continents they\'ve been to!',
        'Challenge them to a freestyle rap battle!',
        'Ask them what their favourite vegetable is!',
        'Ask them to tell you about the best road trip they\'ve been on!',
        'Ask them if they own a drone!',
        # 'Ask them what their favourite restaurant close to the office is!',
        'Ask them if they\'ve ever won the lottery!',
        'Ask them if they own a boat!',
        'Ask them what the weirdest food they\'ve ever eaten is!',
        'Ask them to list the names of every FreshBooker!',
        'Ask them what their favourite SNL skit is!',
        'Ask them if they can do any celebrity impressions!',
        'Ask them if they\'ve ever been a contestant on Wheel of Fortune!',
        'Ask them if they know any secret handshakes!',
        # 'Ask them if they think that robots (like me!) will one day rule the earth mwahahaha!',
        'Ask them if they believe in aliens!',
        'Ask them if they\'ve ever seen a UFO!',
        'Ask them what their favourite cartoon was when they were a kid!',
        'Ask them if they\'re playing any rec sports this year!',
        'Ask them if they\'ve ever been a contestant on The Price is Right!',
        'Ask them if they believe in Bigfoot!',
        'Ask them about the worst haircut they\'ve ever had!',
        'Ask them what their favourite B movie is!',
        'Ask them if they know any lit af slang!',
        'Ask them if they recycle!',
        'Ask them what their favourite kind of cheese is!',
        'Ask them if they have a fidget spinner!'
    ], 3)
