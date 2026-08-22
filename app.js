const state={topics:[],filter:'all',genre:'すべて'};
const storeKey='bottom-topic-ammo-v1';
const saved=JSON.parse(localStorage.getItem(storeKey)||'{"today":[],"favorite":[],"used":[],"hot":[],"bad":[]}');
const genres=['すべて','食べ物','恋愛','仕事・学校','日常','趣味','価値観','季節','トレンド'];

const $=s=>document.querySelector(s);
const stars=n=>'★'.repeat(n)+'☆'.repeat(5-n);
const persist=()=>localStorage.setItem(storeKey,JSON.stringify(saved));
const toggle=(bucket,id)=>{const i=saved[bucket].indexOf(id);i>=0?saved[bucket].splice(i,1):saved[bucket].push(id);persist();render();};

function todayText(){return new Intl.DateTimeFormat('ja-JP',{month:'long',day:'numeric',weekday:'short'}).format(new Date())}
function setupGenres(){const row=$('#genreRow');genres.forEach(g=>{const b=document.createElement('button');b.textContent=g;b.dataset.genre=g;if(g==='すべて')b.classList.add('active');b.onclick=()=>{state.genre=g;row.querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b));render();};row.appendChild(b);});}

async function load(){
  const evergreen=await fetch('./data/evergreen.json').then(r=>r.json());
  let trend=[];let updated=null;
  try{const payload=await fetch('./data/trends.json?'+Date.now(),{cache:'no-store'}).then(r=>r.json());trend=payload.topics||[];updated=payload.updatedAt;}catch(e){}
  state.topics=[...trend,...evergreen];
  $('#trendStatusDot').style.background=trend.length?'#86efac':'#fcd34d';
  $('#trendStatusText').textContent=trend.length?`トレンド ${trend.length}件`:'定番ネタで表示中';
  $('#sectionMeta').textContent=updated?`トレンド更新: ${new Date(updated).toLocaleString('ja-JP')}`:'トレンド未取得。GitHub Actions設定後に自動更新されます';
  render();
}

function filtered(){
 let arr=[...state.topics];
 if(state.filter==='first')arr=arr.filter(t=>t.scores.first>=4);
 if(state.filter==='short')arr=arr.filter(t=>t.scores.short>=4).sort((a,b)=>b.scores.short-a.scores.short);
 if(state.filter==='saved')arr=arr.filter(t=>saved.today.includes(t.id));
 if(state.filter==='favorite')arr=arr.filter(t=>saved.favorite.includes(t.id));
 if(state.genre!=='すべて')arr=arr.filter(t=>t.genre===state.genre||(state.genre==='トレンド'&&t.source==='Google Trends'));
 return arr.filter(t=>!saved.bad.includes(t.id));
}

function render(){
 const list=$('#topicList');list.innerHTML='';const arr=filtered();
 $('#sectionTitle').textContent={all:'今日のおすすめ',first:'初見向け',short:'今日の切り抜き候補',saved:'今日使う',favorite:'お気に入り'}[state.filter];
 if(!arr.length){list.innerHTML='<div class="empty">まだ話題がありません。別のカテゴリを見てみてください。</div>';return;}
 arr.forEach(t=>{
  const node=$('#topicCardTemplate').content.cloneNode(true);
  node.querySelector('.source-badge').textContent=t.source;
  node.querySelector('.genre-badge').textContent=t.genre;
  node.querySelector('.topic-title').textContent=t.title;
  node.querySelector('.opening').textContent='「'+t.opening+'」';
  node.querySelector('.scores').innerHTML=`<span>💬 ${stars(t.scores.first)}</span><span>🔥 ${stars(t.scores.short)}</span><span>🗣 ${stars(t.scores.expand)}</span>`;
  const tb=node.querySelector('.today-btn');tb.textContent=saved.today.includes(t.id)?'✓ 今日使う':'＋ 今日使う';tb.classList.toggle('on',saved.today.includes(t.id));tb.onclick=()=>toggle('today',t.id);
  const fb=node.querySelector('.fav-btn');fb.textContent=saved.favorite.includes(t.id)?'♥':'♡';fb.classList.toggle('on',saved.favorite.includes(t.id));fb.onclick=()=>toggle('favorite',t.id);
  node.querySelector('.detail-btn').onclick=()=>openDetail(t);
  list.appendChild(node);
 });
}

function openDetail(t){
 $('#modalTitle')?.remove();
 $('#modalContent').innerHTML=`
 <div class="card-topline"><span class="source-badge">${esc(t.source)}</span><span class="genre-badge">${esc(t.genre)}</span></div>
 <h2 id="modalTitle">${esc(t.title)}</h2>
 <p class="detail-label">最初の一言</p><div class="detail-box">${esc(t.opening)}</div>
 <p class="detail-label">話の広げ方</p><ul class="detail-list">${t.expansions.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
 <p class="detail-label">関連する話題</p><div class="related-chips">${t.related.map(x=>`<span>${esc(x)}</span>`).join('')}</div>
 ${t.shortReason?`<p class="detail-label">短尺向きな理由</p><div class="detail-box">${esc(t.shortReason)}</div>`:''}
 ${t.splitPoint?`<p class="detail-label">コメントが割れそうなポイント</p><div class="detail-box">${esc(t.splitPoint)}</div>`:''}
 ${t.videoTitle?`<p class="detail-label">切り抜きタイトル候補</p><div class="detail-box">${esc(t.videoTitle)}</div>`:''}
 <p class="detail-label">向いている用途</p><div class="score-grid"><span>初見コメント</span><span>${stars(t.scores.first)}</span><span>雑談の広げやすさ</span><span>${stars(t.scores.expand)}</span><span>切り抜き</span><span>${stars(t.scores.short)}</span><span>長時間雑談</span><span>${stars(t.scores.long)}</span></div>
 <div class="modal-actions"><button data-a="used">${saved.used.includes(t.id)?'✓ 使用済み':'使用済みにする'}</button><button class="hot" data-a="hot">${saved.hot.includes(t.id)?'🔥 盛り上がった登録済':'🔥 盛り上がった'}</button><button class="bad" data-a="bad">👎 微妙</button><button data-a="today">${saved.today.includes(t.id)?'今日使うから外す':'＋ 今日使う'}</button></div>`;
 $('#modalContent').querySelectorAll('[data-a]').forEach(b=>b.onclick=()=>{toggle(b.dataset.a,t.id);openDetail(t);});
 $('#modalBackdrop').classList.remove('hidden');document.body.style.overflow='hidden';
}
function closeModal(){ $('#modalBackdrop').classList.add('hidden');document.body.style.overflow=''; }
function esc(v){return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function shuffle(){for(let i=state.topics.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[state.topics[i],state.topics[j]]=[state.topics[j],state.topics[i]];}render();}

document.addEventListener('DOMContentLoaded',()=>{
 $('#todayLabel').textContent=todayText();setupGenres();
 $('#tabs').querySelectorAll('button').forEach(b=>b.onclick=()=>{state.filter=b.dataset.filter;$('#tabs').querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b));render();});
 $('#closeModal').onclick=closeModal;$('#modalBackdrop').onclick=e=>{if(e.target.id==='modalBackdrop')closeModal();};$('#shuffleBtn').onclick=shuffle;$('#refreshBtn').onclick=()=>location.reload();
 if('serviceWorker'in navigator)navigator.serviceWorker.register('./sw.js');
 load();
});
