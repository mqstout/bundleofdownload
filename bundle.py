# Bundle of Holding bulk downloader
# Author: MqsTout
# Please, respect Bundle of Holding and download responsibly.
# See the FAQ, https://bundleofholding.com/index/faq
#
# Prerequisites: splinter, requests
#  [super user] pip install requests
#  [super user] pip install splinter#
# usage: bundle.py -h
# 

import sys, getopt, re, os
import requests
from splinter import Browser

version = 0.1

def download_all_warning():
	lines = []
	lines.append("Think hard before downloading all bundles.")
	lines.append("It could be a lot of bandwidth and disrespectful of the site.")
	lines.append("See: https://bundleofholding.com/index/faq")
	mx = 0
	for l in lines:
		mx = max(mx, len(l))
	lines[:] = ["! {0: <{sz}} !".format(l, sz=mx) for l in lines]
	cap = "!" * (mx+4)
	print(cap)
	for l in lines:
		print(l)
	print(cap)
	print()

def print_help():
	print("Bundle of Holding Wizard's Vault Downloader (Version {0})".format(version))
	print("Usage:")
	print("\tbundle.py -u <username> -p <password> -a -o -s")
	print("\t -u\tUser name (email address)")
	print("\t -p\tPassword")
	print("\t -a\tDownload all files for all bundles.")
	print("\t -o\tAutomatically overwrite existing files.")
	print("\t -s\tSkip existing files. (Precludes -o.)")
	print()
	download_all_warning()

def bundle(argv):
	username = ""
	password = ""
	all = False
	overwrite = False
	skip = False
	try:
		opts, args = getopt.getopt(argv, "hu:p:aso", ["username=", "password="] )
	except getopt.GetoptError:
		print_help()
		exit(2)
	for opt, arg in opts:
		if opt == "-h":
			print_help()
			exit()
		elif opt == "-a":
			download_all_warning()
			all = True
		elif opt == "-o":
			overwrite = True
		elif opt == "-s":
			skip = True
		elif opt in ("-u", "--username"):
			username = arg
		elif opt in ("-p", "--password"):
			password = arg
	del argv, args, opts
	
	if not username:
		username = input("Username (email): ")
		if not username:
			print("Empty, exiting.")
			exit(2)
	if not password:
		password = input("Password: ")
		if not password:
			print("Empty, exiting.")
			exit(2)
	
	browser = Browser()
	print("Logging in...")
	browser.visit('https://bundleofholding.com/user/login')
	browser.fill('users_email', username)
	browser.fill('password', password)
	browser.find_by_name('submit').click()

	if (len(browser.find_by_css("div.logged-in")) > 0):
	#if browser.is_text_present("Wizard's Cabinet"):
		print("Getting lists...")
		browser.visit('https://bundleofholding.com/download/list')
	else:
		print("Failed to log in.")
		if (input("Quit browser? */n ") != "n"):
			browser.quit()
		exit()

	bListBox = browser.find_by_id('overview')
	bListList = bListBox.find_by_tag('a')
	bundles = []
	for e in bListList:
		bundles.append( (e.value, e['href']) )

	del bListBox, bListList

	bundle_count = len(bundles)
	item = 0
	vault = {}
	for b in bundles:
		item += 1
		print("\tFile list {0} of {1}.".format(item, bundle_count))
		vault[b[0]] = []
		browser.visit(b[1])
		bLinks = browser.find_link_by_partial_href('file_id')
		# todo: get file list with file sizes if possible
		# problem: not all pages have "core-bundle" element; older ones are uglier
		# xpath span/a?
		for e in bLinks:
			vault[b[0]].append( (e.value, e['href']) )
			
	del item, bundle_count, bLinks

	print("\n\n")

# Chose to make command line parameter only to help reinforce FAQ.
#	if not all:
#		download_all_warning()
#		
#		totalfiles = 0
#		for bundle, files in vault.items():
#			totalfiles += len(files)
#
#		if (input("There are {0} bundles with a total of {1} files. Download all? y/* ".format(len(vault), totalfiles) ) == "y"):
#			all = True
#		del totalfiles
				
	rx = re.compile("[^\w _()'-]+")
	cookies = browser.cookies.all()
	for bundle, files in vault.items():
		print("{0} has {1} files.".format(bundle, len(files)) )
		if (all or input("\tDownload? y/* ") == "y"):
			print("\t...Downloading {0}".format(bundle))
			p = rx.sub("", bundle)
			os.makedirs(p, exist_ok=True)
			for f in files:
				#fn = rx.sub("", f[0]) # Or, assume remote's fine.
				print("\t\t{0}".format(f[0], end=""))
				fn = p + "/" + f[0]
				if (os.path.isfile(fn)):
					if (not skip and (overwrite or input("\tExists. Overwrite? y/* ") == "y")):
						print("Overwrite.")
						pass
					else:
						print("Skip.")
						continue
				r = requests.get(f[1], cookies = cookies, stream=True)
				#idiom taken from a stack overflow result
				with open(fn, 'wb') as fd:
					for chunk in r.iter_content(1000000):
						if chunk:
							fd.write(chunk)
							fd.flush()
							print(".", end="")
							sys.stdout.flush()
				print()
	del rx, cookies
	
	print("\n")
	browser.quit()
	exit()

if __name__ == "__main__":
	bundle(sys.argv[1:])
