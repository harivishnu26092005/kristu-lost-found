from pathlib import Path
from datetime import date
import html
import pandas as pd
import streamlit as st
from database import init_db, seed_demo_data, list_reports, get_report, create_report, update_status, stats, CATEGORIES, BLOCKS, add_claim, list_claims, update_claim_status, delete_demo_data
from matching import suggest_matches

ROOT=Path(__file__).parent; UPLOADS=ROOT/'uploads'; UPLOADS.mkdir(exist_ok=True)
st.set_page_config(page_title='Jayan Find | Kristu Jayanti University',page_icon='🎒',layout='wide')
init_db(); seed_demo_data()
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp{background:linear-gradient(180deg,#fbfcff,#f4f6fb);font-family:'DM Sans',-apple-system,BlinkMacSystemFont,sans-serif;color:#172033}
[data-testid="stHeader"]{background:rgba(251,252,255,.85)}.block-container{max-width:1220px;padding-top:1.5rem;padding-bottom:3rem}
h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.035em;color:#17233d}
.hero{padding:clamp(1.5rem,4vw,3rem);border:1px solid #e4e9f3;border-radius:28px;background:radial-gradient(circle at 88% 10%,rgba(101,126,255,.13),transparent 28%),linear-gradient(130deg,#fff,#f1f4ff 62%,#eefaf7);box-shadow:0 14px 44px rgba(28,42,77,.055);margin-bottom:1.3rem}
.eyebrow{color:#5367d8;text-transform:uppercase;font-size:.75rem;font-weight:800;letter-spacing:.15em}.hero h1{font-size:clamp(2.5rem,6vw,4.6rem);line-height:1.02;margin:.6rem 0 .85rem}.hero p{font-size:1.08rem;max-width:690px;color:#5d6880;line-height:1.7}
.card,.blockcard{background:white;border:1px solid #e5eaf2;border-radius:19px;padding:1.1rem 1.2rem;box-shadow:0 8px 26px rgba(30,48,85,.045);margin-bottom:.75rem;transition:transform .18s ease,box-shadow .18s ease}.card:hover,.blockcard:hover{transform:translateY(-2px);box-shadow:0 14px 32px rgba(30,48,85,.08)}
.tag{display:inline-block;border:1px solid #e0e6f1;border-radius:999px;padding:.2rem .6rem;font-size:.75rem;color:#58647b;background:#f8faff;margin-right:.25rem}.muted{color:#7a8498;font-size:.87rem}div[data-testid="stMetric"]{background:white;border:1px solid #e7ebf3;padding:1rem;border-radius:17px;box-shadow:0 6px 20px rgba(30,48,85,.035)}
div.stButton>button,div.stFormSubmitButton>button{border-radius:12px;font-weight:650;transition:all .18s ease}div.stButton>button:hover{transform:translateY(-1px)}[data-testid="stSidebar"]{background:#f3f5fa;border-right:1px solid #e4e8f0}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
</style>''',unsafe_allow_html=True)
def esc(x): return html.escape(str(x or ''))
def logo():
 p=ROOT/'assets'/'college_logo.png'
 if p.exists(): st.image(str(p),width=85)
def header():
 a,b=st.columns([1,8],vertical_alignment='center')
 with a: logo()
 with b: st.markdown('### JAYAN FIND'); st.caption('Kristu Jayanti University · Campus Lost & Found')
def card(item,key):
 badge='🔴 LOST' if item['item_type']=='Lost' else '🟢 FOUND'
 if item['status']=='Returned': badge='✓ RETURNED'
 st.markdown(f"<div class='card'><span class='tag'>{badge}</span><span class='tag'>{esc(item['category'])}</span><h3 style='font-size:1.18rem;margin:.75rem 0 .3rem'>{esc(item['title'])}</h3><p style='color:#68748b;line-height:1.55'>{esc(item['description'])}</p><div class='muted'>⌖ {esc(item['block'])} · {esc(item['sublocation'])}</div><div class='muted'>Date: {esc(item['item_date'])} · Report #{item['id']}</div></div>",unsafe_allow_html=True)
 with st.expander('Details & recovery'):
  if item.get('image_path') and (ROOT/item['image_path']).exists(): st.image(str(ROOT/item['image_path']),width=260)
  st.write('**Status:**',item['status']); st.write('**Safe contact route:**',item['contact_method'])
  st.caption('Verify ownership before returning valuables. Never publish full ID numbers or sensitive details.')
  if item['status'] not in ['Returned','Closed']:
   if st.button('Request to claim',key=f'claim_{key}_{item["id"]}'):
    st.session_state.claim_for=item['id']; st.session_state.page='Claim an Item'; st.rerun()
   if st.button('Mark returned (demo)',key=f'return_{key}_{item["id"]}'):
    update_status(item['id'],'Returned'); st.success('Updated in demo.'); st.rerun()

with st.sidebar:
 logo(); st.markdown('## JAYAN FIND'); st.caption('Kristu Jayanti University')
 pages=['Home & Discover','Report an Item','Campus Blocks','Possible Matches','Campus Impact','Claim an Item','Admin Demo']
 if 'page' not in st.session_state: st.session_state.page=pages[0]
 st.session_state.page=st.radio('NAVIGATION',pages,index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
 st.divider(); st.caption('A campus-focused lost & found prototype.'); st.info('Privacy first: do not publish passwords, full ID numbers, or private claim answers.')
page=st.session_state.page
if page=='Home & Discover':
 header(); st.markdown('<section class="hero"><div class="eyebrow">Kristu Jayanti University · Campus community</div><h1>Lost something?<br>Let’s bring it home.</h1><p>A calmer, smarter way to report missing belongings, share found items, and help classmates reconnect with what matters — right here on campus.</p></section>',unsafe_allow_html=True)
 s=stats(); cols=st.columns(4)
 for col,label,value in zip(cols,['Open lost','Open found','Items returned','Total reports'],[s['lost'],s['found'],s['returned'],s['total']]): col.metric(label,value)
 a,b,c=st.columns(3)
 with a:
  if st.button('＋ Report lost item',type='primary',use_container_width=True): st.session_state.report_type='Lost'; st.session_state.page='Report an Item'; st.rerun()
 with b:
  if st.button('＋ Report found item',use_container_width=True): st.session_state.report_type='Found'; st.session_state.page='Report an Item'; st.rerun()
 with c:
  if st.button('⌕ Browse items',use_container_width=True): st.session_state.browse=True
 st.markdown('## Explore your campus')
 cols=st.columns(4)
 for col,block in zip(cols,BLOCKS):
  with col:
   n=len(list_reports(block=block,limit=1000)); st.markdown(f"<div class='blockcard'><div class='eyebrow'>CAMPUS BLOCK</div><h3 style='font-size:1rem'>{esc(block)}</h3><div class='muted'>{n} reports</div></div>",unsafe_allow_html=True)
   if st.button('Explore',key='explore_'+block,use_container_width=True): st.session_state.filter_block=block; st.session_state.page='Campus Blocks'; st.rerun()
 st.markdown('## Search the campus board')
 a,b,c=st.columns([2,1,1]); search=a.text_input('Search items',placeholder='wallet, ID card, library…'); kind=b.selectbox('Type',['All','Lost','Found','Returned']); cat=c.selectbox('Category',['All categories']+CATEGORIES); block=st.selectbox('Campus block',['All blocks']+BLOCKS)
 results=list_reports(search=search,item_type=kind if kind in ['Lost','Found'] else None,category=cat if cat!='All categories' else None,block=block if block!='All blocks' else None,status='Returned' if kind=='Returned' else None,limit=100)
 if results:
  cols=st.columns(2)
  for i,item in enumerate(results[:20]):
   with cols[i%2]: card(item,'home')
 else: st.info('No matching items. Try a different filter or submit a report.')
 st.caption('Sample entries are fictional demo records. Statistics update from the local database.')
elif page=='Report an Item':
 header(); st.markdown('<section class="hero"><div class="eyebrow">Help the campus community</div><h1>Make a report.</h1><p>Share enough detail to recognise the item while keeping private information private.</p></section>',unsafe_allow_html=True)
 default=st.session_state.pop('report_type','Lost')
 with st.form('report',clear_on_submit=True):
  typ=st.radio('What are you reporting?',['Lost','Found'],index=0 if default=='Lost' else 1,horizontal=True); title=st.text_input('Item name *',placeholder='e.g. Navy blue umbrella')
  a,b=st.columns(2)
  with a: cat=st.selectbox('Category',CATEGORIES); block=st.selectbox('Campus block',BLOCKS); sub=st.selectbox('Specific location',['Classroom','Corridor','Library','Cafeteria','Auditorium','Laboratory','Reception','Parking Area','Sports Area','Hostel','Bus / Transport Area','Other'])
  with b: day=st.date_input('Date lost/found',value=date.today(),max_value=date.today()); contact=st.text_input('Safe contact route *',placeholder='Campus help desk or college email'); uploaded=st.file_uploader('Optional photo (max 4 MB)',type=['png','jpg','jpeg','webp'])
  desc=st.text_area('Description *',placeholder='Colour, brand, case, or other non-sensitive identifying details…'); privacy=st.checkbox('I have not included passwords, full ID numbers, or sensitive personal information.'); submit=st.form_submit_button('Submit report',type='primary',use_container_width=True)
  if submit:
   if not title.strip() or not desc.strip() or not contact.strip(): st.error('Please fill item name, description and contact route.')
   elif not privacy: st.error('Please confirm the privacy check.')
   elif uploaded and uploaded.size>4*1024*1024: st.error('Choose an image smaller than 4 MB.')
   else:
    image_path=None
    if uploaded:
     suffix=Path(uploaded.name).suffix.lower(); safe=f'item_{abs(hash((title,uploaded.name,uploaded.size)))%10**10}{suffix}'; (UPLOADS/safe).write_bytes(uploaded.getvalue()); image_path=str(Path('uploads')/safe)
    rid=create_report(title=title.strip(),category=cat,item_type=typ,block=block,sublocation=sub,item_date=day.isoformat(),description=desc.strip(),contact_method=contact.strip(),image_path=image_path)
    st.success(f'Report saved! Reference number #{rid}.'); st.balloons(); st.markdown('### Possible matches')
    candidates=list_reports(item_type='Found' if typ=='Lost' else 'Lost',status='Open',limit=500); matches=suggest_matches(get_report(rid),candidates)
    if matches:
     for item,score,reasons in matches[:3]: st.write(f"**{item['title']}** — {score}% similarity · {item['block']} / {item['sublocation']}"); st.caption('Why suggested: '+', '.join(reasons))
    else: st.info('No close matches yet. Your report is saved and searchable.')
 st.caption('Local prototype: reports are saved on the computer running this app, not shared across devices.')
elif page=='Campus Blocks':
 header(); st.markdown('<section class="hero"><div class="eyebrow">Explore by location</div><h1>Your campus.<br>One place to look.</h1><p>Browse reports by the four main campus blocks.</p></section>',unsafe_allow_html=True)
 options=['All blocks']+BLOCKS; default=st.session_state.pop('filter_block','All blocks'); chosen=st.selectbox('Choose a block',options,index=options.index(default) if default in options else 0); typ=st.selectbox('Report type',['All','Lost','Found','Returned'])
 cols=st.columns(4)
 for col,bl in zip(cols,BLOCKS):
  with col: st.markdown(f"<div class='blockcard'><h3 style='font-size:1rem'>{esc(bl)}</h3><div class='muted'>{len(list_reports(block=bl,limit=1000))} reports</div></div>",unsafe_allow_html=True)
 results=list_reports(block=chosen if chosen!='All blocks' else None,item_type=typ if typ in ['Lost','Found'] else None,status='Returned' if typ=='Returned' else None,limit=300)
 if results:
  cols=st.columns(2)
  for i,item in enumerate(results):
   with cols[i%2]: card(item,'blocks')
 else: st.info('No items found for this filter.')
elif page=='Possible Matches':
 header(); st.markdown('<section class="hero"><div class="eyebrow">Local matching</div><h1>Could these be yours?</h1><p>Suggestions compare item names, descriptions, categories and campus locations. A match is not proof of ownership.</p></section>',unsafe_allow_html=True)
 lost=list_reports(item_type='Lost',status='Open',limit=500); found=list_reports(item_type='Found',status='Open',limit=500)
 if not lost or not found: st.info('Add at least one open lost report and one open found report to see suggestions.')
 else:
  ids=[x['id'] for x in lost]; rid=st.selectbox('Select lost report',ids,format_func=lambda i:f"#{i} · {next(x['title'] for x in lost if x['id']==i)}"); matches=suggest_matches(get_report(rid),found)
  if matches:
   for item,score,reasons in matches[:8]:
    st.markdown(f"<div class='card'><span class='tag'>POSSIBLE MATCH</span><span class='tag'>{score}% similarity</span><h3>{esc(item['title'])}</h3><p>{esc(item['description'])}</p><div class='muted'>{esc(item['block'])} · {esc(item['sublocation'])}</div></div>",unsafe_allow_html=True); st.caption('Reason: '+', '.join(reasons))
  else: st.info('No close matches found. Add more descriptive details to reports.')
elif page=='Campus Impact':
 header(); st.markdown('<section class="hero"><div class="eyebrow">Campus impact</div><h1>Every return matters.</h1><p>Live statistics calculated from this prototype database.</p></section>',unsafe_allow_html=True); s=stats(); cols=st.columns(4)
 for col,label,val in zip(cols,['Total reports','Lost reports','Found reports','Returned'],[s['total'],s['lost_all'],s['found_all'],s['returned']]): col.metric(label,val)
 if s['total']: st.progress(min(s['returned']/s['total'],1.0),text=f"{round(s['returned']/s['total']*100)}% marked returned")
 rows=list_reports(limit=1000)
 if rows:
  df=pd.DataFrame(rows); a,b=st.columns(2)
  with a: st.markdown('### Reports by category'); st.bar_chart(df.groupby('category').size().sort_values(ascending=False))
  with b: st.markdown('### Reports by campus block'); st.bar_chart(df.groupby('block').size().sort_values(ascending=False))
 st.caption('Prototype figures only; these are not official university statistics.')
elif page=='Claim an Item':
 header(); st.markdown('<section class="hero"><div class="eyebrow">Recovery request</div><h1>Claim an item.</h1><p>Submit a private verification clue. Never include passwords or full ID numbers.</p></section>',unsafe_allow_html=True); items=list_reports(status='Open',limit=500)
 if not items: st.info('No open reports to claim.')
 else:
  chosen=st.selectbox('Choose report',[x['id'] for x in items],index=next((i for i,x in enumerate(items) if x['id']==st.session_state.get('claim_for')),0),format_func=lambda i:f"#{i} · {next(x['title'] for x in items if x['id']==i)}")
  with st.form('claimform',clear_on_submit=True): claimant=st.text_input('Your name or demo identifier'); contact=st.text_input('Safe contact route'); proof=st.text_area('Private ownership clue'); send=st.form_submit_button('Send claim request',type='primary',use_container_width=True)
  if send:
   if not claimant.strip() or not contact.strip() or not proof.strip(): st.error('Complete all fields.')
   else: cid=add_claim(chosen,claimant.strip(),contact.strip(),proof.strip()); update_status(chosen,'Claim Pending'); st.success(f'Claim submitted. Reference #{cid}. Staff verification is required in real use.'); st.rerun()
 claims=list_claims(); st.subheader('Demo claim requests')
 if claims: st.dataframe(pd.DataFrame([{k:x[k] for k in ['id','item_id','claimant','status','created_at']} for x in claims]),use_container_width=True,hide_index=True)
 else: st.caption('No claims yet.')
elif page=='Admin Demo':
 header(); st.markdown('<section class="hero"><div class="eyebrow">Demonstration only</div><h1>Moderation desk.</h1><p>Review reports and claim requests. This page is not protected by real university authentication.</p></section>',unsafe_allow_html=True); st.warning('Do not deploy this demo admin page publicly as-is. Real authentication and authorisation are required.')
 for item in list_reports(limit=500):
  with st.expander(f"#{item['id']} · {item['item_type']} · {item['title']} · {item['status']}"):
   st.write(item['block'],'/',item['sublocation']); st.write(item['description']); a,b,c=st.columns(3)
   if a.button('Reopen',key=f"open{item['id']}"): update_status(item['id'],'Open'); st.rerun()
   if b.button('Mark returned',key=f"ret{item['id']}"): update_status(item['id'],'Returned'); st.rerun()
   if c.button('Close',key=f"close{item['id']}"): update_status(item['id'],'Closed'); st.rerun()
 st.subheader('Claim requests')
 for claim in list_claims():
  with st.expander(f"Claim #{claim['id']} · report #{claim['item_id']} · {claim['status']}"):
   st.write('Claimant:',claim['claimant']); st.write('Contact:',claim['contact_method']); st.write('Private clue:',claim['proof_note']); a,b=st.columns(2)
   if a.button('Approve claim',key=f"ca{claim['id']}"): update_claim_status(claim['id'],'Approved'); update_status(claim['item_id'],'Returned'); st.rerun()
   if b.button('Reject claim',key=f"cr{claim['id']}"): update_claim_status(claim['id'],'Rejected'); update_status(claim['item_id'],'Open'); st.rerun()
 st.divider(); st.write('Remove only fictional seeded records.');
 if st.button('Remove demo records'): st.session_state.confirm_delete=True
 if st.session_state.get('confirm_delete'):
  st.warning('Confirm removal of seeded demo records?'); a,b=st.columns(2)
  if a.button('Confirm delete',type='primary'): delete_demo_data(); st.session_state.confirm_delete=False; st.rerun()
  if b.button('Cancel'): st.session_state.confirm_delete=False; st.rerun()
st.divider(); st.caption('JAYAN FIND · Kristu Jayanti University · College Lost & Found prototype')
