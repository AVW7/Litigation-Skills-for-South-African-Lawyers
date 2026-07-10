// State Management
const state = {
  currentView: 'dashboard',
  currentPage: 1,
  currentBase: null,
  vaultData: null,
  activeRuleIndex: 0,
  spotlightSelectedIdx: -1,
  spotlightResults: []
};

// DOM Cache
const dom = {
  sidebar: document.getElementById('sidebar'),
  openSidebarBtn: document.getElementById('openSidebar'),
  closeSidebarBtn: document.getElementById('closeSidebar'),
  breadcrumbs: document.getElementById('breadcrumbs'),
  contentViewport: document.getElementById('contentViewport'),
  
  // Views
  viewDashboard: document.getElementById('view-dashboard'),
  viewNote: document.getElementById('view-note'),
  viewBase: document.getElementById('view-base'),
  
  // Sidebar items
  sidebarChaptersList: document.getElementById('sidebarChaptersList'),
  navLinks: document.querySelectorAll('.nav-link'),
  
  // Dashboard Hero
  startReadingBtn: document.getElementById('startReadingBtn'),
  rulesQuickBtn: document.getElementById('rulesQuickBtn'),
  
  // Rule of the Day
  etiquetteDisplay: document.getElementById('etiquetteDisplay'),
  nextRuleBtn: document.getElementById('nextRuleBtn'),
  
  // Note Reader
  pdfPageBadge: document.getElementById('pdfPageBadge'),
  printedPageBadge: document.getElementById('printedPageBadge'),
  prevPageBtn: document.getElementById('prevPageBtn'),
  nextPageBtn: document.getElementById('nextPageBtn'),
  navPageText: document.getElementById('navPageText'),
  noteMarkdownBody: document.getElementById('noteMarkdownBody'),
  metaChapter: document.getElementById('metaChapter'),
  metaTitle: document.getElementById('metaTitle'),
  metaTags: document.getElementById('metaTags'),
  noteOutlineList: document.getElementById('noteOutlineList'),
  
  // Base Simulator
  baseTitleName: document.getElementById('baseTitleName'),
  baseDescription: document.getElementById('baseDescription'),
  baseSearchInput: document.getElementById('baseSearchInput'),
  baseGroupSelect: document.getElementById('baseGroupSelect'),
  baseViewport: document.getElementById('baseViewport'),
  
  // Theme and Spotlight
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  hudSearchBtn: document.getElementById('hudSearchBtn'),
  spotlightTrigger: document.getElementById('spotlightTrigger'),
  spotlightOverlay: document.getElementById('spotlightOverlay'),
  spotlightInput: document.getElementById('spotlightInput'),
  spotlightResults: document.getElementById('spotlightResults')
};

// Initialize Application
async function init() {
  setupEventListeners();
  await loadVaultData();
  lucide.createIcons();
  
  // Setup initial view
  navigate('dashboard');
  displayRandomRule();
  populateSidebarChapters();
}

// Load compiled JSON data
async function loadVaultData() {
  try {
    const response = await fetch('/vault_data.json');
    if (!response.ok) throw new Error('Failed to fetch vault data');
    state.vaultData = await response.json();
    console.log('Vault data loaded successfully:', state.vaultData);
  } catch (error) {
    console.error('Error loading vault data:', error);
    // Fallback in case of CORS or local serve issues
    state.vaultData = { pages: [], rules: [], bases: {} };
    alert('Failed to load vault data. Please ensure the dev server is running.');
  }
}

// Setup Event Listeners
function setupEventListeners() {
  // Sidebar toggle
  dom.openSidebarBtn.addEventListener('click', () => dom.sidebar.classList.add('active'));
  dom.closeSidebarBtn.addEventListener('click', () => dom.sidebar.classList.remove('active'));

  // Nav link clicks
  dom.navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const view = link.getAttribute('data-view');
      const base = link.getAttribute('data-base');
      
      dom.navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      
      if (view === 'base') {
        state.currentBase = base;
      }
      navigate(view);
      dom.sidebar.classList.remove('active');
    });
  });

  // Theme Toggle
  dom.themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    dom.themeToggleBtn.innerHTML = `<i data-lucide="${isLight ? 'moon' : 'sun'}"></i>`;
    lucide.createIcons();
  });

  // Spotlight Search Events
  const openSpotlight = () => {
    dom.spotlightOverlay.classList.add('active');
    dom.spotlightInput.focus();
    dom.spotlightInput.value = '';
    renderSpotlightResults('');
  };
  
  const closeSpotlight = () => {
    dom.spotlightOverlay.classList.remove('active');
    state.spotlightSelectedIdx = -1;
  };

  dom.spotlightTrigger.addEventListener('click', openSpotlight);
  dom.hudSearchBtn.addEventListener('click', openSpotlight);
  
  dom.spotlightOverlay.addEventListener('click', (e) => {
    if (e.target === dom.spotlightOverlay) closeSpotlight();
  });

  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openSpotlight();
    }
    if (e.key === 'Escape') {
      closeSpotlight();
    }
    if (dom.spotlightOverlay.classList.contains('active')) {
      handleSpotlightNavigation(e);
    }
  });

  dom.spotlightInput.addEventListener('input', (e) => {
    renderSpotlightResults(e.target.value);
  });

  // Hero Actions
  dom.startReadingBtn.addEventListener('click', () => navigateToPage(1));
  dom.rulesQuickBtn.addEventListener('click', () => {
    state.currentBase = 'Rules.base';
    navigate('base');
  });

  // Rule of the Day Action
  dom.nextRuleBtn.addEventListener('click', displayRandomRule);

  // Note Navigation
  dom.prevPageBtn.addEventListener('click', () => navigateToPage(state.currentPage - 1));
  dom.nextPageBtn.addEventListener('click', () => navigateToPage(state.currentPage + 1));

  // Base Controls
  dom.baseSearchInput.addEventListener('input', filterAndRenderBase);
  dom.baseGroupSelect.addEventListener('change', filterAndRenderBase);
  
  // Dashboard Widget Quick Links
  document.querySelectorAll('.quick-nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      navigateToPage(parseInt(item.getAttribute('data-page')));
    });
  });

  document.querySelectorAll('.base-link-card').forEach(card => {
    card.addEventListener('click', () => {
      state.currentBase = card.getAttribute('data-base');
      navigate('base');
    });
  });
}

// Populate Sidebar Chapters list
function populateSidebarChapters() {
  if (!state.vaultData || !state.vaultData.pages) return;
  
  // Group by chapter
  const chapters = {};
  state.vaultData.pages.forEach(p => {
    if (p.chapterNum && !chapters[p.chapterNum]) {
      chapters[p.chapterNum] = {
        title: p.chapter.replace(/^Chapter \d+:\s*/, ''),
        firstPage: p.pdfPage
      };
    }
  });

  dom.sidebarChaptersList.innerHTML = '';
  Object.keys(chapters).sort((a,b) => parseInt(a) - parseInt(b)).forEach(num => {
    const ch = chapters[num];
    const el = document.createElement('a');
    el.className = 'chapter-nav-item';
    el.innerHTML = `<span style="color: hsl(var(--accent-secondary)); margin-right: 8px;">${num}</span> ${ch.title}`;
    el.addEventListener('click', () => navigateToPage(ch.firstPage));
    dom.sidebarChaptersList.appendChild(el);
  });
}

// Display Random Rule of the Day
function displayRandomRule() {
  if (!state.vaultData || !state.vaultData.rules.length) return;
  const idx = Math.floor(Math.random() * state.vaultData.rules.length);
  state.activeRuleIndex = idx;
  const rule = state.vaultData.rules[idx];
  
  dom.etiquetteDisplay.innerHTML = `
    <h4 class="etiquette-title">${rule.title}</h4>
    <div class="etiquette-category">${rule.category}</div>
    <p class="etiquette-text">${rule.content.substring(0, 240)}...</p>
    <a href="#" class="internal-link" id="readFullRuleBtn" style="margin-top: 12px; display: inline-block;">Read Full Rule →</a>
  `;
  
  document.getElementById('readFullRuleBtn').addEventListener('click', (e) => {
    e.preventDefault();
    state.currentBase = 'Rules.base';
    navigate('base');
  });
}

// Navigation Router
function navigate(viewName) {
  state.currentView = viewName;
  
  // Hide all views
  dom.viewDashboard.classList.remove('active');
  dom.viewNote.classList.remove('active');
  dom.viewBase.classList.remove('active');
  
  // Show active view
  const activePanel = document.getElementById(`view-${viewName}`);
  activePanel.classList.add('active');
  
  // Run transition animation
  gsap.fromTo(activePanel, { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out' });
  
  updateBreadcrumbs();
  
  if (viewName === 'note') {
    renderNotePage();
  } else if (viewName === 'base') {
    renderBaseView();
  }
  
  // Reset scroll
  dom.contentViewport.scrollTop = 0;
}

function updateBreadcrumbs() {
  let html = `<span class="breadcrumb-item"><a href="#" class="internal-link" id="bcHome">Vault</a></span>`;
  
  if (state.currentView === 'dashboard') {
    html += ` <span class="breadcrumb-sep">/</span> <span class="breadcrumb-active">Dashboard</span>`;
  } else if (state.currentView === 'note') {
    const page = state.vaultData.pages.find(p => p.pdfPage === state.currentPage);
    const chapterName = page ? page.chapter.split(':')[0] : 'Chapter';
    html += ` <span class="breadcrumb-sep">/</span> <span class="breadcrumb-item">${chapterName}</span>`;
    html += ` <span class="breadcrumb-sep">/</span> <span class="breadcrumb-active">Page ${state.currentPage}</span>`;
  } else if (state.currentView === 'base') {
    html += ` <span class="breadcrumb-sep">/</span> <span class="breadcrumb-active">${state.currentBase}</span>`;
  }
  
  dom.breadcrumbs.innerHTML = html;
  
  const bcHome = document.getElementById('bcHome');
  if (bcHome) {
    bcHome.addEventListener('click', (e) => {
      e.preventDefault();
      navigate('dashboard');
    });
  }
}

// Navigate to specific PDF Page
function navigateToPage(pageIndex) {
  if (pageIndex < 1 || pageIndex > 319) return;
  state.currentPage = pageIndex;
  navigate('note');
}

// Render Note Page Content
function renderNotePage() {
  const page = state.vaultData.pages.find(p => p.pdfPage === state.currentPage);
  if (!page) {
    dom.noteMarkdownBody.innerHTML = `<p>Error loading page content.</p>`;
    return;
  }
  
  // Update indicators
  dom.pdfPageBadge.textContent = `PDF Page ${page.pdfPage}`;
  dom.printedPageBadge.textContent = page.printedPage ? `Printed Page ${page.printedPage}` : 'Intro / Preface';
  dom.navPageText.textContent = `Page ${page.pdfPage} of 319`;
  
  // Note Meta Sidebar
  dom.metaChapter.textContent = page.chapter || 'Unknown';
  dom.metaTitle.textContent = page.title;
  
  dom.metaTags.innerHTML = '';
  page.tags.forEach(tag => {
    const span = document.createElement('span');
    span.className = 'tag-badge';
    span.textContent = `#${tag}`;
    dom.metaTags.appendChild(span);
  });
  
  // Parse Custom Obsidian Markdown Content
  let parsedContent = page.content;
  
  // 1. Convert wikilinks `[[Page-X]]` or `[[Page-X|Label]]`
  parsedContent = parsedContent.replace(/\[\[Page-(\d+)(?:\|([^\]]+))?\]\]/g, (match, pNum, label) => {
    const displayLabel = label || `Page ${pNum}`;
    return `<a href="#" class="obsidian-wikilink" data-page="${pNum}">${displayLabel}</a>`;
  });
  
  // Handle other links like `[[Dashboard]]`
  parsedContent = parsedContent.replace(/\[\[Dashboard\]\]/g, `<a href="#" class="obsidian-dashboard-link">Dashboard</a>`);
  parsedContent = parsedContent.replace(/\[\[rules\]\]/g, `<a href="#" class="obsidian-rules-link">Etiquette Rules</a>`);
  
  // 2. Convert highlights `==text==`
  parsedContent = parsedContent.replace(/==([^=]+)==/g, '<mark>$1</mark>');
  
  // 3. Render Markdown Body
  const html = marked.parse(parsedContent);
  dom.noteMarkdownBody.innerHTML = html;
  
  // Re-process Obsidian specific components after marked HTML rendering
  
  // Handle Wikilinks clicks
  dom.noteMarkdownBody.querySelectorAll('.obsidian-wikilink').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigateToPage(parseInt(link.getAttribute('data-page')));
    });
  });
  
  dom.noteMarkdownBody.querySelectorAll('.obsidian-dashboard-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigate('dashboard');
    });
  });

  dom.noteMarkdownBody.querySelectorAll('.obsidian-rules-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      state.currentBase = 'Rules.base';
      navigate('base');
    });
  });

  // Make check-list checkboxes interactive
  dom.noteMarkdownBody.querySelectorAll('input[type="checkbox"]').forEach(box => {
    box.addEventListener('change', () => {
      // Toggle visual completed class on its parent li
      const li = box.closest('li');
      if (li) {
        if (box.checked) {
          li.style.textDecoration = 'line-through';
          li.style.opacity = '0.5';
        } else {
          li.style.textDecoration = 'none';
          li.style.opacity = '1';
        }
      }
    });
  });
  
  // Build note outline list
  dom.noteOutlineList.innerHTML = '';
  const headings = dom.noteMarkdownBody.querySelectorAll('h1, h2, h3');
  if (headings.length === 0) {
    dom.noteOutlineList.innerHTML = '<span style="color: hsl(var(--color-text-muted)); font-size: 0.8rem;">No headings on this page</span>';
  } else {
    headings.forEach((heading, idx) => {
      const id = `heading-${idx}`;
      heading.id = id;
      
      const link = document.createElement('a');
      link.className = 'outline-link';
      link.textContent = heading.textContent;
      link.style.paddingLeft = heading.tagName === 'H3' ? '12px' : '0px';
      
      link.addEventListener('click', (e) => {
        e.preventDefault();
        heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      dom.noteOutlineList.appendChild(link);
    });
  }
  
  lucide.createIcons();
}

// Render Base view
function renderBaseView() {
  const baseFile = state.currentBase || 'Pages.base';
  dom.baseTitleName.textContent = baseFile;
  
  // Configure Group By options and title description
  dom.baseGroupSelect.innerHTML = '<option value="">No Grouping</option>';
  
  if (baseFile === 'Pages.base') {
    dom.baseDescription.textContent = 'Listing and filtering all 319 Litigation Skills pages.';
    dom.baseGroupSelect.innerHTML += `
      <option value="chapter">Group by Chapter</option>
    `;
  } else if (baseFile === 'Chapters.base') {
    dom.baseDescription.textContent = 'Structured table of contents for book chapters.';
  } else if (baseFile === 'Rules.base') {
    dom.baseDescription.textContent = 'Etiquette & ethical rules cards for South African litigation.';
    dom.baseGroupSelect.innerHTML += `
      <option value="category">Group by Category</option>
    `;
  }
  
  dom.baseSearchInput.value = '';
  filterAndRenderBase();
}

// Filter, group, and render table/cards
function filterAndRenderBase() {
  const baseFile = state.currentBase || 'Pages.base';
  const query = dom.baseSearchInput.value.toLowerCase().trim();
  const groupBy = dom.baseGroupSelect.value;
  
  dom.baseViewport.innerHTML = '';
  
  if (baseFile === 'Pages.base') {
    // Render Pages Table
    let rows = state.vaultData.pages;
    if (query) {
      rows = rows.filter(r => 
        r.title.toLowerCase().includes(query) || 
        r.chapter.toLowerCase().includes(query) ||
        r.pdfPage.toString().includes(query)
      );
    }
    
    // Grouping & Rendering
    const container = document.createElement('div');
    container.className = 'base-table-container';
    
    const table = document.createElement('table');
    table.className = 'base-table';
    table.innerHTML = `
      <thead>
        <tr>
          <th>Note Name</th>
          <th>PDF Page</th>
          <th>Printed Page</th>
          <th>Chapter</th>
        </tr>
      </thead>
      <tbody id="baseTableBody">
      </tbody>
    `;
    container.appendChild(table);
    dom.baseViewport.appendChild(container);
    
    const tbody = table.querySelector('#baseTableBody');
    
    if (groupBy === 'chapter') {
      // Group pages by chapter
      const groups = {};
      rows.forEach(r => {
        if (!groups[r.chapter]) groups[r.chapter] = [];
        groups[r.chapter].push(r);
      });
      
      Object.keys(groups).forEach(groupName => {
        // Group Header Row
        const hr = document.createElement('tr');
        hr.className = 'group-row';
        hr.innerHTML = `<td colspan="4">${groupName} (${groups[groupName].length} pages)</td>`;
        tbody.appendChild(hr);
        
        groups[groupName].forEach(p => {
          const tr = document.createElement('tr');
          tr.style.cursor = 'pointer';
          tr.innerHTML = `
            <td><a href="#" class="page-link" data-page="${p.pdfPage}">Page-${p.pdfPage}.md</a></td>
            <td>${p.pdfPage}</td>
            <td>${p.printedPage || '--'}</td>
            <td>${p.chapter}</td>
          `;
          tr.addEventListener('click', () => navigateToPage(p.pdfPage));
          tbody.appendChild(tr);
        });
      });
    } else {
      // Plain render
      rows.forEach(p => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.innerHTML = `
          <td><a href="#" class="page-link" data-page="${p.pdfPage}">Page-${p.pdfPage}.md</a></td>
          <td>${p.pdfPage}</td>
          <td>${p.printedPage || '--'}</td>
          <td>${p.chapter}</td>
        `;
        tr.addEventListener('click', () => navigateToPage(p.pdfPage));
        tbody.appendChild(tr);
      });
    }
    
  } else if (baseFile === 'Chapters.base') {
    // Render Chapters List View
    const chapters = {};
    state.vaultData.pages.forEach(p => {
      if (p.chapterNum && !chapters[p.chapterNum]) {
        chapters[p.chapterNum] = {
          num: p.chapterNum,
          name: p.chapter,
          startPage: p.pdfPage
        };
      }
    });
    
    let rows = Object.values(chapters).sort((a,b) => a.num - b.num);
    if (query) {
      rows = rows.filter(r => r.name.toLowerCase().includes(query));
    }
    
    const container = document.createElement('div');
    container.className = 'base-table-container';
    
    const table = document.createElement('table');
    table.className = 'base-table';
    table.innerHTML = `
      <thead>
        <tr>
          <th>Chapter Name</th>
          <th>Starting Page</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(r => `
          <tr style="cursor: pointer;" data-page="${r.startPage}">
            <td><strong>Chapter ${r.num}</strong>: ${r.name.replace(/^Chapter \d+:\s*/, '')}</td>
            <td>Page ${r.startPage}</td>
          </tr>
        `).join('')}
      </tbody>
    `;
    container.appendChild(table);
    dom.baseViewport.appendChild(container);
    
    table.querySelectorAll('tr').forEach(row => {
      const page = row.getAttribute('data-page');
      if (page) {
        row.addEventListener('click', () => navigateToPage(parseInt(page)));
      }
    });
    
  } else if (baseFile === 'Rules.base') {
    // Render Rules Cards View
    let cardData = state.vaultData.rules;
    if (query) {
      cardData = cardData.filter(r => 
        r.title.toLowerCase().includes(query) || 
        r.content.toLowerCase().includes(query) ||
        r.category.toLowerCase().includes(query)
      );
    }
    
    const grid = document.createElement('div');
    grid.className = 'base-cards-grid';
    dom.baseViewport.appendChild(grid);
    
    if (groupBy === 'category') {
      const cats = {};
      cardData.forEach(r => {
        if (!cats[r.category]) cats[r.category] = [];
        cats[r.category].push(r);
      });
      
      Object.keys(cats).forEach(catName => {
        // Render Group Category Header
        const header = document.createElement('div');
        header.style.gridColumn = '1 / -1';
        header.style.marginTop = '20px';
        header.style.borderBottom = '1px solid rgba(var(--border-glass))';
        header.style.paddingBottom = '8px';
        header.innerHTML = `<h3 style="font-family: var(--font-display); font-weight: 700;">${catName} (${cats[catName].length} rules)</h3>`;
        grid.appendChild(header);
        
        cats[catName].forEach(rule => {
          const card = document.createElement('div');
          card.className = 'base-card-item glass';
          card.innerHTML = `
            <span class="category">${rule.category}</span>
            <h4>${rule.title}</h4>
            <div class="body">${formatRuleBody(rule.content)}</div>
          `;
          grid.appendChild(card);
        });
      });
    } else {
      cardData.forEach(rule => {
        const card = document.createElement('div');
        card.className = 'base-card-item glass';
        card.innerHTML = `
          <span class="category">${rule.category}</span>
          <h4>${rule.title}</h4>
          <div class="body">${formatRuleBody(rule.content)}</div>
        `;
        grid.appendChild(card);
      });
    }
  }
}

// Convert rule body text (which might have markdown-like lists) to beautiful HTML list
function formatRuleBody(text) {
  let lines = text.split('\n');
  let html = '';
  lines.forEach(line => {
    line = line.trim();
    if (line.startsWith('*') || line.startsWith('-') || line.startsWith('☐')) {
      const clean = line.replace(/^[\*\-☐]\s*/, '');
      html += `<li>${clean}</li>`;
    } else {
      if (html && !html.endsWith('</ul>')) {
        html += '</ul>';
      }
      if (line) {
        html += `<p style="margin-bottom: 8px;">${line}</p>`;
      }
    }
  });
  if (html.includes('<li>') && !html.includes('<ul>')) {
    html = `<ul style="margin-left: 16px; margin-bottom: 8px;">${html}</ul>`;
  }
  return html;
}

// Render Spotlight search results
function renderSpotlightResults(query) {
  dom.spotlightResults.innerHTML = '';
  state.spotlightSelectedIdx = -1;
  
  if (!state.vaultData) return;
  
  const q = query.toLowerCase().trim();
  let results = [];
  
  if (!q) {
    // Show recent/default quick links
    results = [
      { type: 'action', title: 'Go to Dashboard', subtitle: 'View main overview widgets', icon: 'layout-dashboard', action: () => navigate('dashboard') },
      { type: 'action', title: 'Open Pages Database', subtitle: 'Spreadsheet list of all pages', icon: 'database', action: () => { state.currentBase = 'Pages.base'; navigate('base'); } },
      { type: 'action', title: 'Open Court Etiquette Rules', subtitle: 'Litigation rules checklist cards', icon: 'shield-alert', action: () => { state.currentBase = 'Rules.base'; navigate('base'); } },
      { type: 'note', title: 'Page 3: Client Interviewing Intro', subtitle: 'Chapter 1 starting page', icon: 'book-open', action: () => navigateToPage(3) },
      { type: 'note', title: 'Page 126: Courtroom Protocol', subtitle: 'Chapter 15 starting page', icon: 'scale', action: () => navigateToPage(126) }
    ];
  } else {
    // 1. Search Pages (by title or content)
    state.vaultData.pages.forEach(p => {
      const matchTitle = p.title.toLowerCase().includes(q);
      const matchContent = p.content.toLowerCase().includes(q);
      
      if (matchTitle || matchContent) {
        results.push({
          type: 'note',
          title: p.title,
          subtitle: `PDF Page ${p.pdfPage} • ${p.chapter}`,
          icon: 'book-open',
          score: matchTitle ? 10 : 1,
          action: () => navigateToPage(p.pdfPage)
        });
      }
    });
    
    // 2. Search Rules
    state.vaultData.rules.forEach(r => {
      const matchTitle = r.title.toLowerCase().includes(q);
      const matchContent = r.content.toLowerCase().includes(q);
      
      if (matchTitle || matchContent) {
        results.push({
          type: 'rule',
          title: r.title,
          subtitle: `Rule • ${r.category}`,
          icon: 'shield-alert',
          score: matchTitle ? 8 : 2,
          action: () => {
            state.currentBase = 'Rules.base';
            navigate('base');
            // Give filter input the value
            dom.baseSearchInput.value = r.title;
            filterAndRenderBase();
          }
        });
      }
    });
    
    // Sort by score
    results.sort((a, b) => b.score - a.score);
    results = results.slice(0, 8); // Limit to 8 results
  }
  
  state.spotlightResults = results;
  
  if (results.length === 0) {
    dom.spotlightResults.innerHTML = `<div class="spotlight-item" style="cursor: default; justify-content: center;"><span style="color: hsl(var(--color-text-muted)); font-size: 0.9rem;">No results found for "${query}"</span></div>`;
    return;
  }
  
  results.forEach((r, idx) => {
    const el = document.createElement('div');
    el.className = 'spotlight-item';
    el.innerHTML = `
      <i data-lucide="${r.icon || 'file-text'}"></i>
      <div>
        <div class="title">${r.title}</div>
        <div class="subtitle">${r.subtitle}</div>
      </div>
    `;
    el.addEventListener('click', () => {
      r.action();
      dom.spotlightOverlay.classList.remove('active');
    });
    dom.spotlightResults.appendChild(el);
  });
  
  lucide.createIcons();
}

// Handle spotlight keyboard navigation (Arrow Up, Arrow Down, Enter)
function handleSpotlightNavigation(e) {
  const items = dom.spotlightResults.querySelectorAll('.spotlight-item');
  if (items.length === 0) return;
  
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    state.spotlightSelectedIdx = (state.spotlightSelectedIdx + 1) % items.length;
    updateSpotlightSelection(items);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    state.spotlightSelectedIdx = (state.spotlightSelectedIdx - 1 + items.length) % items.length;
    updateSpotlightSelection(items);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (state.spotlightSelectedIdx >= 0 && state.spotlightSelectedIdx < items.length) {
      items[state.spotlightSelectedIdx].click();
    } else if (items.length > 0) {
      // Click first item by default
      items[0].click();
    }
  }
}

function updateSpotlightSelection(items) {
  items.forEach((item, idx) => {
    if (idx === state.spotlightSelectedIdx) {
      item.classList.add('selected');
      item.scrollIntoView({ block: 'nearest' });
    } else {
      item.classList.remove('selected');
    }
  });
}

// Run application
window.addEventListener('DOMContentLoaded', init);
