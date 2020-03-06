from midiutil import MIDIFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from settings import token
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


def midi_generate(midi, tempo, octave):
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

    with open("corona_{}_{}.mid".format(tempo, octave), "wb") as output_file:
        MyMIDI.writeFile(output_file)


def corona_midi(update, context):
    msg_list = update.message.text.split(' ')
    tempo = msg_list[1]
    octave = msg_list[2]
    # print(tempo, octave)
    midi_generate(corona_notes_list(octave), tempo, octave)
    os.system('timidity corona_{}_{}.mid -Ow -o - |'
              ' ffmpeg -i - -acodec libmp3lame -ab 64k corona_{}_{}.mp3'.format(tempo, octave, tempo, octave))

    time.sleep(5)
    context.bot.send_audio(chat_id=update.effective_chat.id,
                           audio=open('corona_{}_{}.mp3'.format(tempo, octave), 'rb'))


updater.dispatcher.add_handler(CommandHandler('corona', corona_midi))
updater.start_polling()
updater.idle()
