#!/usr/bin/env python3

import requests
import pickle
import sys

def requestRange(url, token):
    """
        Iterate over the stuff of the given URL.
    """
    repoRequest=requests.get(url, params={'access_token':token})
    if repoRequest.status_code == 401:
        sys.exit('API request failed. Bad token?')
    if repoRequest.status_code != 200:
        return
    yield repoRequest.json()
    while 'next' in repoRequest.links:
        repoRequest = requests.get(repoRequest.links['next']['url'], params={'access_token':token})
        yield repoRequest.json()

def repoRange(url, token):
    """
        Iterate over the repositories of the given URL.
    """
    totalRepo = 0
    for pppRepos in requestRange(url, token):
        totalRepo += len(pppRepos)
        for repo in pppRepos:
            print(repo['name'])
            yield repo
    print("\n%d repositories found." % totalRepo)

def printScore(scoresMap):
    """
        Print the scores of the given map.
    """
    totalEvent = 0
    for nbEvent in scoresMap.values():
        totalEvent += nbEvent
    scores = sorted(scoresMap.items(), key = lambda x: -x[1])
    print("\nTotal: %d." % totalEvent)
    for (author, nbEvent) in scores:
        print("{0}: {1} ({2:.1f}%)".format(author.ljust(40), str(nbEvent).ljust(5), nbEvent/totalEvent*100))

def underline(string):
    return("\n%s\n%s" % (string, "-"*len(string)))

def printCommitStats(token):
    """
        Print stats about commits of the ProjetPP.
        Exclude “merge” and “bump” commits.
    """
    commitCount = {}
    for repo in repoRange('https://api.github.com/orgs/ProjetPP/repos', token):
        for repoCommits in requestRange(repo['commits_url'].split('{')[0], token):
            for commit in repoCommits:
                if 'bump' not in commit['commit']['message'].lower() and 'merge' not in commit['commit']['message'].lower():
                    try:
                        login = commit['author']['login']
                    except (KeyError, TypeError):
                        continue
                    try:
                        commitCount[login] += 1
                    except KeyError:
                        commitCount[login] = 1
    printScore(commitCount)

def printEventStats(token):
    """
        Print stats about events of the ProjetPP.
        Exclude “PushEvent” events.
    """
    eventCount = {}
    eventTypeCount = {}
    for repo in repoRange('https://api.github.com/orgs/ProjetPP/repos', token):
        for repoEvents in requestRange(repo['events_url'], token):
            for event in repoEvents:
                try:
                    typeName = event['type']
                except (KeyError, TypeError):
                    continue
                if typeName == 'PushEvent':
                    continue
                try:
                    eventTypeCount[typeName] += 1
                except:
                    eventTypeCount[typeName] = 1
                try:
                    login = event['actor']['login']
                except (KeyError, TypeError):
                    continue
                try:
                    eventCount[login] += 1
                except:
                    eventCount[login] = 1
    printScore(eventTypeCount)
    printScore(eventCount)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Syntax: %s <token file (pickle format)>' % sys.argv[0])
    try:
        tokenFile = open(sys.argv[1],'rb')
        token = pickle.load(tokenFile)
        tokenFile.close()
    except FileNotFoundError:
        sys.exit('The file %s does not exist.' % sys.argv[1])
    except pickle.UnpicklingError:
        sys.exit('The token was not saved with pickle.')
    if not isinstance(token, str):
        sys.exit('The token is not a string.')
    try:
        print(underline('Commits'))
        printCommitStats(token)
        print('')
        print(underline('Events'))
        printEventStats(token)
        print('')
    except requests.ConnectionError:
        sys.exit('API request failed. No internet connection?')
