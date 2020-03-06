from midiutil import MIDIFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from settings import token

updater = Updater(token, use_context=True)


def corona_notes_list():
    # reading input file with corona_virus DNA
    dna_str = ''
    for i in open('corona_dna').readlines():
        dna_str += ''.join(i.split(' ')[1:])
    dna_str = dna_str.replace('\n', '')
    print(dna_str)

    # result replacing with note's codes
    octave = 4
    dna_str = dna_str.replace('a', '{},'.format(33 + 12 * (octave-1)))
    dna_str = dna_str.replace('c', '{},'.format(24 + 12 * (octave-1)))
    dna_str = dna_str.replace('g', '{},'.format(31 + 12 * (octave-1)))
    dna_str = dna_str.replace('t', '{},'.format(29 + 12 * (octave-1)))
    print(dna_str)

    midi = []
    for note in dna_str[:-1].split(','):
        midi.append(int(note))

    return midi


def midi_generate(midi):
    degrees = midi  # MIDI note number
    track = 0
    channel = 0
    time = 0    # In beats
    duration = 1    # In beats
    tempo = 300   # In BPM
    volume = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    with open("play.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)


def commands(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='/add_good слово\n'
                                  '/add_bad слово\n'
                                  '/del_good слово\n'
                                  '/del_bad слово\n'
                                  '/good_list слово\n'
                                  '/bad_list слово\n'
                                  '/who_add слово\n'
                                  '/leaders\n'
                                  '/attack\n'
                                  '/commands\n')

updater.dispatcher.add_handler(CommandHandler('commands', commands))
updater.start_polling()
updater.idle()
