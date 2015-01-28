import github
import requests
from requests_oauthlib import OAuth2
import pickle
import sys

def print_stats(token):
    ppp_repos=requests.get('https://api.github.com/orgs/ProjetPP/repos',params={'access_token':token}).json()
    commit_counts = {}
    total = 0
    print("%d repositories found." % len(ppp_repos))
    for repo in ppp_repos:
        print(repo['name'])
        repo_commits = requests.get(repo['commits_url'].split('{')[0],params={'access_token':token})
        while(repo_commits.ok):
            for commit in repo_commits.json():
                if 'bump' not in commit['commit']['message'].lower() and 'merge' not in commit['commit']['message'].lower():
                    total+=1
                    try:
                        login = commit['author']['login']
                    except KeyError:
                        continue
                    except TypeError:
                        continue
                    try:
                        commit_counts[login] += 1
                    except KeyError:
                        commit_counts[login] = 1
            try:
                repo_commits = requests.get(repo_commits.links['next']['url'],params={'access_token':token})
            except KeyError:
                break
    print('')
    print("Total: %d\n" % total)
    scores = sorted(commit_counts.items(),key = lambda x: -x[1])
    for (author,nbCommits) in scores:
        print("{0}: {1} ({2:.1f}%)".format(author.ljust(20),str(nbCommits).ljust(5),nbCommits/total*100))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Syntax: %s <token file (pickle format)>' % sys.argv[0])
    try:
        token_file = open(sys.argv[1],'rb')
        token = pickle.load(token_file)
        token_file.close()
    except FileNotFoundError:
        sys.exit('The file %s does not exist.' % sys.argv[1])
    except pickle.UnpicklingError:
        sys.exit('The token was not saved with pickle.')
    if not isinstance(token,str):
        sys.exit('The token is not a string.')
    print_stats(token)
