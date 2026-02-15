# shortcut.py

INJECT_NUMBERS = """
(() => {
  const SELECTOR = "button, a, input, select, textarea, [role='button'], [onclick], .btn, .button";
  const ZINDEX = 2147483647;
  const START_INDEX = 1;

  function qAll(doc, sel) { return Array.from((doc || document).querySelectorAll(sel)); }

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
        } catch (e) {}
      });
    }
    return docs;
  }

  const topDoc = document;
  const topWin = window;
  const docs = collectDocs(topDoc);

  // Clean up existing
  qAll(topDoc, '.ai-visual-wrapper').forEach(b => b.remove());
  docs.forEach(d => qAll(d, '[data-ai-idx]').forEach(el => el.removeAttribute('data-ai-idx')));

  function getAbsoluteRect(element) {
    let r = element.getBoundingClientRect();
    let win = element.ownerDocument.defaultView;
    while (win && win !== topWin) {
      const frameEl = win.frameElement;
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

  const targets = [];
  docs.forEach(d => {
    qAll(d, SELECTOR).forEach(el => {
      try {
        const r = el.getBoundingClientRect();
        const cs = d.defaultView.getComputedStyle(el);
        if (r.width > 2 && r.height > 2 && cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity || '1') > 0.1) {
          targets.push({ el, doc: d });
        }
      } catch (e) {}
    });
  });

  const frag = topDoc.createDocumentFragment();
  const map = new Map();
  let idx = START_INDEX;

  targets.forEach(t => {
    try {
      const el = t.el;
      const abs = getAbsoluteRect(el);
      const thisIdx = idx++;
      el.setAttribute('data-ai-idx', String(thisIdx));

      // Generate a unique color based on index
      const hue = (thisIdx * 137.5) % 360; 
      const color = `hsl(${hue}, 80%, 45%)`;
      const bgColor = `hsla(${hue}, 80%, 45%, 0.15)`;

      // Create a wrapper for the highlight and the label
      const wrapper = topDoc.createElement('div');
      wrapper.className = 'ai-visual-wrapper';
      wrapper.dataset.aiIdx = String(thisIdx);
      
      Object.assign(wrapper.style, {
        position: 'absolute',
        left: `${Math.round(abs.left)}px`,
        top: `${Math.round(abs.top)}px`,
        width: `${Math.round(abs.width)}px`,
        height: `${Math.round(abs.height)}px`,
        border: `2px solid ${color}`,
        backgroundColor: bgColor,
        pointerEvents: 'none',
        zIndex: String(ZINDEX),
        boxSizing: 'border-box'
      });

      // Create the number label at bottom-left outside
      const label = topDoc.createElement('div');
      label.textContent = String(thisIdx);
      Object.assign(label.style, {
        position: 'absolute',
        bottom: '-22px', // Move it outside below the box
        left: '-2px',    // Align with border
        backgroundColor: color,
        color: 'white',
        fontSize: '12px',
        fontWeight: 'bold',
        padding: '1px 4px',
        borderRadius: '0 0 4px 4px',
        whiteSpace: 'nowrap',
        lineHeight: '1.2',
        boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
      });

      wrapper.appendChild(label);
      frag.appendChild(wrapper);
      map.set(String(thisIdx), { el, wrapper, label, color });
    } catch (e) {}
  });

  topDoc.body.appendChild(frag);

  // Sync logic to handle scrolling/layout changes
  function syncAll() {
    for (const [id, pair] of map.entries()) {
      try {
        const { el, wrapper } = pair;
        if (!el.ownerDocument.contains(el)) {
          wrapper.remove();
          map.delete(id);
          continue;
        }
        const abs = getAbsoluteRect(el);
        Object.assign(wrapper.style, {
          left: `${Math.round(abs.left)}px`,
          top: `${Math.round(abs.top)}px`,
          width: `${Math.round(abs.width)}px`,
          height: `${Math.round(abs.height)}px`,
          display: abs.width > 0 ? 'block' : 'none'
        });
      } catch (e) {}
    }
  }

  window.addEventListener('scroll', syncAll, { passive: true, capture: true });
  window.addEventListener('resize', syncAll, { passive: true });
  
  return `Final Index: ${idx - 1}`;
})();
"""

REMOVE_NUMBERS = """
(() => {
    document.querySelectorAll('.ai-visual-wrapper').forEach(e => e.remove());
})();
"""