#!/usr/bin/env python3

import requests
import pickle
import sys
import urllib.request
import os
import shutil
from subprocess import call
import argparse

from github_util import repoRange

archiveExtension = {
    'zipball' : 'zip',
    'tarball' : 'tgz'
}

def downloadEverything(mode, directory, token):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    os.chdir(directory)
    for repo in repoRange('https://api.github.com/orgs/ProjetPP/repos', token):
        if mode == 'git':
            call(['git', 'clone', repo['clone_url']])
        else :
            try:
                urllib.request.urlretrieve('https://api.github.com/repos/projetpp/%s/%s/master' % (repo['name'].lower(), mode),\
                    filename='%s.%s' % (repo['name'].lower(), archiveExtension[mode]))
            except urllib.error.HTTPError: # empty repository
                continue

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
            description='Download the PPP (either the git repositories or archives).')
    parser.add_argument('-o', '--output', type=str,
            default='everything', help='Directory in which the files will be downloaded.')
    parser.add_argument('-m', '--mode', type=str,
            default='git', help='Format of the download (git, tarball or zipball).')
    parser.add_argument('-t', '--token', type=str,
            default='', help='GitHub token (optionnal).')
    args = parser.parse_args()
    if args.token == '':
        token = None
    else:
        try:
            tokenFile = open(args.token,'rb')
            token = pickle.load(tokenFile)
            tokenFile.close()
        except FileNotFoundError:
            sys.exit('The file %s does not exist.' % args.token)
        except pickle.UnpicklingError:
            sys.exit('The token was not saved with pickle.')
        if not isinstance(token,str):
            sys.exit('The token is not a string.')
    if args.mode not in {'git', 'tarball', 'zipball'}:
        sys.exit('The mode must be git, tarball or zipball')
    try:
        downloadEverything(args.mode, args.output, token)
    except requests.ConnectionError:
        sys.exit('API request failed. No internet connection?')
