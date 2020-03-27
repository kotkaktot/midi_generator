from midiutil import MIDIFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from settings import token
from gtts import gTTS
import os
import time

updater = Updater(token, use_context=True)


def corona_notes_list(octave):
    # reading input file with corona_virus DNA
    dna_str = ''
    for i in open('corona_dna').readlines():
        dna_str += ''.join(i.split(' ')[1:])
    dna_str = dna_str.replace('\n', '')
    # print(dna_str)

    # result replacing with note's codes
    octave = int(octave)
    dna_str = dna_str.replace('a', '{},'.format(33 + 12 * (octave-1)))
    dna_str = dna_str.replace('c', '{},'.format(24 + 12 * (octave-1)))
    dna_str = dna_str.replace('g', '{},'.format(31 + 12 * (octave-1)))
    dna_str = dna_str.replace('t', '{},'.format(29 + 12 * (octave-1)))
    # print(dna_str)

    midi = []
    for note in dna_str[:-1].split(','):
        midi.append(int(note))

    return midi


def midi_generate(midi, tempo, octave, name='corona'):
    degrees = midi  # MIDI note number
    track = 0
    channel = 0
    time = 0    # In beats
    duration = 1    # In beats
    volume = 100  # 0-127, as per the MIDI standard
    tempo = int(tempo)

    MyMIDI = MIDIFile(2)  # One track, defaults to format 1 (tempo track is created automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    # print("corona_{}_{}.mid".format(tempo, octave))

    with open("{}_{}_{}.mid".format(name, tempo, octave), "wb") as output_file:
        MyMIDI.writeFile(output_file)


def corona_midi(update, context):
    msg_list = update.message.text.split(' ')
    tempo = msg_list[1]
    octave = msg_list[2]
    # print(tempo, octave)
    midi_generate(corona_notes_list(octave), tempo, octave)
    os.system('timidity corona_{}_{}.mid -Ow -o - |'
              ' ffmpeg -i - -acodec libmp3lame -ab 64k corona_{}_{}.mp3'.format(tempo, octave, tempo, octave))

    context.bot.send_audio(chat_id=update.effective_chat.id,
                           audio=open('corona_{}_{}.mp3'.format(tempo, octave), 'rb'))


def text_to_midi(update, context):
    msg = update.message.text.split('*')
    tempo = msg[0].split(' ')[1]
    text = msg[1]
    midi_list = []
    for symb in text:
        if ord(symb) > 1000:
            midi_list.append(ord(symb)-1000)
        else:
            midi_list.append(ord(symb))

    # print(midi_list)
    midi_generate(midi_list, tempo, 'x', name='text')

    file_name = 'text_{}_x.mp3'.format(tempo, tempo)

    if os.path.isfile(file_name):
        os.remove(file_name)
    os.system('timidity {}.mid -Ow -o - |'
              ' ffmpeg -i - -acodec libmp3lame -ab 64k {}'.format(file_name.split('.')[0], file_name))

    context.bot.send_audio(chat_id=update.effective_chat.id,
                           audio=open(file_name, 'rb'))


def aphorismes(update, context):
    from bs4 import BeautifulSoup
    import requests

    aph_file = 'aphorisme_tts.mp3'

    url = 'http://www.aphorisme.ru/random/?q=2329'
    html = requests.get(url)

    soup = BeautifulSoup(html.content, features="html.parser")

    aph_text = soup.find('div', attrs={'class': 'rendom_aph'}).text

    # print(aph_text)

    generate_mp3_from_text(aph_text, aph_file)

    context.bot.send_audio(chat_id=update.effective_chat.id,
                           audio=open(aph_file, 'rb'))


def generate_mp3_from_text(text, filename):
    tts = gTTS(text,
               lang='ru')

    tts.save(filename)


def brat_mp3(update, context):
    import random
    with open('brat.txt') as f:
        phrases = f.read().splitlines()
    ind = random.randrange(0, len(phrases)-1)

    generate_mp3_from_text(phrases[ind], 'brat_wisdom.mp3')

    context.bot.send_audio(chat_id=update.effective_chat.id,
                           audio=open('brat_wisdom.mp3', 'rb'))


updater.dispatcher.add_handler(CommandHandler('brat', brat_mp3))
updater.dispatcher.add_handler(CommandHandler('wisdom', aphorismes))
updater.dispatcher.add_handler(CommandHandler('text', text_to_midi))
updater.dispatcher.add_handler(CommandHandler('corona', corona_midi))
updater.start_polling()
updater.idle()
