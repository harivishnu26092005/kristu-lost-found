import database
def test_create_and_update_report(tmp_path,monkeypatch):
 monkeypatch.setattr(database,'DB_PATH',tmp_path/'test.db'); database.init_db()
 i=database.create_report(title='Test notebook',category='Books & Notes',item_type='Lost',block='Humanities Block',sublocation='Classroom',item_date='2026-10-26',description='Blue notebook',contact_method='Campus help desk')
 assert database.get_report(i)['title']=='Test notebook'; database.update_status(i,'Returned'); assert database.get_report(i)['status']=='Returned'
