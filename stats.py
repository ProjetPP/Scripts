#!/usr/bin/env python3

import requests
import pickle
import sys

def printStats(token):
    repoRequest=requests.get('https://api.github.com/orgs/ProjetPP/repos',params={'access_token':token})
    if repoRequest.status_code != 200:
        sys.exit('API request failed. Bad token?')
    commitCounts = {}
    totalCommit = 0
    totalRepo = 0
    while True: # I have a dream that one day "do ... while" statement will exist in python
        pppRepos = repoRequest.json()
        totalRepo += len(pppRepos)
        for repo in pppRepos:
            print(repo['name'])
            repoCommits = requests.get(repo['commits_url'].split('{')[0],params={'access_token':token})
            while(repoCommits.ok):
                for commit in repoCommits.json():
                    if 'bump' not in commit['commit']['message'].lower() and 'merge' not in commit['commit']['message'].lower():
                        totalCommit+=1
                        try:
                            login = commit['author']['login']
                        except KeyError:
                            continue
                        except TypeError:
                            continue
                        try:
                            commitCounts[login] += 1
                        except KeyError:
                            commitCounts[login] = 1
                try:
                    repoCommits = requests.get(repoCommits.links['next']['url'],params={'access_token':token})
                except KeyError:
                    break
        try:
            repoRequest = requests.get(repoRequest.links['next']['url'], params={'access_token':token})
        except KeyError:
            break
    print('')
    print("%d repositories found." % totalRepo)
    print("%d commits found." % totalCommit)
    scores = sorted(commitCounts.items(),key = lambda x: -x[1])
    for (author,nbCommits) in scores:
        print("{0}: {1} ({2:.1f}%)".format(author.ljust(20),str(nbCommits).ljust(5),nbCommits/totalCommit*100))

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
    if not isinstance(token,str):
        sys.exit('The token is not a string.')
    try:
        printStats(token)
    except requests.ConnectionError:
        sys.exit('API request failed. No internet connection?')
