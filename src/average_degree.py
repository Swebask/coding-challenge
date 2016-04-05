from __future__ import division
import json
import networkx as nx
import itertools
import time
from decimal import *

# function to write average degree into the file
def write_avg_degree(G,file_write):
    sum_degree = 0
    two_places = Decimal(10) ** -2
    getcontext().rounding = ROUND_DOWN
    for node in G.nodes():
        sum_degree += G.degree(node)
    avg_degree = Decimal(sum_degree/G.number_of_nodes()).quantize(two_places)
    file_write.write(str(avg_degree) + "\n")


if __name__ == '__main__':
    input_file_path = 'tweet_input/tweets.txt'
    output_file_path = 'tweet_output/output.txt'
    file_read = open(input_file_path, 'r')
    file_write = open(output_file_path, 'w')

    hashmap = {}
    G = nx.Graph()

    for line in file_read:
        hashtags = []
        tweet = json.loads(line)

        if 'created_at' not in tweet or len(tweet['entities']['hashtags'])<2:
            continue;
        created_at = time.mktime(time.strptime(tweet['created_at'],"%a %b %d %H:%M:%S +0000 %Y"))

        # checking for tweets outside 60 second window
        if hashmap != {} and max(hashmap.keys()) - created_at > 60:
            write_avg_degree(G,file_write)
            continue;

        # checking for older tweets that have now moved out of 60 second window
        for date in hashmap.keys():
            if created_at - date > 60:
                for pair in itertools.combinations(hashmap.get(date), 2):
                    if G[pair[0]][pair[1]]['weight'] > 1:
                        G[pair[0]][pair[1]]['weight'] -= 1
                    else:
                        G.remove_edge(*pair)
                for hashtag_remove in hashmap.get(date):
                    if G.degree(hashtag_remove) == 0:
                        G.remove_node(hashtag_remove)
                del hashmap[date]

        # adding created_at, hashtag pair to hashmap
        hashmap[created_at] = hashtags

        #adding node(s) to graph
        for hashtag_obj in tweet['entities']['hashtags']:
            hashtag = hashtag_obj['text']
            hashtags.append(hashtag)
            if not G.has_node(hashtag):
                G.add_node(hashtag)

        #adding edges(s) to graph
        for pair in itertools.combinations(hashtags, 2):
            if G.has_edge(*pair):
                G[pair[0]][pair[1]]['weight'] += 1
            else:
                G.add_edge(*pair,weight=1)

        write_avg_degree(G,file_write)

    file_read.close()
    file_write.close()
