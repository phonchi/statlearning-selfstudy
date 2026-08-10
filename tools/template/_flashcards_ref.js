const FLASHCARDS = [{"front": "線性抽象資料型別（Linear ADT）", "back": "資料元素按序排列、每個元素在單一層次上只跟前後元素相連的抽象資料型別，例子有堆疊與佇列。"}, {"front": "堆疊（Stack）", "back": "遵循「後進先出」順序操作的線性資料結構：最後加入的元素最先被移除（LIFO）。"}, {"front": "前端（Front）", "back": "佇列的起點：最早進來的元素所在位置，dequeue 操作從這一端移除元素。"}, {"front": "後端（Rear）", "back": "佇列的終點：enqueue 操作把新元素加在這一端。"}, {"front": "頂端（Top）", "back": "堆疊最後加入的元素、也是結構目前的端點。因為後進先出，它會最先被移除。"}, {"front": "底部（Base）", "back": "堆疊的最底層：最早放進來的元素所在的位置。"}, {"front": "後進先出（LIFO, Last In First Out）", "back": "堆疊採用的原則：最後放進結構的元素最先被取出。"}, {"front": "中序記法（Infix）", "back": "運算子寫在運算元中間的記法，例如 A + B。"}, {"front": "前序記法（Prefix）", "back": "運算子寫在運算元前面的記法，中序的 A + B 寫成 +AB。"}, {"front": "後序記法（Postfix）", "back": "運算子寫在運算元後面的記法，中序的 A + B 寫成 AB+。"}, {"front": "完全括號運算式（Fully Parenthesized Expression）", "back": "每一個二元或一元運算都用括號明確包住的運算式，運算順序完全沒有歧義。"}, {"front": "佇列（Queue）", "back": "遵循「先進先出」原則的線性資料結構：最先加入的元素最先被移除（FIFO）。"}, {"front": "先進先出（FIFO, First In First Out）", "back": "佇列採用的原則：最先放進結構的元素最先被取出。"}, {"front": "雙端佇列（Deque）", "back": "double-ended queue 的簡稱：前後兩端都能插入與移除元素的資料結構，比標準的佇列或堆疊更有彈性。"}];

/* ===== Flashcards engine ===== */
(function(){
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const grid = document.getElementById('fcGrid');
  if (!grid) return;
  const render = cards => {
    grid.innerHTML = cards.map(c =>
      `<div class="fc-card"><div class="fc-inner">
         <div class="fc-face fc-front"><div>${esc(c.front)}</div><div class="fc-hint">CLICK TO FLIP</div></div>
         <div class="fc-face fc-back">${esc(c.back)}</div>
       </div></div>`).join('');
  };
  render(FLASHCARDS);
  grid.addEventListener('click', e => {
    const card = e.target.closest('.fc-card');
    if (card) card.classList.toggle('flipped');
  });
  document.getElementById('fcShuffle').addEventListener('click', () => render([...FLASHCARDS].sort(() => Math.random() - .5)));
  document.getElementById('fcUnflip').addEventListener('click', () => grid.querySelectorAll('.fc-card').forEach(c => c.classList.remove('flipped')));
  document.getElementById('fcFlipAll').addEventListener('click', () => grid.querySelectorAll('.fc-card').forEach(c => c.classList.add('flipped')));
})();
