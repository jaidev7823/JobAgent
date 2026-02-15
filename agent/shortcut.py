# shortcut.py

INJECT_NUMBERS = """
(() => {
  // CONFIG
  const SELECTOR = "button, a, input, select, textarea, [role='button'], [onclick], .btn, .button";
  const MIN_VISIBLE_PIXELS = 1;
  const ZINDEX = 2147483647;
  const START_INDEX = 1;

  // Helpers
  function qAll(doc, sel) { return Array.from((doc || document).querySelectorAll(sel)); }

  // 1) Collect same-origin documents (top + reachable iframes recursively)
  function collectDocs(rootDoc) {
    const docs = [rootDoc];
    const stack = [rootDoc];
    while (stack.length) {
      const doc = stack.pop();
      qAll(doc, 'iframe').forEach(iframe => {
        try {
          const childDoc = iframe.contentDocument;
          if (childDoc && !docs.includes(childDoc)) {
            docs.push(childDoc);
            stack.push(childDoc);
          }
        } catch (e) {
          // Cross-origin iframe: ignore (cannot access)
        }
      });
    }
    return docs;
  }

  const topDoc = document;
  const topWin = window;
  const docs = collectDocs(topDoc);

  // 2) HARD RESET: remove badges from top doc and remove accessible data-ai-idx attrs
  // Remove badges in top doc only (all badges will be appended to top document.body).
  qAll(topDoc, '.ai-number-badge').forEach(b => b.remove());
  // Remove data attributes in all accessible docs
  docs.forEach(d => qAll(d, '[data-ai-idx]').forEach(el => el.removeAttribute('data-ai-idx')));

  // 3) Helper: compute absolute rect relative to top document's document coordinates
  function getAbsoluteRect(element) {
    // start with the element's rect inside its own viewport
    let r = element.getBoundingClientRect();
    let win = element.ownerDocument.defaultView;

    // Walk up frames summing frameElement rects to convert into top-level viewport coords
    while (win && win !== topWin) {
      const frameEl = win.frameElement; // element in parent that hosts this window
      if (!frameEl) break;
      const fr = frameEl.getBoundingClientRect();
      r = {
        top: r.top + fr.top,
        left: r.left + fr.left,
        bottom: r.bottom + fr.top,
        right: r.right + fr.left,
        width: r.width,
        height: r.height
      };
      win = win.parent;
    }

    // r.top/left are now relative to the top viewport; add top scroll to get document coordinates
    const scrollY = topWin.scrollY || topWin.pageYOffset || 0;
    const scrollX = topWin.scrollX || topWin.pageXOffset || 0;
    return {
      top: r.top + scrollY,
      left: r.left + scrollX,
      bottom: r.bottom + scrollY,
      right: r.right + scrollX,
      width: r.width,
      height: r.height
    };
  }

  // 4) Visibility guard for an element (uses the element's owner document/window)
  function isVisible(el, rect) {
    try {
      if (!rect) rect = el.getBoundingClientRect();
      if (rect.width <= MIN_VISIBLE_PIXELS || rect.height <= MIN_VISIBLE_PIXELS) return false;
      const cs = el.ownerDocument.defaultView.getComputedStyle(el);
      if (!cs) return false;
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') === 0) return false;
      // Basic viewport check: element's rect must intersect the top window viewport (rough)
      const vpH = topWin.innerHeight, vpW = topWin.innerWidth;
      // We'll compute absolute rect later; here do a cheap viewport presence test for performance:
      if (rect.bottom < 0 || rect.right < 0) return false;
      // allow elements partly in viewport; final absolute position still used.
      return true;
    } catch (e) {
      return false;
    }
  }

  // 5) Collect targets from all accessible documents
  const targets = []; // { el, doc }
  docs.forEach(d => {
    qAll(d, SELECTOR).forEach(el => {
      try {
        const r = el.getBoundingClientRect();
        if (!isVisible(el, r)) return;
        targets.push({ el, doc: d });
      } catch (e) {
        // continue
      }
    });
  });

  // 6) Atomic create: set attribute on element (in its doc) and create badge in top doc
  const frag = topDoc.createDocumentFragment();
  const map = new Map(); // idx -> { el, doc, badge }
  let idx = START_INDEX;
  targets.forEach(t => {
    try {
      const el = t.el;
      const absolute = getAbsoluteRect(el);
      // final visibility check using absolute coordinates and computed style
      const cs = el.ownerDocument.defaultView.getComputedStyle(el);
      if (!cs) return;
      if (absolute.width <= 0 || absolute.height <= 0) return;
      // ATOMIC: set attribute and create badge immediately
      const thisIdx = idx++;
      el.setAttribute('data-ai-idx', String(thisIdx));

      const badge = topDoc.createElement('div');
      badge.className = 'ai-number-badge';
      badge.textContent = String(thisIdx);
      badge.dataset.aiIdx = String(thisIdx);

      Object.assign(badge.style, {
        position: 'absolute',
        left: `${Math.round(absolute.left)}px`,
        top: `${Math.round(absolute.top)}px`,
        background: '#FFFFFF',
        color: '#000000',
        fontSize: '14px',
        padding: '2px 6px',
        border: '1px solid rgba(0,0,0,0.18)',
        boxShadow: '0 2px 6px rgba(0,0,0,0.25)',
        zIndex: String(ZINDEX),
        pointerEvents: 'none',
        lineHeight: '1',
        whiteSpace: 'nowrap',
        transform: 'none',
        willChange: 'top, left',
      });

      frag.appendChild(badge);
      map.set(String(thisIdx), { el, doc: t.doc, badge });
    } catch (e) {
      // keep going; atomicity preserved for successful ones
    }
  });

  topDoc.body.appendChild(frag);

  const total = Math.max(0, idx - START_INDEX);
  if (total === 0) {
    console.log('ai-badge: no visible same-origin targets found (or targets are inside cross-origin iframes).');
    return `Final Index: 0`;
  }

  // 7) Synchronization: update positions when things move.
  let scheduled = false;
  function scheduleSync() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      syncAll();
    });
  }

  function syncAll() {
    for (const [id, pair] of map.entries()) {
      try {
        const { el, badge } = pair;
        // If element removed from DOM, cleanup both sides
        if (!el.ownerDocument || !el.ownerDocument.contains(el)) {
          badge.remove();
          try { el.removeAttribute && el.removeAttribute('data-ai-idx'); } catch {}
          map.delete(id);
          continue;
        }
        // If element not visible now, hide the badge (but keep attribute)
        const r = getAbsoluteRect(el);
        const cs = el.ownerDocument.defaultView.getComputedStyle(el);
        if (!cs || r.width <= 0 || r.height <= 0 || cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') === 0) {
          badge.style.display = 'none';
          continue;
        } else {
          badge.style.display = '';
        }

        badge.style.left = `${Math.round(r.left)}px`;
        badge.style.top = `${Math.round(r.top)}px`;
      } catch (e) {
        // ignore and continue
      }
    }
  }

  // Listen to top scroll/resize
  const onTopScrollResize = () => scheduleSync();
  topWin.addEventListener('scroll', onTopScrollResize, { passive: true, capture: true });
  topWin.addEventListener('resize', onTopScrollResize, { passive: true });

  // For each accessible doc, add scroll/resize listeners on its window (if not top)
  const frameWindows = new Set();
  docs.forEach(d => {
    const w = d.defaultView;
    if (w && w !== topWin && !frameWindows.has(w)) {
      try {
        w.addEventListener('scroll', scheduleSync, { passive: true, capture: true });
        w.addEventListener('resize', scheduleSync, { passive: true });
        frameWindows.add(w);
      } catch (e) {
        // ignore
      }
    }
  });

  // MutationObservers to detect layout changes (top doc and accessible frames)
  const observers = [];
  try {
    docs.forEach(d => {
      try {
        const mo = new d.defaultView.MutationObserver(scheduleSync);
        mo.observe(d.documentElement || d.body || d, {
          attributes: true,
          childList: true,
          subtree: true,
          attributeFilter: ['style', 'class', 'hidden']
        });
        observers.push(mo);
      } catch (e) { /* ignore */ }
    });
  } catch (e) {}

  // ResizeObserver on elements when supported
  let ro = null;
  try {
    if (typeof ResizeObserver !== 'undefined') {
      ro = new ResizeObserver(scheduleSync);
      for (const { el } of map.values()) {
        try { ro.observe(el); } catch (e) { /* ignore */ }
      }
    }
  } catch (e) {}

  // Initial sync
  syncAll();

  // Cleanup function
  function cleanup() {
    try {
      topWin.removeEventListener('scroll', onTopScrollResize, { capture: true });
      topWin.removeEventListener('resize', onTopScrollResize);
    } catch (e) {}
    frameWindows.forEach(w => {
      try {
        w.removeEventListener('scroll', scheduleSync, { capture: true });
        w.removeEventListener('resize', scheduleSync);
      } catch (e) {}
    });
    observers.forEach(o => {
      try { o.disconnect(); } catch (e) {}
    });
    if (ro) {
      try { ro.disconnect(); } catch (e) {}
    }
    for (const [id, pair] of map.entries()) {
      try { pair.badge.remove(); } catch (e) {}
      try { pair.el.removeAttribute('data-ai-idx'); } catch (e) {}
    }
    map.clear();
    // Final wipe of any stray badges in top doc
    qAll(topDoc, '.ai-number-badge').forEach(b => b.remove());
  }

  // Expose cleanup
  try {
    Object.defineProperty(topWin, '__aiNumberBadgeCleanup', {
      value: cleanup,
      writable: false,
      configurable: true,
      enumerable: false
    });
  } catch (e) {}

  console.log(`✅ ai-badge: synchronized ${total} elements across ${docs.length} accessible document(s). Cleanup: window.__aiNumberBadgeCleanup()`);
  return `Final Index: ${total}`;
})();
"""

REMOVE_NUMBERS = """
() => {
    document.querySelectorAll('.ai-number-badge').forEach(e => e.remove());
}
"""