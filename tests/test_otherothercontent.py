'''	TESTS: for now run from package home with `PYTHONPATH=`pwd` py.test tests/test_otherothercontent.py`'''	


from otherothercontent import otherothercontent

GUIDE = './targets/pilot_sites.csv'

def test_getArticles():
	data = otherothercontent.fetchSiteGuide(GUIDE)
	for i in data:
		result = otherothercontent.getArticles(i)
		assert result.values()[0] is not []