import os
import re
import sys
import json

from flask import Flask, make_response, request
from mpyq import mpyq
import protocol29406

api = Flask(__name__)


@api.route('/<filename>', methods=['GET'])
def parse_replay(filename):
    archive = mpyq.MPQArchive('/tmp/%s' % filename)
    resp = {}

    # Read the protocol header, this can be read with any protocol
    contents = archive.header['user_data_header']['content']
    header = protocol29406.decode_replay_header(contents)
    if request.args.has_key('header'):
        resp['header'] = header

    # The header's baseBuild determines which protocol to use
    baseBuild = header['m_version']['m_baseBuild']
    try:
        protocol = __import__('protocol%s' % (baseBuild,))
    except:
        files = [int(re.search(r'^protocol([0-9]+)\.py$', f).group(1)) for f in os.listdir('.') if re.match(r'^protocol[0-9]+\.py$', f)]
        files.sort(reverse=True)
        protocol = __import__('protocol%s' % files[0])

    # Print protocol details
    if request.args.has_key('details'):
        contents = archive.read_file('replay.details')
        resp['details'] = protocol.decode_replay_details(contents)

    # Print protocol init data
    if request.args.has_key('initdata'):
        contents = archive.read_file('replay.initData')
        resp['initdata'] = protocol.decode_replay_initdata(contents)

    # Print game events and/or game events stats
    if request.args.has_key('gameevents'):
        contents = archive.read_file('replay.game.events')
        resp['gameevents'] = protocol.decode_replay_game_events(contents)

    # Print message events
    if request.args.has_key('messageevents'):
        contents = archive.read_file('replay.message.events')
        resp['messageevents'] = protocol.decode_replay_message_events(contents)

    # Print tracker events
    if request.args.has_key('trackerevents') and hasattr(protocol, 'decode_replay_tracker_events'):
        contents = archive.read_file('replay.tracker.events')
        resp['trackerevents'] = protocol.decode_replay_tracker_events(contents)

    # Print attributes events
    if request.args.has_key('attributeevents'):
        contents = archive.read_file('replay.attributes.events')
        resp['attributeevents'] = protocol.decode_replay_attributes_events(contents)

    print >> sys.stdout, resp
    headers = {'Content-Type': 'application/json'}
    return make_response(json.dumps(resp, encoding='ISO-8859-1'), 200, headers)


if __name__ == '__main__':
    api.run()
