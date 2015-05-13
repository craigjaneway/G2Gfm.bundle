#     Edited: for site name change by me (Craig Janeway).
######################################################################################

TITLE = "4do.se"
PREFIX = "/video/4do"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://4do.se"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_COVER)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_COVER)
	VideoClipObject.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
	HTTP.Headers['Referer'] = 'http://4do.se/'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Movies", category = "/movies", page_count = 1), title = "Movies", thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="TV Series", category = "/tvseries", page_count = 1), title = "TV Series", thumb = R(ICON_SERIES)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Latest Episodes", category = "/episodes", page_count = 1), title = "Latest Episodes", thumb = R(ICON_SERIES)))
	oc.add(DirectoryObject(key = Callback(GenreMenu, title="Genres"), title = "Genres", thumb = R(ICON_LIST)))
	
	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(BASE_URL + category + "/index.php?&page=" + str(page_count))

	for each in page_data.xpath("//td[@class='topic_content']"):
		url = BASE_URL + category + "/" + each.xpath("./div/a/@href")[0]
		title = each.xpath("./div/a/img/@alt")[0]
		thumb = each.xpath("./div/a/img/@src")[0]
		
		if category == "/movies" or category == "/episodes":
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)

		if category == "/tvseries":
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)
	
	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = title, category = category, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
# Checks whether page is episode page or not. If not, display episode list

@route(PREFIX + "/pageepisodes")
def PageEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)
	eps_list = page_data.xpath("//div[@class='inner']/h3/a")
	season_list = page_data.xpath("//div[@class='titleline']/h2/a")
	if len(season_list) >= 1:
		for each in season_list:
			season_url = BASE_URL + "/forum/" + each.xpath("./@href")[0]
			season_title = title + " " + each.xpath("./text()")[0]

			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, title = season_title, url = season_url),
				title = season_title,
				thumb = R(ICON_SERIES)
				)
			)

	for each in eps_list:
		ep_url = BASE_URL + "/forum/" + each.xpath("./@href")[0]
		ep_title = each.xpath("./text()")[0]
	
		if ep_title.find("Season Download") < 1:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0], url = ep_url),
				title = ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0],
				thumb = R(ICON_LIST)
				)
			)

	return oc
	
######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)
	title = page_data.xpath("//title/text()")[0].rsplit(" Streaming",1)[0].rsplit(" Download",1)[0]
	thumb = page_data.xpath("//blockquote[@class='postcontent restore']//div/img/@src")[0]

	#load recursive iframes to find google docs url
	try:
		first_frame_url = page_data.xpath("//blockquote/div/iframe/@src")[1]
	except:
		first_frame_url = page_data.xpath("//blockquote/div/iframe/@src")[0]
	first_frame_data = HTML.ElementFromString(HTTP.Request(first_frame_url, headers={'referer':url}))
	second_frame_url = first_frame_data.xpath("//iframe/@src")[0]
	second_frame_data = HTML.ElementFromString(HTTP.Request(second_frame_url, headers={'referer':first_frame_url}))
	final_frame_url = second_frame_data.xpath("//iframe/@src")[0]
	
	oc.add(VideoClipObject(
		url = final_frame_url,
		thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
		title = title
		)
	)
	try:
		second_frame_url_part2 = second_frame_url.split(".php")[0]+"2.php"
		second_frame_data_part2 = HTML.ElementFromString(HTTP.Request(second_frame_url_part2, headers={'referer':first_frame_url}))
		final_frame_url_part2 = second_frame_data_part2.xpath("//iframe/@src")[0]
		Log ("Part2:"+final_frame_url_part2)
		oc.add(VideoClipObject(
			url = final_frame_url_part2,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
			title = "2-"+title
			)
		)
	except:
		Log ("Part2 Exception")

	try:
		second_frame_url_part3 = second_frame_url.split(".php")[0]+"3.php"
		second_frame_data_part3 = HTML.ElementFromString(HTTP.Request(second_frame_url_part3, headers={'referer':first_frame_url}))
		final_frame_url_part3 = second_frame_data_part3.xpath("//iframe/@src")[0]
		Log ("Part3:"+final_frame_url_part3)
		oc.add(VideoClipObject(
			url = final_frame_url_part3,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
			title = "3-"+title
			)
		)
	except:
		Log ("Part3 Exception")
		
	if len(page_data.xpath("//iframe[@class='restrain']/@src")) > 0:	
		trailer_url = page_data.xpath("//iframe[@class='restrain']/@src")[0].split("?",1)[0].replace("//www.youtube.com/embed/", "http://www.youtube.com/watch?v=")
		oc.add(VideoClipObject(
			url = trailer_url,
			thumb = R(ICON_SERIES),
			title = "Watch Trailer"
			)
		)	
	
	return oc

######################################################################################
# Displays movie genre categories
	
@route(PREFIX + "/genremenu")
def GenreMenu(title):

	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL("http://4do.se/movies/genre.php?showC=27")

	for each in page_data.xpath("//td[@class='topic_content']"):
		url = BASE_URL + "/movies/" + "/" + each.xpath("./div/a/@href")[0]
		thumb = each.xpath("./div/a/img/@src")[0]
		title = thumb.rsplit("/",1)[1].rsplit("-",1)[0]
		
		oc.add(DirectoryObject(
			key = Callback(GenrePage, title = title, url = url, page_count = 1),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
			)
		)
		
	return oc

######################################################################################
# Performs the same role as ShowCategory, but with adjustments for genre menu quirks
	
@route(PREFIX + "/genrepage")
def GenrePage(title, url, page_count):
	
	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)

	for each in page_data.xpath("//td[@class='topic_content']"):
		url = BASE_URL + "/movies/" + each.xpath("./div/a/@href")[0]
		title = each.xpath("./div/a/img/@alt")[0]
		thumb = each.xpath("./div/a/img/@src")[0]
		
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
			)
		)
		
	try:
		next_page = BASE_URL + page_data.xpath("//div[@class = 'mainpagination']//a/@href")[0].rsplit("=",1)[0] + "=" + str(int(page_count) + 1)
	except:
		next_page = "null"
	
	if next_page != "null":
		oc.add(NextPageObject(
			key = Callback(GenrePage, title = title, url = next_page, page_count = int(page_count) + 1),
			title = "More...",
			thumb = R(ICON_NEXT)
				)
			)
	
	return oc
