from matching import score_match, suggest_matches
def test_match_scores_category_and_location():
 a={'id':1,'title':'Blue bottle','category':'Bottle / Lunch Box','block':'Main Block','sublocation':'Library','description':'blue metal bottle'}
 b={'id':2,'title':'Blue metal bottle','category':'Bottle / Lunch Box','block':'Main Block','sublocation':'Library','description':'blue bottle found'}
 score,reasons=score_match(a,b); assert score>=60; assert 'same category' in reasons
def test_same_record_is_not_suggested():
 a={'id':1,'title':'Keys','category':'Keys','block':'PG Block','sublocation':'Corridor','description':'two keys'}
 assert suggest_matches(a,[a])==[]
