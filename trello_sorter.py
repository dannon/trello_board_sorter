"""
Galaxy Trello Issue Sorter
Work in progress.  Or not, works well enough as it is.
"""

import os
import requests
import time
#from requests_oauthlib import OAuth1Session  # This should really be used at some point.

#g2roboto super secret!
key = os.env.get('TRELLO_AUTH_KEY')
secret = os.environ.get('TRELLO_AUTH_SECRET')
token = os.environ.get('TRELLO_OAUTH_TOKEN')

#Trello id of the boards to sort.
BOARDS = ['75c1kASa',  # galaxy dev
          'csTK4j3B',  # cloudman dev
          'm1HRlOCO',  # galaxy dev internal
          'v2fx42Ms',  # galaxy infrastructure
          'vHqpKpZF',  # galaxy toolshed
          ]


def set_position(card_id, position='top'):
    """Sets the position of a particular card.  Default top."""
    payload = {'pos': position,
               'key': key,
               'token': secret}
    requests.put("https://api.trello.com/1/cards/%s" % card_id, payload)


def card_is_low_priority(card):
    """returns true if a card is low priority"""
    for item in card['labels']:
        if item['color'] == 'red':
            return True
    return False


def sort_list(list_id):
    """Sorts all the cards in a list.  This is really stupid and just sorts in
    python and reassigns numbers.  Meaning, if there's a shift downward,
    everything gets bumped down a slot.  We could get away with fewer requests
    by actually using numbers between existing positions move individual
    cards."""
    cards = requests.get("https://api.trello.com/1/lists/%s/cards" % list_id).json()
    if cards:
        sorted_cards = sorted(cards, key=lambda c: (card_is_low_priority(c), len(c['idMembersVoted']), c['badges']['comments'], c['idShort']))
        used_positions = [c['pos'] for c in cards]
        for i, card in enumerate(sorted_cards[::-1]):
            if card['pos'] != i + 1:
                print "WAS %s, now %s: %s %s\t%s" % (card['pos'], i + 1, card_is_low_priority(card), len(card['idMembersVoted']), card['name'])
                #Make sure there isn't already a card at that position, or trello does things we don't want.
                if i + 1 in used_positions:
                    cards_to_move = [c for c in cards if c['pos'] == i + 1]
                    for c in cards_to_move:
                        print "\tCLEARING %s:%s\t%s" % (c['pos'], i + 1, c['name'])
                        set_position(c, 9000)  # just throw it way at the end, hopefully we never have this many cards.
                        used_positions.remove(i + 1)
                        time.sleep(1)
                set_position(card['id'], i + 1)
                used_positions.remove(card['pos'])
                used_positions.append(i + 1)
                time.sleep(1)
            else:
                print "SKIP %s: %s %s\t%s" % (i + 1, card_is_low_priority(card), len(card['idMembersVoted']), card['name'])


def sort_board(board_id):
    """Sorts all the cards in a board."""
    print "https://api.trello.com/1/boards/%s/lists?key=%s&token=%s" % (board_id, key, token)
    lists = requests.get("https://api.trello.com/1/boards/%s/lists?key=%s&token=%s" % (board_id, key, token)).json()
    for l in lists:
        sort_list(l['id'])

if __name__ == "__main__":
    for board in BOARDS:
        print "----------------------------------------------------------------\nBOARD:\t%s" % board
        try:
            sort_board(board)
        except Exception, ex:
            print ex
