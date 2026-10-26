import sqlite3
from pathlib import Path
from datetime import date
DB_PATH = Path(__file__).parent / 'jayan_find.db'
CATEGORIES = ['ID Card','Books & Notes','Wallet / Purse','Keys','Electronics','Bottle / Lunch Box','Clothing / Accessories','Jewellery','Documents','Other']
BLOCKS = ['PG Block','Main Block','Admin Block','Humanities Block']
def connect():
    c=sqlite3.connect(DB_PATH, timeout=10); c.row_factory=sqlite3.Row; return c
def init_db():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,category TEXT NOT NULL,item_type TEXT NOT NULL,block TEXT NOT NULL,sublocation TEXT NOT NULL,item_date TEXT NOT NULL,description TEXT NOT NULL,contact_method TEXT NOT NULL,image_path TEXT,status TEXT NOT NULL DEFAULT 'Open',is_demo INTEGER NOT NULL DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS claims(id INTEGER PRIMARY KEY AUTOINCREMENT,item_id INTEGER NOT NULL,claimant TEXT NOT NULL,contact_method TEXT NOT NULL,proof_note TEXT NOT NULL,status TEXT DEFAULT 'Pending',created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(item_id) REFERENCES reports(id) ON DELETE CASCADE)''')
def list_reports(search=None,item_type=None,category=None,block=None,status=None,limit=200):
    q='SELECT * FROM reports WHERE 1=1'; p=[]
    if search:
        q+=' AND (title LIKE ? OR description LIKE ? OR category LIKE ? OR block LIKE ? OR sublocation LIKE ?)'; t='%'+search+'%'; p += [t]*5
    for col,val in [('item_type',item_type),('category',category),('block',block),('status',status)]:
        if val: q+=f' AND {col}=?'; p.append(val)
    q+=' ORDER BY id DESC LIMIT ?'; p.append(min(max(int(limit),1),5000))
    with connect() as c: return [dict(r) for r in c.execute(q,p).fetchall()]
def get_report(i):
    with connect() as c:
        r=c.execute('SELECT * FROM reports WHERE id=?',(int(i),)).fetchone(); return dict(r) if r else None
def create_report(**x):
    with connect() as c:
        cur=c.execute('INSERT INTO reports(title,category,item_type,block,sublocation,item_date,description,contact_method,image_path,status,is_demo) VALUES(?,?,?,?,?,?,?,?,?,\'Open\',0)',(x['title'],x['category'],x['item_type'],x['block'],x['sublocation'],x['item_date'],x['description'],x['contact_method'],x.get('image_path'))); return cur.lastrowid
def update_status(i,status):
    if status not in ['Open','Claim Pending','Returned','Closed']: raise ValueError('Invalid status')
    with connect() as c: c.execute('UPDATE reports SET status=? WHERE id=?',(status,int(i)))
def stats():
    with connect() as c:
        count=lambda sql: c.execute(sql).fetchone()[0]
        return {'total':count('SELECT COUNT(*) FROM reports'),'lost':count("SELECT COUNT(*) FROM reports WHERE item_type='Lost' AND status='Open'"),'found':count("SELECT COUNT(*) FROM reports WHERE item_type='Found' AND status='Open'"),'returned':count("SELECT COUNT(*) FROM reports WHERE status='Returned'"),'lost_all':count("SELECT COUNT(*) FROM reports WHERE item_type='Lost'"),'found_all':count("SELECT COUNT(*) FROM reports WHERE item_type='Found'")}
def seed_demo_data():
    with connect() as c:
        if c.execute('SELECT COUNT(*) FROM reports WHERE is_demo=1').fetchone()[0]: return
        d=date.today().isoformat(); rows=[('Blue metal water bottle','Bottle / Lunch Box','Found','Main Block','Library',d,'Blue bottle left near study tables. Fictional demo item.','Campus help desk (demo)'),('Black wallet','Wallet / Purse','Lost','Cafeteria','Cafeteria',d,'Small black wallet. Verify contents privately. Demo item.','Campus help desk (demo)'),('Data Science textbook','Books & Notes','Found','Main Block','Corridor',d,'Textbook found on a bench. Demo item.','Campus help desk (demo)'),('Student ID card','ID Card','Found','Admin Block','Reception',d,'ID card handed in; details intentionally hidden. Demo item.','Campus help desk (demo)'),('Silver keychain with two keys','Keys','Lost','PG Block','Sports Area',d,'Two keys on a silver keychain. Demo item.','Campus help desk (demo)'),('Wireless earbuds case','Electronics','Found','PG Block','Corridor',d,'White earbuds case. Demo item.','Campus help desk (demo)'),('Blue notebook','Books & Notes','Lost','Humanities Block','Classroom',d,'Blue notebook with class notes. Demo item.','Campus help desk (demo)'),('Black umbrella','Clothing / Accessories','Found','Humanities Block','Reception',d,'Foldable black umbrella. Demo item.','Campus help desk (demo)')]
        c.executemany("INSERT INTO reports(title,category,item_type,block,sublocation,item_date,description,contact_method,status,is_demo) VALUES(?,?,?,?,?,?,?,?, 'Open',1)",rows)
def add_claim(item_id,claimant,contact,proof):
    with connect() as c:
        cur=c.execute("INSERT INTO claims(item_id,claimant,contact_method,proof_note,status) VALUES(?,?,?,?,'Pending')",(item_id,claimant,contact,proof)); return cur.lastrowid
def list_claims():
    with connect() as c: return [dict(r) for r in c.execute('SELECT * FROM claims ORDER BY id DESC').fetchall()]
def update_claim_status(i,s):
    if s not in ['Pending','Approved','Rejected']: raise ValueError('Invalid claim status')
    with connect() as c: c.execute('UPDATE claims SET status=? WHERE id=?',(s,int(i)))
def delete_demo_data():
    with connect() as c:
        c.execute('DELETE FROM claims WHERE item_id IN (SELECT id FROM reports WHERE is_demo=1)'); c.execute('DELETE FROM reports WHERE is_demo=1')
