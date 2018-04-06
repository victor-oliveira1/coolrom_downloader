#!/bin/python3
#Copyright © 2018 Victor Oliveira <victor.oliveira@gmx.com>
#This work is free. You can redistribute it and/or modify it under the
#terms of the Do What The Fuck You Want To Public License, Version 2,
#as published by Sam Hocevar. See the COPYING file for more details.

import urllib.request
import urllib.parse
from html.parser import HTMLParser
import os

buffer_size = 1024 * 8

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = list()
        self.attrib = list()
        self.starttag = list()

    def handle_starttag(self, tag, attrib):
        if tag:
            self.starttag.append(tag)
        if attrib:
            self.attrib.append(attrib)
    def handle_data(self, data):
        data = data.strip()
        if data:
            self.data.append(data)

def _getHtml(url):
    req = urllib.request.urlopen(url)
    html = req.read().decode()
    return html

def _getConsoles():
    url = 'http://coolrom.com/roms/'
    html_page = _getHtml(url)
    html_parser = MyHTMLParser()
    html_parser.feed(html_page)
    consoles = list()
    for line in html_parser.attrib:
        try:
            if 'roms' in line[0][1]:
                if len(line) == 1:
                    console_name = line[0][1].split('/')[2]
                    consoles.append(console_name)
        except IndexError:
            pass
    return consoles

def _getRomslist(console, letter):
    url = 'http://coolrom.com/roms/{}/{}/'.format(console, letter)
    html_page = _getHtml(url)
    html_parser = MyHTMLParser()
    html_parser.feed(html_page)
    roms = dict()
    for line in html_parser.attrib:
        try:
            if 'roms' in line[0][1]:
                if len(line) == 1:
                    if 'php' in line[0][1]:
                        rom = line[0][1]
                        rom_link = rom
                        rom_name = rom.split('/')[-1]
                        rom_name = rom_name.split('.php')[0]
                        rom_name = rom_name.replace('_', ' ')
                        roms.update({rom_name : rom_link})
        except IndexError:
            pass
    return roms
                        
def _downloadRom(rom_link):
    rom_id = rom_link.split('/')[3]
    rom_name = rom_link.split('/')[-1]
    rom_name = rom_name.split('.php')[0]
    rom_name = rom_name.replace('_', ' ')
    console_name = rom_link.split('/')[2]
    url = 'http://coolrom.com/dlpop.php?id={}'.format(rom_id)
    html_page = _getHtml(url)
    html_parser = MyHTMLParser()
    html_parser.feed(html_page)
    html_parser.feed(html_parser.data[1])
    for line in html_parser.attrib:
        try:
            if 'action' in line[1][0]:
                url_download = line[1][1]
                break
        except IndexError:
            pass
    req_header = {'Referer' : 'http://coolrom.com/{}'.format(rom_link)}
    req = urllib.request.Request(url_download, headers=req_header)
    req = urllib.request.urlopen(req)
    file_size = req.getheader('Content-Length')
    file_size = int(file_size)
    file_name = req.getheader('Content-Disposition')
    file_name = file_name.split('=')[-1]
    file_name = file_name.strip('"')
    file_name = urllib.parse.unquote(file_name)
    print('Console: {}'.format(console_name))
    print('Rom: {}'.format(rom_name))
    print('File: {}'.format(file_name))
    print('File Size: {:.2f}MB'.format(file_size / 1000 / 1000))
    with open(file_name, 'wb') as file:
        i = 0
        try:
            while True:
                buffer = req.read(buffer_size)
                if buffer:
                    file.write(buffer)
                    i += 1
                    print('{:.1f}%'.format((i * buffer_size / file_size) * 100), end='\r')
                else:
                    break
        except KeyboardInterrupt:
            os.remove(file_name)
            print('Download cancelled.\nLeftover file deleted.')

print('Coolrom Downloader\n')
print('== Select console ==')
consoles = _getConsoles()
for console in consoles:
    print(consoles.index(console), console)
console_selected = input('> ')
console_selected = int(console_selected)

print('== Input rom letter ==')
rom_letter = input('> ')
roms_list = _getRomslist(consoles[console_selected], rom_letter)
roms_names = list()
for rom_name in roms_list:
    roms_names.append(rom_name)

print('== Select rom ==')
for rom_name in roms_names:
    print(roms_names.index(rom_name), rom_name)
rom_selected = input('> ')
rom_selected = int(rom_selected)

print('== Downloading rom ==')
rom_selected_name = roms_names[rom_selected]
_downloadRom(roms_list[rom_selected_name])
