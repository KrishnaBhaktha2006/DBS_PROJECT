const DEFAULT_API_BASE = localStorage.getItem('marketdeck_api_base') || 'http://127.0.0.1:8000';
const state = {
  apiBase: DEFAULT_API_BASE,
  token: localStorage.getItem('marketdeck_token') || '',
  me: null,
  listings: [],
  categories: [],
  notifications: [],
  alerts: [],
  transactions: [],
  selectedListing: null,
  selectedOffers: [],
  loading: true,
  busy: false,
  error: '',
  view: 'explore',
  filters: {
    type: '',
    c_id: '',
    price_min: '',
    price_max: '',
    status: 'active',
    search: '',
  },
  toasts: [],
};

const el = document.getElementById('app');

function normalizeResponse(payload) {
  if (payload && typeof payload === 'object' && 'success' in payload) {
    if (!payload.success) {
      throw new Error(payload.detail || payload.message || 'Request failed');
    }
    return payload.data;
  }
  return payload;
}

async function api(path, options = {}) {
  const { auth = true, headers = {}, body, method = 'GET' } = options;
  const requestHeaders = { Accept: 'application/json', ...headers };

  if (body !== undefined) {
    requestHeaders['Content-Type'] = 'application/json';
  }

  if (auth && state.token) {
    requestHeaders.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(`${state.apiBase}${path}`, {
    method,
    headers: requestHeaders,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  let payload = null;
  const text = await response.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch (error) {
      payload = { detail: text };
    }
  }

  const data = normalizeResponse(payload);

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || payload?.message || `HTTP ${response.status}`);
  }

  return data;
}

function setBusy(value) {
  state.busy = value;
  render();
}

function pushToast(title, message, kind = 'info') {
  const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  state.toasts = [{ id, title, message, kind }, ...state.toasts].slice(0, 4);
  render();
  window.setTimeout(() => {
    state.toasts = state.toasts.filter((toast) => toast.id !== id);
    render();
  }, 3200);
}

function formatDate(value) {
  if (!value) return 'n/a';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString([], {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
}

function currency(value) {
  const number = Number(value ?? 0);
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(Number.isFinite(number) ? number : 0);
}

function flattenCategories(nodes, depth = 0, result = []) {
  for (const node of nodes || []) {
    result.push({ ...node, depth });
    if (node.children?.length) {
      flattenCategories(node.children, depth + 1, result);
    }
  }
  return result;
}

function findCategoryName(c_id) {
  const lookup = flattenCategories(state.categories);
  return lookup.find((category) => String(category.c_id) === String(c_id))?.name || `Category ${c_id}`;
}

function getListingStatusPill(status) {
  const lower = String(status || '').toLowerCase();
  if (lower === 'active') return 'success';
  if (lower === 'sold' || lower === 'closed') return 'warning';
  return 'soft';
}

function getOfferStatusClass(status) {
  const lower = String(status || '').toLowerCase();
  if (lower === 'accepted') return 'success';
  if (lower === 'rejected') return 'danger';
  return 'soft';
}

function getTimeAgo(date) {
  if (!date || Number.isNaN(date.getTime())) return 'recently';
  const seconds = Math.floor((Date.now() - date) / 1000);
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 2592000) return `${Math.floor(seconds / 86400)}d ago`;
  return `${Math.floor(seconds / 2592000)}mo ago`;
}

function updateStateFromForm(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function renderAppShell() {
  const categoryFlat = flattenCategories(state.categories);
  const selected = state.selectedListing;
  const ownerView = selected && state.me && Number(selected.u_id) === Number(state.me.u_id);
  const offerForListing = selected ? state.selectedOffers : [];
  const unreadNotifications = state.notifications.filter((item) => !Number(item.seen)).length;

  const listingCategories = ['<option value="">All categories</option>']
    .concat(
      categoryFlat.map((category) => {
        const indent = '— '.repeat(category.depth);
        return `<option value="${category.c_id}">${indent}${escapeHtml(category.name)}</option>`;
      }),
    )
    .join('');

  const createCategoryOptions = ['<option value="">Top level</option>']
    .concat(
      categoryFlat.map((category) => {
        const indent = '— '.repeat(category.depth);
        return `<option value="${category.c_id}">${indent}${escapeHtml(category.name)}</option>`;
      }),
    )
    .join('');

  el.innerHTML = `
    <div class="shell">
      ${renderTopbar()}

      <section class="hero">
        <div class="hero-grid">
          <div>
            <h1>Buy, sell & connect with trusted traders</h1>
            <p>Browse thousands of listings, manage your active sales and purchases, and grow your trading reputation.</p>
            <div class="hero-actions">
              <button class="button" data-scroll-to="explore">Browse listings</button>
              <button class="button-secondary" data-scroll-to="actions">My account</button>
            </div>
          </div>
          <div class="hero-badges" style="display: none;">
            <div class="stat-grid">
              <article class="stat">
                <p class="stat-value">${state.listings.length}</p>
                <p class="stat-label">Listings loaded</p>
              </article>
              <article class="stat">
                <p class="stat-value">${state.categories.length}</p>
                <p class="stat-label">Categories in tree</p>
              </article>
              <article class="stat">
                <p class="stat-value">${unreadNotifications}</p>
                <p class="stat-label">Unread notifications</p>
              </article>
            </div>
            <div class="mini-card">
              <div class="split-title">
                <strong>Current session</strong>
                <span class="pill ${state.token ? 'success' : ''}">${state.token ? 'Authenticated' : 'Guest mode'}</span>
              </div>
              <p class="micro">API: ${escapeHtml(state.apiBase)}</p>
              <p class="micro">${state.me ? `Signed in as ${escapeHtml(state.me.username)} (#${state.me.u_id})` : 'Login or register to create content and manage your data.'}</p>
            </div>
          </div>
        </div>
      </section>

      <div class="main-grid" id="explore">
        <aside class="section">
          <div class="section-header">
            <div>
              <p class="kicker">Categories</p>
              <h2>Tree view</h2>
            </div>
            <button class="button-quiet" data-action="refresh-categories">Refresh</button>
          </div>
          ${renderCategoryTree()}
          <div class="divider"></div>
          <div class="stack">
            <div class="field">
              <label class="label" for="apiBase">API base URL</label>
              <input class="ghost-input" id="apiBase" value="${escapeHtml(state.apiBase)}" spellcheck="false" />
            </div>
            <button class="button-secondary" data-action="save-api-base">Save API base</button>
          </div>
        </aside>

        <main class="section section-columns">
          <div class="section-header">
            <div>
              <p class="kicker">Browse</p>
              <h2>Listings</h2>
            </div>
            <span class="pill">Public endpoint</span>
          </div>

          <form class="filter-row" id="filterForm">
            <div class="field">
              <label class="label" for="type">Type</label>
              <select class="select" id="type" name="type">
                <option value="">All</option>
                <option value="buy" ${state.filters.type === 'buy' ? 'selected' : ''}>Buy</option>
                <option value="sell" ${state.filters.type === 'sell' ? 'selected' : ''}>Sell</option>
              </select>
            </div>
            <div class="field">
              <label class="label" for="status">Status</label>
              <select class="select" id="status" name="status">
                <option value="active" ${state.filters.status === 'active' ? 'selected' : ''}>Active</option>
                <option value="sold" ${state.filters.status === 'sold' ? 'selected' : ''}>Sold</option>
                <option value="closed" ${state.filters.status === 'closed' ? 'selected' : ''}>Closed</option>
                <option value="fulfilled" ${state.filters.status === 'fulfilled' ? 'selected' : ''}>Fulfilled</option>
                <option value="" ${state.filters.status === '' ? 'selected' : ''}>Any</option>
              </select>
            </div>
            <div class="field">
              <label class="label" for="c_id">Category</label>
              <select class="select" id="c_id" name="c_id">
                ${listingCategories}
              </select>
            </div>
            <div class="field">
              <label class="label" for="price_min">Min price</label>
              <input class="input" id="price_min" name="price_min" type="number" step="0.01" placeholder="0" value="${escapeHtml(state.filters.price_min)}" />
            </div>
            <div class="field">
              <label class="label" for="price_max">Max price</label>
              <input class="input" id="price_max" name="price_max" type="number" step="0.01" placeholder="100000" value="${escapeHtml(state.filters.price_max)}" />
            </div>
            <div class="field">
              <label class="label" for="search">Search local results</label>
              <input class="input" id="search" name="search" placeholder="title, seller, category" value="${escapeHtml(state.filters.search || '')}" />
            </div>
            <div class="field full action-row">
              <button class="button" type="submit">Apply filters</button>
              <button class="button-secondary" type="button" data-action="reset-filters">Reset</button>
            </div>
          </form>

          <div class="cards-grid">
            ${renderListingCards()}
          </div>
        </main>

        <aside class="detail-card" id="actions">
          <div class="section-header">
            <div>
              <p class="kicker">Detail view</p>
              <h2>Selected listing</h2>
            </div>
            ${state.selectedListing ? `<span class="pill ${getListingStatusPill(state.selectedListing.status)}">${escapeHtml(state.selectedListing.status)}</span>` : '<span class="pill">None selected</span>'}
          </div>
          ${renderSelectedListing(selected, ownerView, offerForListing, createCategoryOptions)}
        </aside>
      </div>

      <section class="section" id="dashboard">
        <div class="section-header">
          <div>
            <p class="kicker">Workbench</p>
            <h2>Actions and activity</h2>
          </div>
          <div class="tabs">
            <button class="tab ${state.view === 'auth' ? 'active' : ''}" data-view="auth">Auth</button>
            <button class="tab ${state.view === 'create' ? 'active' : ''}" data-view="create">Create</button>
            <button class="tab ${state.view === 'activity' ? 'active' : ''}" data-view="activity">Activity</button>
          </div>
        </div>

        <div class="stack">
          ${state.view === 'auth' ? renderAuthPanel() : ''}
          ${state.view === 'create' ? renderCreatePanel(createCategoryOptions) : ''}
          ${state.view === 'activity' ? renderActivityPanel() : ''}
        </div>
      </section>
    </div>

    <div class="toast-wrap">
      ${state.toasts
        .map(
          (toast) => `
            <div class="toast ${toast.kind}">
              <strong>${escapeHtml(toast.title)}</strong>
              <div>${escapeHtml(toast.message)}</div>
            </div>
          `,
        )
        .join('')}
    </div>
  `;

  attachEvents();
  syncSelectedControls();
}

function renderTopbar() {
  const statusClass = state.loading ? 'status-dot' : 'status-dot live';
  return `
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark">M</div>
        <h1 class="brand-title">Marketplace</h1>
      </div>

      <div class="status-stack">
        <span class="status-label" style="display: none;">Status</span>
      </div>

      <button class="button-secondary" data-view="${state.token ? 'activity' : 'auth'}">${state.token ? 'Dashboard' : 'Login'}</button>
      <div>
        ${state.token ? '<button class="button-danger" data-action="logout">Sign out</button>' : '<span class="pill">Guest</span>'}
      </div>
    </header>
  `;
}

function renderCategoryTree() {
  if (!state.categories.length) {
    return '<div class="empty">No categories loaded yet.</div>';
  }

  const renderNodes = (nodes) => `
    <ul class="tree">
      ${nodes
        .map(
          (node) => `
            <li class="tree-item">
              <div class="tree-node">
                <div>
                  <strong>${escapeHtml(node.name)}</strong>
                  <div class="micro">ID ${node.c_id}${node.parent_id ? ` • parent ${node.parent_id}` : ' • root'}</div>
                </div>
                <span class="pill">${node.children?.length || 0} child${node.children?.length === 1 ? '' : 'ren'}</span>
              </div>
              ${node.children?.length ? `<div class="tree-children">${renderNodes(node.children)}</div>` : ''}
            </li>
          `,
        )
        .join('')}
    </ul>
  `;

  return renderNodes(state.categories);
}

function renderListingCards() {
  const filtered = applyLocalListingSearch(state.listings);

  if (!filtered.length) {
    return '<div class="empty">No listings match the current filters.</div>';
  }

  return filtered
    .map((listing) => {
      const selected = state.selectedListing?.listing_id === listing.listing_id;
      const timeAgo = getTimeAgo(new Date(listing.created_at));
      return `
        <article class="listing-card ${selected ? 'selected' : ''}" data-listing-id="${listing.listing_id}">
          <div class="listing-header">
            <div class="listing-info">
              <h3 class="listing-title">${escapeHtml(listing.title)}</h3>
              <div class="listing-meta">
                <span class="micro">${escapeHtml(listing.seller_username || `User ${listing.u_id}`)}</span>
                <span class="micro">• ${timeAgo}</span>
              </div>
            </div>
            <div class="listing-price">${currency(listing.price)}</div>
          </div>
          <p class="listing-desc">${escapeHtml((listing.description || '').substring(0, 80))}${(listing.description || '').length > 80 ? '...' : ''}</p>
          <div class="listing-footer">
            <span class="chip ${getListingStatusPill(listing.status)}">${escapeHtml(listing.status)}</span>
            <span class="chip soft">${escapeHtml(listing.type)}</span>
            <button class="button-quiet" data-action="select-listing" data-listing-id="${listing.listing_id}" style="margin-left: auto;">View →</button>
          </div>
        </article>
      `;
    })
    .join('');
}

function renderSelectedListing(selected, ownerView, offers, categoryOptions) {
  if (!selected) {
    return `
      <div class="empty">
        Pick a listing from the feed to see details, place an offer, or manage it if you own it.
      </div>
    `;
  }

  return `
    <div class="stack">
      <div>
        <p class="eyebrow">${escapeHtml(selected.type)} listing</p>
        <h3 class="detail-title">${escapeHtml(selected.title)}</h3>
        <div class="detail-meta" style="margin-top: 10px;">
          <span class="pill ${getListingStatusPill(selected.status)}">${escapeHtml(selected.status)}</span>
          <span class="pill">${currency(selected.price)}</span>
          <span class="pill">${escapeHtml(selected.cond || 'n/a')}</span>
        </div>
      </div>

      <div class="detail-panel">
        <div class="mini-card">
          <p class="micro">Seller</p>
          <strong>${escapeHtml(selected.seller_username || `User ${selected.u_id}`)}</strong>
          <div class="micro">Category: ${escapeHtml(selected.category_name || findCategoryName(selected.c_id))}</div>
          <div class="micro">Created: ${formatDate(selected.created_at)}</div>
        </div>
        <p class="detail-description">${escapeHtml(selected.description || 'No description provided.')}</p>
      </div>

      ${state.token && !ownerView && selected.status === 'active' ? renderOfferForm(selected) : ''}
      ${state.token && ownerView ? renderOwnerTools(selected, offers, categoryOptions) : ''}
      ${state.token && ownerView ? renderEditListingForm(selected) : ''}
    </div>
  `;
}

function renderOfferForm(selected) {
  return `
    <form class="stack" id="offerForm">
      <div class="divider"></div>
      <h3>Place offer</h3>
      <div class="field">
        <label class="label" for="offered_price">Offered price</label>
        <input class="input" id="offered_price" name="offered_price" type="number" step="0.01" min="0" placeholder="Enter your amount" />
      </div>
      <div class="field">
        <label class="label" for="message">Message</label>
        <textarea class="textarea" id="message" name="message" placeholder="Add a short message to the seller"></textarea>
      </div>
      <input type="hidden" name="listing_id" value="${selected.listing_id}" />
      <button class="button" type="submit">Send offer</button>
    </form>
  `;
}

function renderOwnerTools(selected, offers) {
  return `
    <section class="stack">
      <div class="divider"></div>
      <div class="split-title">
        <h3>Seller tools</h3>
        <button class="button-quiet" data-action="refresh-offers">Refresh offers</button>
      </div>
      <div class="mini-card">
        <p class="micro">Offer count</p>
        <strong>${offers.length}</strong>
      </div>
      ${offers.length ? renderOfferList(offers) : '<div class="empty">No offers yet for this listing.</div>'}
    </section>
  `;
}

function renderOfferList(offers) {
  return `
    <div class="stack">
      ${offers
        .map(
          (offer) => `
            <article class="timeline-item">
              <div class="split-title">
                <strong>${escapeHtml(offer.buyer_username || `Buyer ${offer.buyer_id}`)}</strong>
                <span class="pill ${getOfferStatusClass(offer.status)}">${escapeHtml(offer.status)}</span>
              </div>
              <div class="meta-row">
                <span class="pill">${currency(offer.offered_price)}</span>
                <span class="pill">${formatDate(offer.created_at)}</span>
              </div>
              <div class="muted">${escapeHtml(offer.message || 'No message provided.')}</div>
              ${offer.status === 'pending' ? `
                <div class="action-row">
                  <button class="button" data-action="accept-offer" data-offer-id="${offer.offer_id}">Accept</button>
                  <button class="button-danger" data-action="reject-offer" data-offer-id="${offer.offer_id}">Reject</button>
                </div>
              ` : ''}
            </article>
          `,
        )
        .join('')}
    </div>
  `;
}

function renderEditListingForm(selected) {
  return `
    <form class="stack" id="listingEditForm">
      <div class="divider"></div>
      <h3>Edit listing</h3>
      <input type="hidden" name="listing_id" value="${selected.listing_id}" />
      <div class="form-grid">
        <div class="field full">
          <label class="label" for="edit_title">Title</label>
          <input class="input" id="edit_title" name="title" value="${escapeHtml(selected.title)}" />
        </div>
        <div class="field full">
          <label class="label" for="edit_description">Description</label>
          <textarea class="textarea" id="edit_description" name="description">${escapeHtml(selected.description || '')}</textarea>
        </div>
        <div class="field">
          <label class="label" for="edit_price">Price</label>
          <input class="input" id="edit_price" name="price" type="number" step="0.01" value="${escapeHtml(selected.price)}" />
        </div>
        <div class="field">
          <label class="label" for="edit_cond">Condition</label>
          <select class="select" id="edit_cond" name="cond">
            ${['new', 'like_new', 'good', 'fair', 'poor'].map((cond) => `<option value="${cond}" ${selected.cond === cond ? 'selected' : ''}>${cond}</option>`).join('')}
          </select>
        </div>
        <div class="field full">
          <label class="label" for="edit_status">Status</label>
          <select class="select" id="edit_status" name="status">
            ${['active', 'sold', 'closed', 'fulfilled'].map((status) => `<option value="${status}" ${selected.status === status ? 'selected' : ''}>${status}</option>`).join('')}
          </select>
        </div>
      </div>
      <button class="button-secondary" type="submit">Save listing</button>
      <button class="button-danger" type="button" data-action="delete-listing" data-listing-id="${selected.listing_id}">Close listing</button>
    </form>
  `;
}

function renderAuthPanel() {
  return `
    <section class="auth-card" id="auth">
      <div class="section-header">
        <div>
          <p class="kicker">Session</p>
          <h2>Authentication</h2>
        </div>
        <span class="pill ${state.token ? 'success' : ''}">${state.token ? 'Connected' : 'Not signed in'}</span>
      </div>
      <div class="auth-grid">
        <form class="stack" id="loginForm">
          <h3>Login</h3>
          <div class="field">
            <label class="label" for="login_email">Email</label>
            <input class="input" id="login_email" name="email" type="email" required />
          </div>
          <div class="field">
            <label class="label" for="login_password">Password</label>
            <input class="input" id="login_password" name="password" type="password" required />
          </div>
          <button class="button" type="submit">Login</button>
        </form>

        <form class="stack" id="registerForm">
          <h3>Register</h3>
          <div class="field">
            <label class="label" for="reg_username">Username</label>
            <input class="input" id="reg_username" name="username" required />
          </div>
          <div class="field">
            <label class="label" for="reg_email">Email</label>
            <input class="input" id="reg_email" name="email" type="email" required />
          </div>
          <div class="field">
            <label class="label" for="reg_password">Password</label>
            <input class="input" id="reg_password" name="password" type="password" required />
          </div>
          <div class="field">
            <label class="label" for="reg_phone">Phone</label>
            <input class="input" id="reg_phone" name="phone" placeholder="Optional" />
          </div>
          <button class="button-secondary" type="submit">Create account</button>
        </form>
      </div>
      <p class="auth-note">
        JWT tokens are stored in localStorage and sent as a Bearer token to protected routes.
      </p>
    </section>
  `;
}

function renderCreatePanel(createCategoryOptions) {
  return `
    <section class="section" id="create">
      <div class="section-header">
        <div>
          <p class="kicker">Create</p>
          <h2>Compose new data</h2>
        </div>
        <span class="pill">Authenticated routes</span>
      </div>

      <div class="form-grid">
        <form class="stack panel" id="createListingForm">
          <h3>Create listing</h3>
          <div class="field">
            <label class="label" for="listing_title">Title</label>
            <input class="input" id="listing_title" name="title" required />
          </div>
          <div class="field">
            <label class="label" for="listing_description">Description</label>
            <textarea class="textarea" id="listing_description" name="description"></textarea>
          </div>
          <div class="form-row">
            <div class="field">
              <label class="label" for="listing_price">Price</label>
              <input class="input" id="listing_price" name="price" type="number" step="0.01" min="0" required />
            </div>
            <div class="field">
              <label class="label" for="listing_cond">Condition</label>
              <select class="select" id="listing_cond" name="cond">
                ${['new', 'like_new', 'good', 'fair', 'poor'].map((cond) => `<option value="${cond}">${cond}</option>`).join('')}
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="field">
              <label class="label" for="listing_type">Type</label>
              <select class="select" id="listing_type" name="type">
                <option value="sell">Sell</option>
                <option value="buy">Buy</option>
              </select>
            </div>
            <div class="field">
              <label class="label" for="listing_category">Category</label>
              <select class="select" id="listing_category" name="c_id" required>
                ${createCategoryOptions}
              </select>
            </div>
          </div>
          <button class="button" type="submit">Publish listing</button>
        </form>

        <form class="stack panel" id="createAlertForm">
          <h3>Create alert</h3>
          <div class="field">
            <label class="label" for="alert_category">Category</label>
            <select class="select" id="alert_category" name="c_id">
              <option value="">Any</option>
              ${createCategoryOptions}
            </select>
          </div>
          <div class="field">
            <label class="label" for="alert_price_limit">Price limit</label>
            <input class="input" id="alert_price_limit" name="price_limit" type="number" step="0.01" min="0" placeholder="Optional" />
          </div>
          <div class="field">
            <label class="label" for="alert_keyword">Keyword</label>
            <input class="input" id="alert_keyword" name="keyword" placeholder="Optional" />
          </div>
          <button class="button-secondary" type="submit">Save alert</button>
        </form>

        <form class="stack panel" id="createCategoryForm">
          <h3>Create category</h3>
          <div class="field">
            <label class="label" for="category_name">Name</label>
            <input class="input" id="category_name" name="name" required />
          </div>
          <div class="field">
            <label class="label" for="category_parent">Parent</label>
            <select class="select" id="category_parent" name="parent_id">
              ${createCategoryOptions}
            </select>
          </div>
          <button class="button-secondary" type="submit">Add category</button>
        </form>
      </div>
    </section>
  `;
}

function renderActivityPanel() {
  return `
    <section class="section" id="activity">
      <div class="section-header">
        <div>
          <p class="kicker">Activity</p>
          <h2>Notifications, alerts, and transactions</h2>
        </div>
        <button class="button-quiet" data-action="refresh-activity">Refresh all</button>
      </div>

      <div class="main-grid" style="grid-template-columns: repeat(3, minmax(0, 1fr));">
        <div class="stack panel" style="padding: 18px;">
          <div class="split-title">
            <h3>Notifications</h3>
            <span class="pill">${state.notifications.length}</span>
          </div>
          ${state.notifications.length ? renderNotifications() : '<div class="empty">No notifications yet.</div>'}
        </div>
        <div class="stack panel" style="padding: 18px;">
          <div class="split-title">
            <h3>Alerts</h3>
            <span class="pill">${state.alerts.length}</span>
          </div>
          ${state.alerts.length ? renderAlerts() : '<div class="empty">No alerts yet.</div>'}
        </div>
        <div class="stack panel" style="padding: 18px;">
          <div class="split-title">
            <h3>Transactions</h3>
            <span class="pill">${state.transactions.length}</span>
          </div>
          ${state.transactions.length ? renderTransactions() : '<div class="empty">No transactions yet.</div>'}
        </div>
      </div>
    </section>
  `;
}

function renderNotifications() {
  return `
    <div class="timeline">
      ${state.notifications
        .map(
          (notification) => `
            <article class="timeline-item">
              <div class="split-title">
                <strong>${escapeHtml(notification.listing_title || `Listing ${notification.listing_id}`)}</strong>
                <span class="pill ${notification.seen ? '' : 'warning'}">${notification.seen ? 'Seen' : 'New'}</span>
              </div>
              <div class="micro">Alert #${notification.alert_id} • Listing #${notification.listing_id}</div>
              <div class="timestamp">${formatDate(notification.created_at)}</div>
              ${notification.seen ? '' : `<button class="button-secondary" data-action="mark-seen" data-notif-id="${notification.notif_id}">Mark seen</button>`}
            </article>
          `,
        )
        .join('')}
    </div>
  `;
}

function renderAlerts() {
  return `
    <div class="timeline">
      ${state.alerts
        .map(
          (alert) => `
            <article class="timeline-item">
              <div class="split-title">
                <strong>${escapeHtml(alert.keyword || `Category ${alert.c_id || 'any'}`)}</strong>
                <span class="pill">#${alert.alert_id}</span>
              </div>
              <div class="meta-row">
                <span class="pill">${alert.c_id ? findCategoryName(alert.c_id) : 'Any category'}</span>
                <span class="pill">${alert.price_limit ? currency(alert.price_limit) : 'No price limit'}</span>
              </div>
              <div class="timestamp">${formatDate(alert.created_at)}</div>
              <button class="button-danger" data-action="delete-alert" data-alert-id="${alert.alert_id}">Delete</button>
            </article>
          `,
        )
        .join('')}
    </div>
  `;
}

function renderTransactions() {
  return `
    <div class="timeline">
      ${state.transactions
        .map(
          (txn) => `
            <article class="timeline-item">
              <div class="split-title">
                <strong>${escapeHtml(txn.listing_title || `Txn ${txn.txn_id}`)}</strong>
                <span class="pill ${txn.status === 'completed' ? 'success' : ''}">${escapeHtml(txn.status)}</span>
              </div>
              <div class="meta-row">
                <span class="pill">${currency(txn.amount)}</span>
                <span class="pill">Buyer: ${escapeHtml(txn.buyer_username || `User ${txn.buyer_id}`)}</span>
                ${txn.seller_username ? `<span class="pill">Seller: ${escapeHtml(txn.seller_username)}</span>` : ''}
              </div>
              <div class="timestamp">${formatDate(txn.txn_date)}</div>
            </article>
          `,
        )
        .join('')}
    </div>
  `;
}

function applyLocalListingSearch(listings) {
  const search = (state.filters.search || '').trim().toLowerCase();
  if (!search) return listings;
  return listings.filter((listing) => {
    const haystack = [listing.title, listing.description, listing.seller_username, listing.category_name]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(search);
  });
}

function syncSelectedControls() {
  const form = document.getElementById('filterForm');
  if (!form) return;
  const categoryField = form.querySelector('[name="c_id"]');
  if (categoryField) categoryField.value = state.filters.c_id || '';
}

function attachEvents() {
  document.querySelectorAll('[data-scroll-to]').forEach((button) => {
    button.addEventListener('click', () => {
      const target = document.getElementById(button.dataset.scrollTo);
      target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  document.querySelectorAll('[data-view]').forEach((button) => {
    button.addEventListener('click', () => {
      state.view = button.dataset.view;
      render();
    });
  });

  document.querySelectorAll('[data-action="logout"]').forEach((button) => {
    button.addEventListener('click', logout);
  });

  document.querySelectorAll('[data-action="save-api-base"]').forEach((button) => {
    button.addEventListener('click', async () => {
      const input = document.getElementById('apiBase');
      if (!input) return;
      const value = input.value.trim().replace(/\/$/, '');
      if (!value) return;
      state.apiBase = value;
      localStorage.setItem('marketdeck_api_base', value);
      pushToast('API base saved', value, 'info');
      await refreshAll();
    });
  });

  document.querySelectorAll('[data-action="refresh-categories"]').forEach((button) => {
    button.addEventListener('click', () => loadCategories());
  });

  document.querySelectorAll('[data-action="refresh-offers"]').forEach((button) => {
    button.addEventListener('click', () => refreshSelectedOffers());
  });

  document.querySelectorAll('[data-action="refresh-activity"]').forEach((button) => {
    button.addEventListener('click', () => refreshActivity());
  });

  document.querySelectorAll('[data-action="select-listing"]').forEach((button) => {
    button.addEventListener('click', () => selectListing(Number(button.dataset.listingId)));
  });

  document.querySelectorAll('[data-listing-id]').forEach((card) => {
    card.addEventListener('click', (event) => {
      const listingId = Number(card.dataset.listingId);
      if (event.target.closest('[data-action="select-listing"]')) return;
      selectListing(listingId);
    });
  });

  const filterForm = document.getElementById('filterForm');
  filterForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const values = updateStateFromForm(filterForm);
    state.filters = {
      type: values.type || '',
      c_id: values.c_id || '',
      price_min: values.price_min || '',
      price_max: values.price_max || '',
      status: values.status || '',
      search: values.search || '',
    };
    await loadListings();
  });

  document.querySelectorAll('[data-action="reset-filters"]').forEach((button) => {
    button.addEventListener('click', async () => {
      state.filters = { type: '', c_id: '', price_min: '', price_max: '', status: 'active', search: '' };
      await loadListings();
    });
  });

  const loginForm = document.getElementById('loginForm');
  loginForm?.addEventListener('submit', handleLogin);

  const registerForm = document.getElementById('registerForm');
  registerForm?.addEventListener('submit', handleRegister);

  const createListingForm = document.getElementById('createListingForm');
  createListingForm?.addEventListener('submit', handleCreateListing);

  const createAlertForm = document.getElementById('createAlertForm');
  createAlertForm?.addEventListener('submit', handleCreateAlert);

  const createCategoryForm = document.getElementById('createCategoryForm');
  createCategoryForm?.addEventListener('submit', handleCreateCategory);

  const offerForm = document.getElementById('offerForm');
  offerForm?.addEventListener('submit', handleCreateOffer);

  const listingEditForm = document.getElementById('listingEditForm');
  listingEditForm?.addEventListener('submit', handleEditListing);

  document.querySelectorAll('[data-action="accept-offer"]').forEach((button) => {
    button.addEventListener('click', () => handleOfferAction('accept', Number(button.dataset.offerId)));
  });

  document.querySelectorAll('[data-action="reject-offer"]').forEach((button) => {
    button.addEventListener('click', () => handleOfferAction('reject', Number(button.dataset.offerId)));
  });

  document.querySelectorAll('[data-action="delete-listing"]').forEach((button) => {
    button.addEventListener('click', () => handleDeleteListing(Number(button.dataset.listingId)));
  });

  document.querySelectorAll('[data-action="mark-seen"]').forEach((button) => {
    button.addEventListener('click', () => handleMarkSeen(Number(button.dataset.notifId)));
  });

  document.querySelectorAll('[data-action="delete-alert"]').forEach((button) => {
    button.addEventListener('click', () => handleDeleteAlert(Number(button.dataset.alertId)));
  });
}

async function handleLogin(event) {
  event.preventDefault();
  const data = updateStateFromForm(event.currentTarget);
  try {
    setBusy(true);
    const result = await api('/auth/login', {
      auth: false,
      method: 'POST',
      body: { email: data.email, password: data.password },
    });
    state.token = result.access_token;
    localStorage.setItem('marketdeck_token', state.token);
    pushToast('Signed in', 'Your session is active.', 'success');
    state.view = 'activity';
    await refreshAll();
  } catch (error) {
    pushToast('Login failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const data = updateStateFromForm(event.currentTarget);
  try {
    setBusy(true);
    await api('/auth/register', {
      auth: false,
      method: 'POST',
      body: {
        username: data.username,
        email: data.email,
        password: data.password,
        phone: data.phone || null,
      },
    });
    pushToast('Account created', 'You can sign in now.', 'success');
    event.currentTarget.reset();
  } catch (error) {
    pushToast('Registration failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleCreateListing(event) {
  event.preventDefault();
  const data = updateStateFromForm(event.currentTarget);
  try {
    setBusy(true);
    await api('/listings/', {
      method: 'POST',
      body: {
        c_id: Number(data.c_id),
        title: data.title,
        description: data.description || null,
        price: Number(data.price),
        cond: data.cond,
        type: data.type,
      },
    });
    pushToast('Listing published', 'New listing created successfully.', 'success');
    event.currentTarget.reset();
    await refreshAll();
  } catch (error) {
    pushToast('Listing failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleEditListing(event) {
  event.preventDefault();
  const data = updateStateFromForm(event.currentTarget);
  const updates = {
    title: data.title || null,
    description: data.description || null,
    price: data.price ? Number(data.price) : null,
    cond: data.cond || null,
    status: data.status || null,
  };

  try {
    setBusy(true);
    await api(`/listings/${data.listing_id}`, {
      method: 'PUT',
      body: updates,
    });
    pushToast('Listing updated', 'Your changes were saved.', 'success');
    await refreshAll();
  } catch (error) {
    pushToast('Update failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleDeleteListing(listingId) {
  if (!confirm('Close this listing?')) return;
  try {
    setBusy(true);
    await api(`/listings/${listingId}`, { method: 'DELETE' });
    pushToast('Listing closed', 'The listing is now closed.', 'success');
    await refreshAll();
  } catch (error) {
    pushToast('Delete failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleCreateAlert(event) {
  event.preventDefault();
  const data = updateStateFromForm(event.currentTarget);
  const body = {
    c_id: data.c_id ? Number(data.c_id) : null,
    price_limit: data.price_limit ? Number(data.price_limit) : null,
    keyword: data.keyword || null,
  };
  try {
    setBusy(true);
    await api('/alerts/', { method: 'POST', body });
    pushToast('Alert created', 'Your alert is now active.', 'success');
    event.currentTarget.reset();
    await refreshActivity();
  } catch (error) {
    pushToast('Alert failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleCreateCategory(event) {
  event.preventDefault();
  const data = updateStateFromForm(event.currentTarget);
  try {
    setBusy(true);
    await api('/categories/', {
      method: 'POST',
      body: {
        name: data.name,
        parent_id: data.parent_id ? Number(data.parent_id) : null,
      },
    });
    pushToast('Category created', 'Tree refreshed.', 'success');
    event.currentTarget.reset();
    await refreshAll();
  } catch (error) {
    pushToast('Category failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleCreateOffer(event) {
  event.preventDefault();
  const data = updateStateFromForm(event.currentTarget);
  try {
    setBusy(true);
    await api('/offers/', {
      method: 'POST',
      body: {
        listing_id: Number(data.listing_id),
        offered_price: Number(data.offered_price),
        message: data.message || null,
      },
    });
    pushToast('Offer sent', 'Seller can review it from the listing detail panel.', 'success');
    event.currentTarget.reset();
    await loadListings();
    await selectListing(Number(data.listing_id));
  } catch (error) {
    pushToast('Offer failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleOfferAction(action, offerId) {
  try {
    setBusy(true);
    await api(`/offers/${offerId}/${action}`, { method: 'POST' });
    pushToast(`Offer ${action}ed`, `Offer ${offerId} has been ${action}ed.`, 'success');
    await refreshSelectedOffers();
    await refreshActivity();
  } catch (error) {
    pushToast(`Offer ${action} failed`, error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleMarkSeen(notifId) {
  try {
    setBusy(true);
    await api(`/notifications/${notifId}/seen`, { method: 'PATCH' });
    pushToast('Notification updated', 'Marked as seen.', 'success');
    await refreshActivity();
  } catch (error) {
    pushToast('Update failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function handleDeleteAlert(alertId) {
  if (!confirm('Delete this alert?')) return;
  try {
    setBusy(true);
    await api(`/alerts/${alertId}`, { method: 'DELETE' });
    pushToast('Alert deleted', 'The alert is no longer active.', 'success');
    await refreshActivity();
  } catch (error) {
    pushToast('Delete failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function refreshSelectedOffers() {
  if (!state.selectedListing || !state.token) return;
  if (Number(state.selectedListing.u_id) !== Number(state.me?.u_id)) return;
  try {
    const offers = await api(`/offers/listing/${state.selectedListing.listing_id}`);
    state.selectedOffers = offers || [];
    render();
  } catch (error) {
    pushToast('Offers unavailable', error.message, 'error');
  }
}

async function selectListing(listingId) {
  try {
    setBusy(true);
    const listing = await api(`/listings/${listingId}`, { auth: false });
    state.selectedListing = listing;
    state.selectedOffers = [];
    render();
    await refreshSelectedOffers();
  } catch (error) {
    pushToast('Selection failed', error.message, 'error');
  } finally {
    setBusy(false);
  }
}

async function loadCategories() {
  try {
    const data = await api('/categories/tree', { auth: false });
    state.categories = data || [];
    render();
  } catch (error) {
    pushToast('Categories unavailable', error.message, 'error');
  }
}

async function loadListings() {
  try {
    const params = new URLSearchParams();
    if (state.filters.type) params.set('type', state.filters.type);
    if (state.filters.c_id) params.set('c_id', state.filters.c_id);
    if (state.filters.price_min) params.set('price_min', state.filters.price_min);
    if (state.filters.price_max) params.set('price_max', state.filters.price_max);
    if (state.filters.status !== '') params.set('status', state.filters.status || '');

    const data = await api(`/listings/${params.toString() ? `?${params.toString()}` : ''}`, { auth: false });
    state.listings = data || [];

    if (!state.selectedListing && state.listings.length) {
      state.selectedListing = state.listings[0];
    } else if (state.selectedListing) {
      const refreshed = state.listings.find((listing) => Number(listing.listing_id) === Number(state.selectedListing.listing_id));
      if (refreshed) {
        state.selectedListing = refreshed;
      }
    }

    render();
    if (state.selectedListing) {
      await refreshSelectedOffers();
    }
  } catch (error) {
    state.error = error.message;
    pushToast('Listings unavailable', error.message, 'error');
  }
}

async function loadMe() {
  if (!state.token) {
    state.me = null;
    return;
  }
  try {
    const data = await api('/users/me');
    state.me = data;
  } catch (error) {
    pushToast('Session expired', error.message, 'error');
    logout();
  }
}

async function loadNotifications() {
  if (!state.token) {
    state.notifications = [];
    return;
  }
  try {
    const data = await api('/notifications/me');
    state.notifications = data || [];
  } catch (error) {
    pushToast('Notifications unavailable', error.message, 'error');
  }
}

async function loadAlerts() {
  if (!state.token) {
    state.alerts = [];
    return;
  }
  try {
    const data = await api('/alerts/me');
    state.alerts = data || [];
  } catch (error) {
    pushToast('Alerts unavailable', error.message, 'error');
  }
}

async function loadTransactions() {
  if (!state.token) {
    state.transactions = [];
    return;
  }
  try {
    const data = await api('/transactions/me');
    state.transactions = data || [];
  } catch (error) {
    pushToast('Transactions unavailable', error.message, 'error');
  }
}

async function refreshActivity() {
  await Promise.all([loadNotifications(), loadAlerts(), loadTransactions()]);
  render();
}

async function refreshAll() {
  state.loading = true;
  render();
  await Promise.all([loadCategories(), loadListings(), loadMe(), loadNotifications(), loadAlerts(), loadTransactions()]);
  state.loading = false;
  render();
}

function logout() {
  state.token = '';
  state.me = null;
  state.notifications = [];
  state.alerts = [];
  state.transactions = [];
  state.selectedOffers = [];
  localStorage.removeItem('marketdeck_token');
  state.view = 'auth';
  pushToast('Signed out', 'Your session was cleared.', 'info');
  render();
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function bindGlobalActions() {
  document.addEventListener('click', async (event) => {
    const offerActionButton = event.target.closest('[data-action="accept-offer"], [data-action="reject-offer"]');
    if (offerActionButton) {
      const action = offerActionButton.dataset.action === 'accept-offer' ? 'accept' : 'reject';
      const offerId = Number(offerActionButton.dataset.offerId);
      await handleOfferAction(action, offerId);
      return;
    }

    if (event.target.closest('[data-action="delete-listing"]') && !event.target.closest('#listingEditForm')) {
      await handleDeleteListing(state.selectedListing?.listing_id);
    }
  });
}

function syncSelectedControls() {
  const form = document.getElementById('filterForm');
  if (!form) return;
  const categoryField = form.querySelector('[name="c_id"]');
  if (categoryField) categoryField.value = state.filters.c_id || '';
}

function render() {
  renderAppShell();
}

bindGlobalActions();
refreshAll().catch((error) => {
  state.loading = false;
  state.error = error.message;
  pushToast('Startup error', error.message, 'error');
  render();
});