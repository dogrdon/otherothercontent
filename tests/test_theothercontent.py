'''	TESTS: for now run from package home with `PYTHONPATH=`pwd` py.test tests/test_theothercontent.py`'''	


from theothercontent import theothercontent

GUIDE = './targets/pilot_sites.csv'

def test_getArticles():
	data = theothercontent.fetchSiteGuide(GUIDE)
	for i in data:
		result = theothercontent.getArticles(i)
		assert result.values()[0] is not []