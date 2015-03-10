import requests

def requestRange(url, token=None):
    """
        Iterate over the stuff of the given URL.
    """
    if not token:
        p = None
    else:
        p = {'access_token':token}
    repoRequest=requests.get(url, params=p)
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
