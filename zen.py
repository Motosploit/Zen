#python 2.7
#import modules
#regex module
import re
#json module
import json
#argument module
import argparse
#requests http library module
from requests import get
#set parser variable, this block will define the arguments and what they do for the program
parser = argparse.ArgumentParser()
#add target, -o, --org arguments to parser
parser.add_argument('target', help='target')
parser.add_argument('-o', help='output file', dest='output')
parser.add_argument('--org', help='organization', dest='org', action='store_true')
#set args variable
args = parser.parse_args()
#set inp variable to the value in the target arg
inp = args.target
#set output variable to the value of output argument
output = args.output
#set the organization variable to the value of the org argument
organization = args.org

#set color variables for end, green, bad and info
end = '\033[1;m'
green = '\033[1;32m'
bad = '\033[1;31m[-]\033[1;m'
info = '\033[1;33m[!]\033[1;m'

#print welcome banner
print ('''%s
	Z E N v1.0
%s''' % (green, end))

#if inp variable ends with / then inp equals the last value in the inp list
if inp.endswith('/'):
	inp = inp[:-1]

#targetOrganization variable equals targetRepo which equals targetUser all equal False
targetOrganization = targetRepo = targetUser = False

#if inp variable count of / is less then for
if inp.count('/') < 4:
	#if / in inp
	if '/' in inp:
		#username equals the last value in the inp list split at / 
		username = inp.split('/')[-1]
	else:
		#username equals inp
		username = inp
	#if organization is True
	if organization:
		#target organization equals True
		targetOrganization = True
	else:
		#else targetUser is True
		targetUser = True
	#else if inp has 4 / in lisy
elif inp.count('/') == 4:
	#targetRepo equals the value of inp split at /
	targetRepo = inp.split('/')
	#username equals the value of the second to last value in targetRepo list
	username = targetRepo[-2]
	#repo equals the last value in targetRepo list
	repo = targetRepo[-1]
	#targetRepo equals True
	targetRepo = True
else:
	#print invalid input colored in the bad variable value
	print ('%s Invalid input' % bad)
	quit()

#define findContributorsFromReport function with the username and repo variables
def findContributorsFromRepo(username, repo):
	#response equals the get request to the url with the values passed into username and repo.
	#And use .text to pull the text from the response
	response = get('https://api.github.com/repos/%s/%s/contributors?per_page=100' % (username, repo)).text
	#contributors equals the returned data from searching response variable
	#with the regular expression of r'https://github\.com/(.*?)"'
	contributors = re.findall(r'https://github\.com/(.*?)"', response)
	#return contributors variable
	return contributors

#define findReposFromUsername function with the username variables
def findReposFromUsername(username):
	#response equals the get request to the url with the values passed into username.
	#And use .text to pull the text from the response
	response = get('https://api.github.com/users/%s/repos?per_page=100&sort=pushed' % username).text
	#repos equals the returned data from searching response variable
	#%s equals username variable
	#with the regular expression of r'"full_name":"%s/(.*?)",.*?"fork":(.*?),'
	repos = re.findall(r'"full_name":"%s/(.*?)",.*?"fork":(.*?),' % username, response)
	#initialize nonForkedRepos list
	nonForkedRepos = []
	#loop through repos list
	for repo in repos:
		#if nothing in position 1 of repo  lisy
		if repo[1] == 'false':
			#append the value at position 0 of repo list to nonForkedRepos
			nonForkedRepos.append(repo[0])
	#return nonForkedRepos variable
	return nonForkedRepos
#define findEmailFromContributor function with the username, repo and contributor variables
def findEmailFromContributor(username, repo, contributor):
	#response equals the get request to the url with the values passed into username, repo and contributor.
	#And use .text to pull the text from the response
	response = get('https://github.com/%s/%s/commits?author=%s' % (username, repo, contributor)).text
	#latestCommit equals the returned data from searching response variable
	#%s equals username and repo variable
	#with the regular expression of r'href="/%s/%s/commit/(.*?)"'
	#the returned data will be of the first paranthesized subgroup that was matched (.group(1) does this)
	latestCommit = re.search(r'href="/%s/%s/commit/(.*?)"' % (username, repo), response).group(1)
	#commitDetails equals the get request to the url with the values passed into username, repo and lastestCommit.
	#And use .text to pull the text from the response
	commitDetails = get('https://github.com/%s/%s/commit/%s.patch' % (username, repo, latestCommit)).text
	#email equals the returned data from searching commitDetails variable
	#with the regular expression of r'<(.*)>'
	#the returned data will be of the first paranthesized subgroup that was matched (.group(1) does this)
	email = re.search(r'<(.*)>', commitDetails).group(1)
	#return email variable
	return email

#define findEmailFromUsername function with username variable
def findEmailFromUsername(username):
	#repos equals the values returned from running the findReposFromUsername function 
	#with the username variable passed to it
	repos = findReposFromUsername(username)
	#for loop through repos list
	for repo in repos:
		#email equals values of findEmailFromContributor 
		#with the username, repo and username variables passed to it
		email = findEmailFromContributor(username, repo, username)
		#if data in email then print out username and email variables
		if email:
			print (username + ' : ' + email)
			break
#define findEmailsFromRepo function with username and repo variable
def findEmailsFromRepo(username, repo):
	#contibutors equals values from findContributorsFromRepo running with username and repo variables
	contributors = findContributorsFromRepo(username, repo)
	#initialize jsonOutput dictionary
	jsonOutput = {}
	#print values of length of contributors
	print ('%s Total contributors: %s%i%s' % (info, green, len(contributors), end))
	#loop through contributors list
	for contributor in contributors:
		#email equals values returned from findEmailFromContributor function
		email = (findEmailFromContributor(username, repo, contributor))
		#print contributor and email values
		print (contributor + ' : ' + email)
		#jsonOuput dictionary contributor key to contain values of email variable
		jsonOutput[contributor] = email
	#if output is true
	if output:
		#jsonOutput key data from dictionary is formatted to json and set to json_string variable
		json_string = json.dumps(jsonOutput, indent=4)
		#savefile equals the output file opened in write mode
		savefile = open(output, 'w+')
		#write to savefile the json_string
		savefile.write(json_string)
		#close the savefile
		savefile.close()
#define the findUsersFromOrganization function
def findUsersFromOrganization(username):
	#response equals the get request to the url with the values passed into username.
	#And use .text to pull the text from the response
	response = get('https://api.github.com/orgs/%s/members?per_page=100' % username).text
	#members equals the returned data from searching response variable
	#with the regular expression of r'"login":"(.*?)"'
	members = re.findall(r'"login":"(.*?)"', response)
	#return members variable
	return members

#if targetOrganization equals true
if targetOrganization:
	#set usernames to output of findUsersFromOrganization(username) function
	usernames = findUsersFromOrganization(username)
	#loop through usernames data
	for username in usernames:
		#run each value through the findEmailFromUsername(username) function
		findEmailFromUsername(username)
#elif targetUser equals true
elif targetUser:
	#run findEmailFromUsername function
	findEmailFromUsername(username)
#eliftargetRepo is true
elif targetRepo:
	#run findEmailsFromRepo function
	findEmailsFromRepo(username, repo)
