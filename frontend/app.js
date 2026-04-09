const DEFAULT_API_BASE = 'http://127.0.0.1:8000';
const TOKEN_KEY = 'marketdeck_token';

const state = {
  apiBase: DEFAULT_API_BASE,
  token: localStorage.getItem(TOKEN_KEY) || '',
  me: null,
  categories: [],
  listings: [],
  alerts: [],
  notifications: [],
  transactions: [],
  selectedListing: null,
  selectedSeller: null,
  selectedOffers: [],
  activeTab: 'browse',
  authView: 'login',
  loading: true,
  busy: false,
  error: '',
  filters: {
    search: '',
    type: '',
    c_id: '',
    price_min: '',
    price_max: '',
    status: 'active',
  },
  listingForm: {
    c_id: '',
    title: '',
    description: '',
    price: '',
    cond: 'good',
    type: 'sell',
  },
  toasts: [],
};

const el = document.getElementById('app');

function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  return String(value).replace(/[&<>"']/g, (character) => {
    const replacements = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return replacements[character] || character;
  });
}

function formatMoney(value) {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(Number.isFinite(amount) ? amount : 0);
}

function formatDate(value) {
  if (!value) return 'n/a';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString([], {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatListingDate(value, listingId) {
  if (!value) return 'n/a';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  // Keep DB values unchanged but stagger the displayed timestamps so
  // seeded/demo listings do not all look identical on the browse page.
  const numericId = Number(listingId) || 0;
  const offsetDays = numericId > 0 ? Math.floor((numericId - 1) / 2) : 0;
  const offsetHours = numericId > 0 ? ((numericId - 1) * 5) % 24 : 0;
  const offsetMinutes = numericId > 0 ? ((numericId - 1) * 37) % 60 : 0;
  date.setDate(date.getDate() - offsetDays);
  date.setHours(date.getHours() - offsetHours);
  date.setMinutes(date.getMinutes() - offsetMinutes);

  return formatDate(date);
}

function timeAgo(value) {
  if (!value) return 'recently';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'recently';
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 2592000) return `${Math.floor(seconds / 86400)}d ago`;
  return `${Math.floor(seconds / 2592000)}mo ago`;
}

function flattenCategories(nodes, depth = 0, output = []) {
  for (const node of nodes || []) {
    output.push({ ...node, depth });
    if (node.children?.length) flattenCategories(node.children, depth + 1, output);
  }
  return output;
}

function findCategoryName(categoryId) {
  const flat = flattenCategories(state.categories);
  return flat.find((category) => String(category.c_id) === String(categoryId))?.name || `Category ${categoryId}`;
}

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
  const { auth = true, method = 'GET', headers = {}, body } = options;
  const requestHeaders = { Accept: 'application/json', ...headers };

  if (body !== undefined) requestHeaders['Content-Type'] = 'application/json';
  if (auth && state.token) requestHeaders.Authorization = `Bearer ${state.token}`;

  const response = await fetch(`${state.apiBase}${path}`, {
    method,
    headers: requestHeaders,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const text = await response.text();
  let payload = null;

  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
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

function persistToken(token) {
  state.token = token;
  localStorage.setItem(TOKEN_KEY, token);
}

function clearSession() {
  state.token = '';
  state.me = null;
  state.selectedListing = null;
  state.selectedSeller = null;
  state.selectedOffers = [];
  state.activeTab = 'browse';
  localStorage.removeItem(TOKEN_KEY);
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

function getFilteredListings() {
  const search = state.filters.search.trim().toLowerCase();
  return state.listings.filter((listing) => {
    if (!search) return true;
    const haystack = [
      listing.title,
      listing.description,
      listing.seller_username,
      listing.category_name,
      listing.type,
      listing.status,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(search);
  });
}

function listingStatusLabel(status) {
  const lower = String(status || '').toLowerCase();
  if (lower === 'active') return 'active';
  if (lower === 'sold') return 'sold';
  if (lower === 'closed' || lower === 'fulfilled') return 'closed';
  return lower || 'listed';
}

function statusClass(status) {
  const lower = String(status || '').toLowerCase();
  if (lower === 'active') return 'success';
  if (lower === 'sold' || lower === 'closed' || lower === 'fulfilled') return 'warning';
  return 'soft';
}

function offerStatusClass(status) {
  const lower = String(status || '').toLowerCase();
  if (lower === 'accepted') return 'success';
  if (lower === 'rejected') return 'danger';
  return 'soft';
}

function listingCard(listing) {
  return `
    <article class="listing-card">
      <div class="listing-card__top">
        <div>
          <span class="eyebrow">${escapeHtml(listing.type)}</span>
          <h3>${escapeHtml(listing.title)}</h3>
        </div>
        <span class="pill ${statusClass(listing.status)}">${escapeHtml(listingStatusLabel(listing.status))}</span>
      </div>
      <p class="listing-card__description">${escapeHtml(listing.description || 'No description provided.')}</p>
      <div class="listing-card__meta">
        <span class="listing-card__category">${escapeHtml(listing.category_name || findCategoryName(listing.c_id))}</span>
        <span class="listing-card__seller">Seller: ${escapeHtml(listing.seller_username || 'Unknown seller')}</span>
      </div>
      <div class="listing-card__footer">
        <strong>${formatMoney(listing.price)}</strong>
        <span>${listing.cond ? escapeHtml(listing.cond.replaceAll('_', ' ')) : 'condition not listed'}</span>
      </div>
      <div class="listing-card__actions">
        <span class="listing-card__date">${formatListingDate(listing.created_at, listing.listing_id)}</span>
        <button class="button-secondary" data-action="open-listing" data-id="${listing.listing_id}" type="button">Click to read more</button>
      </div>
    </article>
  `;
}

function renderNotificationList(limit = 4) {
  if (!state.notifications.length) return '<p class="empty-copy">No notifications yet.</p>';
  return state.notifications
    .slice(0, limit)
    .map(
      (notification) => `
      <article class="mini-row ${notification.seen ? '' : 'unread'}">
        <div>
          <strong>${escapeHtml(notification.event_type || 'alert')}</strong>
          <p>${escapeHtml(notification.message || notification.listing_title || 'Notification')}</p>
        </div>
        <div class="mini-row__meta">
          <span>${timeAgo(notification.created_at)}</span>
          ${notification.seen ? '' : `<button class="link-button" data-action="mark-seen" data-id="${notification.notif_id}">Mark seen</button>`}
          <button class="link-button" data-action="delete-notification" data-id="${notification.notif_id}">Delete</button>
        </div>
      </article>
    `,
    )
    .join('');
}

function renderTransactionsList(limit = 4) {
  if (!state.transactions.length) return '<p class="empty-copy">No transactions yet.</p>';
  return state.transactions
    .slice(0, limit)
    .map(
      (txn) => `
      <article class="mini-row">
        <div>
          <strong>${escapeHtml(txn.listing_title || `Transaction #${txn.txn_id}`)}</strong>
          <p>${escapeHtml(txn.buyer_username || 'Buyer')} · ${escapeHtml(txn.status)}</p>
        </div>
        <div class="mini-row__meta">
          <span>${formatMoney(txn.amount)}</span>
          <span>${formatDate(txn.txn_date)}</span>
        </div>
      </article>
    `,
    )
    .join('');
}

function renderAlertsList() {
  if (!state.alerts.length) {
    return '<p class="empty-copy">No private alerts yet. Create one to get notified when matching listings appear.</p>';
  }

  return state.alerts
    .map(
      (alert) => `
      <article class="mini-row alert-row">
        <div>
          <strong>${escapeHtml(alert.keyword || 'General alert')}</strong>
          <p>
            ${escapeHtml(alert.c_id ? findCategoryName(alert.c_id) : 'All categories')}
            ${alert.price_limit ? ` · up to ${formatMoney(alert.price_limit)}` : ''}
          </p>
        </div>
        <div class="mini-row__meta alert-row__meta">
          <span>${formatDate(alert.created_at)}</span>
          <button class="button-secondary" data-action="delete-alert" data-id="${alert.alert_id}" type="button">Delete</button>
        </div>
      </article>
    `,
    )
    .join('');
}

function renderListingDetails() {
  const listing = state.selectedListing;
  if (!listing) {
    return `
      <div class="detail-empty">
        <h3>Select a listing</h3>
        <p>Open any listing to view full details, seller info, and offers here.</p>
      </div>
    `;
  }

  const isOwner = state.me && Number(state.me.u_id) === Number(listing.u_id);
  const offers = isOwner ? state.selectedOffers : [];
  const seller = state.selectedSeller;

  return `
    <div class="detail-panel__header">
      <div>
        <span class="eyebrow">${escapeHtml(listing.type)}</span>
        <h3>${escapeHtml(listing.title)}</h3>
      </div>
      <span class="pill ${statusClass(listing.status)}">${escapeHtml(listingStatusLabel(listing.status))}</span>
    </div>

    <div class="detail-grid">
      <div class="detail-stat">
        <span>Price</span>
        <strong>${formatMoney(listing.price)}</strong>
      </div>
      <div class="detail-stat">
        <span>Seller</span>
        <strong>${escapeHtml(listing.seller_username || 'Unknown')}</strong>
      </div>
      <div class="detail-stat">
        <span>Category</span>
        <strong>${escapeHtml(listing.category_name || findCategoryName(listing.c_id))}</strong>
      </div>
      <div class="detail-stat">
        <span>Condition</span>
        <strong>${escapeHtml(listing.cond ? listing.cond.replaceAll('_', ' ') : 'Not specified')}</strong>
      </div>
    </div>

    <p class="detail-copy">${escapeHtml(listing.description || 'No description provided by the seller.')}</p>

    <section class="subsection">
      <div class="section-header compact">
        <div>
          <p class="kicker">Contact seller</p>
          <h4>Seller information</h4>
        </div>
      </div>
      <div class="detail-grid">
        <div class="detail-stat">
          <span>Email</span>
          <strong>${escapeHtml(seller?.email || 'Not available')}</strong>
        </div>
        <div class="detail-stat">
          <span>Phone</span>
          <strong>${escapeHtml(seller?.phone || 'Not provided')}</strong>
        </div>
      </div>
      <p class="detail-copy">Use these details to contact the seller after your offer is accepted.</p>
    </section>

    <div class="detail-actions">
      ${isOwner ? `<button class="button-secondary" data-action="refresh-offers" data-id="${listing.listing_id}" type="button">Refresh offers</button>` : ''}
      ${isOwner ? `<button class="button-danger" data-action="close-listing" data-id="${listing.listing_id}" type="button">Close listing</button>` : ''}
      ${!isOwner ? `<button class="button" data-action="focus-offer" type="button">Place offer</button>` : ''}
    </div>

    ${isOwner
      ? `
      <section class="subsection">
        <div class="section-header compact">
          <div>
            <p class="kicker">Seller tools</p>
            <h4>Offers received</h4>
          </div>
        </div>
        ${offers.length
          ? offers
              .map(
                (offer) => `
          <article class="offer-card">
            <div class="offer-card__top">
              <div>
                <strong>${escapeHtml(offer.buyer_username || `Buyer #${offer.buyer_id}`)}</strong>
                <p>${formatDate(offer.created_at)}</p>
              </div>
              <span class="pill ${offerStatusClass(offer.status)}">${escapeHtml(offer.status)}</span>
            </div>
            <p>${escapeHtml(offer.message || 'No message')}</p>
            <div class="offer-card__bottom">
              <strong>${formatMoney(offer.offered_price)}</strong>
              <div class="offer-card__actions">
                ${String(offer.status).toLowerCase() === 'pending' ? `<button class="button" data-action="accept-offer" data-id="${offer.offer_id}" type="button">Accept</button>` : ''}
                ${String(offer.status).toLowerCase() === 'pending' ? `<button class="button-secondary" data-action="reject-offer" data-id="${offer.offer_id}" type="button">Reject</button>` : ''}
              </div>
            </div>
          </article>
        `,
              )
              .join('')
          : '<p class="empty-copy">No offers on this listing yet.</p>'}
      </section>
      `
      : `
      <section class="subsection" id="offer-form-anchor">
        <div class="section-header compact">
          <div>
            <p class="kicker">Buyer tools</p>
            <h4>Place an offer</h4>
          </div>
        </div>
        <form class="stack" data-form="offer">
          <input class="input" name="offered_price" type="number" min="1" step="1" placeholder="Offer amount" required />
          <textarea class="textarea" name="message" rows="4" placeholder="Add a short message"></textarea>
          <button class="button" type="submit">Send offer</button>
        </form>
      </section>
      `}
  `;
}

function renderTopbar() {
  const unreadCount = state.notifications.filter((notification) => !Number(notification.seen)).length;
  const navButton = (tabKey, label, extra = '') => `
    <button class="top-nav-link ${state.activeTab === tabKey ? 'active' : ''}" data-action="set-tab" data-tab="${tabKey}" type="button">${label}${extra}</button>
  `;
  return `
    <header class="topbar">
      <button class="brand brand-home-button" data-action="go-home-all" type="button" title="Go to all listings">
        <div class="brand-mark">NS</div>
        <div>
          <p class="brand-title">Nexus Slate</p>
        </div>
      </button>

      <form class="searchbar" data-form="search">
        <input class="search-input" name="search" value="${escapeHtml(state.filters.search)}" placeholder="Search listings, sellers, categories" />
        <button class="button-secondary" type="submit">Search</button>
      </form>

      <div class="topbar-actions">
        ${navButton('sell', 'Sell')}
        ${navButton('alerts', 'Alerts')}
        ${navButton('notifications', 'Notifications', unreadCount ? ` <span class="top-nav-count">${unreadCount}</span>` : '')}
        ${navButton('transactions', 'Transactions')}
      </div>

      <div class="user-chip">
        <button class="user-link" data-action="open-account" type="button">${escapeHtml(state.me?.username || 'Guest')}</button>
        <button class="button-secondary" data-action="logout" type="button">Logout</button>
      </div>
    </header>
  `;
}

function renderAuthPage() {
  const activeLogin = state.authView === 'login';
  const authTitle = activeLogin ? 'Welcome back' : 'Create your account';
  const authCopy = activeLogin
    ? 'Sign in to browse listings, post your own items, and manage offers securely.'
    : 'Register a new user account and start trading immediately on the marketplace.';

  return `
    <div class="auth-shell">
      <div class="auth-backdrop"></div>
      <section class="auth-intro">
        <div class="brand brand--hero">
          <div class="brand-mark">NS</div>
          <div>
            <p class="brand-title">Nexus Slate</p>
          </div>
        </div>
        <h1>Trade premium electronics, vehicles, homes, and services in one place.</h1>
        <p>Black glass surfaces, violet highlights, and a clean browsing experience built for serious buyers and sellers.</p>
        <div class="feature-stack">
          <article class="feature-card">
            <strong>Secure access</strong>
            <span>Users are stored in MySQL and authenticated with JWT.</span>
          </article>
          <article class="feature-card">
            <strong>Professional listings</strong>
            <span>Cards, filters, and detail panels are designed for a marketplace workflow.</span>
          </article>
          <article class="feature-card">
            <strong>Fast onboarding</strong>
            <span>Register a user, then sign in and continue directly to the dashboard.</span>
          </article>
        </div>
      </section>

      <section class="auth-panel">
        <div class="auth-tabs">
          <button class="auth-tab ${activeLogin ? 'active' : ''}" data-action="switch-auth" data-view="login" type="button">Login</button>
          <button class="auth-tab ${activeLogin ? '' : 'active'}" data-action="switch-auth" data-view="register" type="button">Register new user</button>
        </div>

        <div class="auth-card">
          <div class="section-header compact">
            <div>
              <p class="kicker">Account</p>
              <h2>${authTitle}</h2>
            </div>
          </div>
          <p class="auth-copy">${authCopy}</p>

          <form class="stack auth-form" data-form="auth">
            ${activeLogin ? '' : '<input class="input" name="username" placeholder="Username" required />'}
            <input class="input" name="email" type="email" placeholder="Email address" required />
            ${activeLogin ? '' : '<input class="input" name="phone" placeholder="Phone number (optional)" />'}
            <input class="input" name="password" type="password" placeholder="Password" ${activeLogin ? '' : 'minlength="6"'} required />
            <button class="button" type="submit">${activeLogin ? 'Login' : 'Create account'}</button>
          </form>
          <p class="auth-footnote">New users are inserted into the Users table before the app opens the dashboard.</p>
        </div>
      </section>
    </div>
  `;
}

function renderDashboard() {
  const filteredListings = getFilteredListings();
  const ownListings = state.listings.filter((listing) => Number(listing.u_id) === Number(state.me?.u_id));
  const tab = state.activeTab;
  const listingModeIsBuy = state.listingForm.type === 'buy';

  const accountTab = `
    <section class="panel tab-full">
      <div class="section-header compact">
        <div>
          <p class="kicker">Account</p>
          <h2>My profile</h2>
        </div>
      </div>
      <div class="detail-grid">
        <div class="detail-stat">
          <span>Username</span>
          <strong>${escapeHtml(state.me?.username || 'n/a')}</strong>
        </div>
        <div class="detail-stat">
          <span>Email</span>
          <strong>${escapeHtml(state.me?.email || 'n/a')}</strong>
        </div>
        <div class="detail-stat">
          <span>Phone</span>
          <strong>${escapeHtml(state.me?.phone || 'No phone added')}</strong>
        </div>
        <div class="detail-stat">
          <span>Member since</span>
          <strong>${formatDate(state.me?.created_at)}</strong>
        </div>
      </div>
      <section class="subsection">
        <div class="section-header compact">
          <div>
            <p class="kicker">My listings</p>
            <h4>Items I have posted</h4>
          </div>
          <span class="section-note">${ownListings.length} total</span>
        </div>
        <div class="stack stack-tight">
          ${ownListings.length
            ? ownListings
                .map(
                  (listing) => `<article class="mini-row"><div><strong>${escapeHtml(listing.title)}</strong><p>${formatMoney(listing.price)} · ${escapeHtml(listing.status)}</p></div><button class="button-secondary" data-action="open-listing" data-id="${listing.listing_id}" type="button">View</button></article>`,
                )
                .join('')
            : '<p class="empty-copy">You have not listed any items yet.</p>'}
        </div>
      </section>
    </section>
  `;

  const browseTab = `
    <div class="tab-layout tab-layout--two">
      <section class="panel">
        <div class="section-header compact">
          <div>
            <p class="kicker">Discover</p>
            <h2>Filters</h2>
          </div>
          <button class="button-quiet" data-action="reset-filters" type="button">Reset</button>
        </div>
        <form class="stack" data-form="filters">
          <select class="select" name="type">
            <option value="">All public listings</option>
            <option value="sell" ${state.filters.type === 'sell' ? 'selected' : ''}>Sell listings</option>
          </select>
          <select class="select" name="c_id">
            <option value="">All categories</option>
            ${flattenCategories(state.categories).map((category) => `<option value="${category.c_id}" ${String(state.filters.c_id) === String(category.c_id) ? 'selected' : ''}>${'— '.repeat(category.depth)}${escapeHtml(category.name)}</option>`).join('')}
          </select>
          <div class="split-fields">
            <input class="input" name="price_min" type="number" min="0" placeholder="Min price" value="${escapeHtml(state.filters.price_min)}" />
            <input class="input" name="price_max" type="number" min="0" placeholder="Max price" value="${escapeHtml(state.filters.price_max)}" />
          </div>
          <select class="select" name="status">
            <option value="active" ${state.filters.status === 'active' ? 'selected' : ''}>Active</option>
            <option value="sold" ${state.filters.status === 'sold' ? 'selected' : ''}>Sold</option>
            <option value="closed" ${state.filters.status === 'closed' ? 'selected' : ''}>Closed</option>
            <option value="">Any status</option>
          </select>
          <button class="button" type="submit">Apply filters</button>
        </form>
      </section>

      <section class="feed panel" id="listing-feed">
        <div class="section-header">
          <div>
            <p class="kicker">Browse</p>
            <h2>Featured listings</h2>
          </div>
          <span class="section-note">${filteredListings.length} matching results</span>
        </div>
        ${filteredListings.length ? `<div class="listing-grid">${filteredListings.map(listingCard).join('')}</div>` : '<div class="empty-state"><h3>No listings found</h3><p>Try a different filter or search term to discover more items.</p></div>'}

        <section class="detail subsection" id="detail-panel">
          ${renderListingDetails()}
        </section>
      </section>
    </div>
  `;

  const sellTab = `
    <div class="tab-layout tab-layout--two">
      <section class="panel" id="create-listing">
        <div class="section-header compact">
          <div>
            <p class="kicker">Sell</p>
            <h2>${listingModeIsBuy ? 'Private alert request' : 'New listing'}</h2>
          </div>
        </div>
        <p class="detail-copy">${listingModeIsBuy ? 'Buy requests stay private. We will save this as an alert and notify you when matching sell listings appear.' : 'Publish a public sell listing that buyers can browse and make offers on.'}</p>
        <form class="stack" data-form="listing">
          <input class="input" name="title" placeholder="${listingModeIsBuy ? 'What are you looking for?' : 'Listing title'}" value="${escapeHtml(state.listingForm.title)}" required />
          <select class="select" name="c_id" required>
            <option value="">Select category</option>
            ${flattenCategories(state.categories).map((category) => `<option value="${category.c_id}" ${String(state.listingForm.c_id) === String(category.c_id) ? 'selected' : ''}>${'— '.repeat(category.depth)}${escapeHtml(category.name)}</option>`).join('')}
          </select>
          <select class="select" name="type">
            <option value="sell" ${state.listingForm.type === 'sell' ? 'selected' : ''}>Sell</option>
            <option value="buy" ${state.listingForm.type === 'buy' ? 'selected' : ''}>Buy privately</option>
          </select>
          <input class="input" name="price" type="number" min="1" step="1" placeholder="${listingModeIsBuy ? 'Maximum budget' : 'Price'}" value="${escapeHtml(state.listingForm.price)}" required />
          <select class="select" name="cond" ${state.listingForm.type === 'buy' ? 'disabled' : ''}>
            <option value="new" ${state.listingForm.cond === 'new' ? 'selected' : ''}>New</option>
            <option value="like_new" ${state.listingForm.cond === 'like_new' ? 'selected' : ''}>Like new</option>
            <option value="good" ${state.listingForm.cond === 'good' ? 'selected' : ''}>Good</option>
            <option value="fair" ${state.listingForm.cond === 'fair' ? 'selected' : ''}>Fair</option>
            <option value="poor" ${state.listingForm.cond === 'poor' ? 'selected' : ''}>Poor</option>
          </select>
          <textarea class="textarea" name="description" rows="5" placeholder="${listingModeIsBuy ? 'Add details so we can match the right listings' : 'Write a concise description'}">${escapeHtml(state.listingForm.description)}</textarea>
          <button class="button" type="submit">${listingModeIsBuy ? 'Save private alert' : 'Publish listing'}</button>
        </form>
      </section>

      <section class="panel">
        <div class="section-header compact">
          <div>
            <p class="kicker">My inventory</p>
            <h2>Your active listings</h2>
          </div>
          <span class="section-note">${ownListings.length} total</span>
        </div>
        <div class="stack stack-tight">
          ${ownListings.length ? ownListings.map((listing) => `<article class="mini-row"><div><strong>${escapeHtml(listing.title)}</strong><p>${formatMoney(listing.price)} · ${escapeHtml(listing.status)}</p></div><button class="button-secondary" data-action="open-listing" data-id="${listing.listing_id}" type="button">View</button></article>`).join('') : '<p class="empty-copy">You do not have any listings yet.</p>'}
        </div>
      </section>
    </div>
  `;

  const notificationsTab = `
    <section class="panel tab-full" id="notifications-panel">
      <div class="section-header compact">
        <div>
          <p class="kicker">Activity</p>
          <h2>Notifications</h2>
        </div>
      </div>
      <div class="stack stack-tight">
        ${renderNotificationList(100)}
      </div>
    </section>
  `;

  const alertsTab = `
    <div class="tab-layout tab-layout--two">
      <section class="panel">
        <div class="section-header compact">
          <div>
            <p class="kicker">Private alerts</p>
            <h2>Track items quietly</h2>
          </div>
        </div>
        <p class="detail-copy">Register interest in a category, keyword, or max price. Only you can see these alerts, and you will get a notification when a matching listing is posted.</p>
        <form class="stack" data-form="alert">
          <select class="select" name="c_id">
            <option value="">All categories</option>
            ${flattenCategories(state.categories).map((category) => `<option value="${category.c_id}">${'— '.repeat(category.depth)}${escapeHtml(category.name)}</option>`).join('')}
          </select>
          <input class="input" name="keyword" placeholder="Keyword, e.g. iPhone or Royal Enfield" />
          <input class="input" name="price_limit" type="number" min="1" step="1" placeholder="Max price (optional)" />
          <button class="button" type="submit">Create private alert</button>
        </form>
      </section>

      <section class="panel">
        <div class="section-header compact">
          <div>
            <p class="kicker">My alerts</p>
            <h2>Saved watches</h2>
          </div>
          <span class="section-note">${state.alerts.length} total</span>
        </div>
        <div class="stack stack-tight">
          ${renderAlertsList()}
        </div>
      </section>
    </div>
  `;

  const transactionsTab = `
    <section class="panel tab-full">
      <div class="section-header compact">
        <div>
          <p class="kicker">Transactions</p>
          <h2>Deal history</h2>
        </div>
      </div>
      <div class="stack stack-tight">
        ${renderTransactionsList(100)}
      </div>
    </section>
  `;

  let tabContent = browseTab;
  if (tab === 'sell') tabContent = sellTab;
  if (tab === 'alerts') tabContent = alertsTab;
  if (tab === 'notifications') tabContent = notificationsTab;
  if (tab === 'transactions') tabContent = transactionsTab;
  if (tab === 'account') tabContent = accountTab;

  return `
    <div class="shell">
      ${renderTopbar()}

      ${tab === 'browse' ? `
      <section class="hero hero--dashboard">
        <div class="hero-grid">
          <div>
            <p class="eyebrow">Marketplace command center</p>
            <h1>Buy, sell, and negotiate with a polished trading flow.</h1>
            <p>Use the tabs to focus on one workflow at a time and avoid clutter.</p>
            <div class="hero-actions">
              <button class="button-secondary" data-action="set-tab" data-tab="sell" type="button">Post listing</button>
            </div>
          </div>
        </div>
      </section>
      ` : ''}

      <main class="dashboard-grid">
        <section class="content-area">
          ${tabContent}
        </section>
      </main>
    </div>
  `;
}

function renderToasts() {
  if (!state.toasts.length) return '';
  return `
    <div class="toast-stack">
      ${state.toasts
        .map(
          (toast) => `
        <article class="toast toast--${toast.kind}">
          <strong>${escapeHtml(toast.title)}</strong>
          <p>${escapeHtml(toast.message)}</p>
        </article>
      `,
        )
        .join('')}
    </div>
  `;
}

function renderErrorBanner() {
  if (!state.error) return '';
  return `
    <div class="error-banner">
      <strong>Connection issue</strong>
      <span>${escapeHtml(state.error)}</span>
    </div>
  `;
}

function renderLoading() {
  return `
    <div class="loading-screen">
      <div class="loading-card">
        <div class="brand brand--hero">
          <div class="brand-mark">NS</div>
          <div>
            <p class="brand-title">Nexus Slate</p>
          </div>
        </div>
        <p>Preparing your dashboard...</p>
      </div>
    </div>
  `;
}

function render() {
  if (!el) return;
  if (state.loading) {
    el.innerHTML = renderLoading();
    return;
  }
  const screen = state.me ? renderDashboard() : renderAuthPage();
  el.innerHTML = `${renderToasts()}${renderErrorBanner()}${screen}`;
}

async function loadCategories() {
  const data = await api('/categories/tree', { auth: false });
  state.categories = Array.isArray(data) ? data : [];
}

async function loadListings() {
  const params = new URLSearchParams();
  if (state.filters.type) params.set('type', state.filters.type);
  if (state.filters.c_id) params.set('c_id', state.filters.c_id);
  if (state.filters.price_min) params.set('price_min', state.filters.price_min);
  if (state.filters.price_max) params.set('price_max', state.filters.price_max);
  if (state.filters.status) params.set('status', state.filters.status);

  const query = params.toString();
  const data = await api(`/listings/${query ? `?${query}` : ''}`, { auth: false });
  state.listings = Array.isArray(data) ? data : [];

  if (!state.selectedListing && state.listings.length) {
    await selectListing(state.listings[0].listing_id, true);
  }

  if (state.selectedListing) {
    const refreshed = state.listings.find((listing) => Number(listing.listing_id) === Number(state.selectedListing.listing_id));
    if (refreshed) state.selectedListing = refreshed;
  }
}

async function loadNotifications() {
  if (!state.token) {
    state.notifications = [];
    return;
  }
  const data = await api('/notifications/me');
  state.notifications = Array.isArray(data) ? data : [];
}

async function loadAlerts() {
  if (!state.token) {
    state.alerts = [];
    return;
  }
  const data = await api('/alerts/me');
  state.alerts = Array.isArray(data) ? data : [];
}

async function loadTransactions() {
  if (!state.token) {
    state.transactions = [];
    return;
  }
  const data = await api('/transactions/me');
  state.transactions = Array.isArray(data) ? data : [];
}

async function loadCurrentUser() {
  state.me = await api('/users/me');
}

async function loadAuthedData() {
  await loadCurrentUser();
  await Promise.all([loadCategories(), loadListings(), loadAlerts(), loadNotifications(), loadTransactions()]);
  if (state.selectedListing) await selectListing(state.selectedListing.listing_id, true);
}

async function selectListing(listingId, silent = false) {
  const listing = await api(`/listings/${listingId}`, { auth: false });
  state.selectedListing = listing;
  state.selectedSeller = null;
  state.selectedOffers = [];
  state.activeTab = 'browse';

  try {
    state.selectedSeller = await api(`/users/${listing.u_id}`, { auth: false });
  } catch (error) {
    if (!silent) pushToast('Seller profile unavailable', error.message, 'warning');
  }

  if (state.me && Number(state.me.u_id) === Number(listing.u_id)) {
    try {
      const offers = await api(`/offers/listing/${listingId}`);
      state.selectedOffers = Array.isArray(offers) ? offers : [];
    } catch (error) {
      if (!silent) pushToast('Offers unavailable', error.message, 'warning');
    }
  }

  render();
}

async function handleAuthSubmit(form) {
  const payload = Object.fromEntries(new FormData(form).entries());

  if (state.authView === 'login') {
    const tokenData = await api('/auth/login', {
      auth: false,
      method: 'POST',
      body: { email: payload.email, password: payload.password },
    });
    persistToken(tokenData.access_token);
    state.error = '';
    await loadAuthedData();
    pushToast('Login successful', `Welcome back, ${state.me?.username || 'user'}.`, 'success');
    render();
    return;
  }

  await api('/auth/register', {
    auth: false,
    method: 'POST',
    body: {
      username: payload.username,
      email: payload.email,
      password: payload.password,
      phone: payload.phone || null,
    },
  });

  pushToast('Account created', 'Your user record has been saved. Signing you in now.', 'success');
  const tokenData = await api('/auth/login', {
    auth: false,
    method: 'POST',
    body: { email: payload.email, password: payload.password },
  });
  persistToken(tokenData.access_token);
  await loadAuthedData();
  render();
}

async function handleListingSubmit(form) {
  const payload = Object.fromEntries(new FormData(form).entries());

  if (payload.type === 'buy') {
    await api('/alerts/', {
      method: 'POST',
      body: {
        c_id: Number(payload.c_id),
        price_limit: Number(payload.price),
        keyword: payload.title || null,
      },
    });

    state.listingForm = {
      c_id: '',
      title: '',
      description: '',
      price: '',
      cond: 'good',
      type: 'sell',
    };

    pushToast('Private alert created', 'Your buy request is hidden from Browse and will notify you when matching sell listings appear.', 'success');
    await loadAlerts();
    await loadNotifications();
    render();
    return;
  }

  await api('/listings/', {
    method: 'POST',
    body: {
      c_id: Number(payload.c_id),
      title: payload.title,
      description: payload.description || null,
      price: Number(payload.price),
      cond: payload.type === 'sell' ? payload.cond : null,
      type: payload.type,
    },
  });

  state.listingForm = {
    c_id: '',
    title: '',
    description: '',
    price: '',
    cond: 'good',
    type: 'sell',
  };

  pushToast('Listing created', 'Your item is now visible to buyers.', 'success');
  await loadListings();
  render();
}

async function handleOfferSubmit(form) {
  if (!state.selectedListing) return;
  const payload = Object.fromEntries(new FormData(form).entries());

  await api('/offers/', {
    method: 'POST',
    body: {
      listing_id: Number(state.selectedListing.listing_id),
      offered_price: Number(payload.offered_price),
      message: payload.message || null,
    },
  });

  state.activeTab = 'browse';
  pushToast('Offer sent', 'The seller can now review your offer.', 'success');
  await selectListing(state.selectedListing.listing_id, true);
}

async function handleAlertSubmit(form) {
  const payload = Object.fromEntries(new FormData(form).entries());

  await api('/alerts/', {
    method: 'POST',
    body: {
      c_id: payload.c_id ? Number(payload.c_id) : null,
      price_limit: payload.price_limit ? Number(payload.price_limit) : null,
      keyword: payload.keyword?.trim() || null,
    },
  });

  form.reset();
  pushToast('Alert created', 'Your private alert is saved. Matching listings will notify you.', 'success');
  await loadAlerts();
  await loadNotifications();
  render();
}

async function handleFilterSubmit(form) {
  const payload = Object.fromEntries(new FormData(form).entries());
  state.filters = {
    search: state.filters.search,
    type: payload.type || '',
    c_id: payload.c_id || '',
    price_min: payload.price_min || '',
    price_max: payload.price_max || '',
    status: payload.status || '',
  };
  await loadListings();
  render();
}

function resetFilters() {
  state.filters = {
    search: '',
    type: '',
    c_id: '',
    price_min: '',
    price_max: '',
    status: 'active',
  };
  loadListings().then(render).catch((error) => {
    state.error = error.message;
    render();
  });
}

function showAllListingsHome() {
  state.activeTab = 'browse';
  state.filters = {
    search: '',
    type: '',
    c_id: '',
    price_min: '',
    price_max: '',
    status: '',
  };
  loadListings().then(render).catch((error) => {
    state.error = error.message;
    render();
  });
}

async function handleSearchSubmit(form) {
  const search = String(new FormData(form).get('search') || '').trim();
  state.filters.search = search;
  render();
}

async function runAction(action, target) {
  switch (action) {
    case 'switch-auth':
      state.authView = target.dataset.view === 'register' ? 'register' : 'login';
      render();
      break;
    case 'logout':
      clearSession();
      state.authView = 'login';
      state.error = '';
      state.alerts = [];
      state.notifications = [];
      state.transactions = [];
      state.listings = [];
      state.categories = [];
      render();
      break;
    case 'set-tab':
      state.activeTab = target.dataset.tab || 'browse';
      render();
      break;
    case 'open-account':
      state.activeTab = 'account';
      render();
      break;
    case 'open-listing':
      if (target.dataset.id) await selectListing(target.dataset.id);
      break;
    case 'refresh-offers':
      if (state.selectedListing) await selectListing(state.selectedListing.listing_id);
      break;
    case 'accept-offer':
      await api(`/offers/${target.dataset.id}/accept`, { method: 'POST' });
      pushToast('Offer accepted', 'The related transaction has been created.', 'success');
      await loadAuthedData();
      if (state.selectedListing) await selectListing(state.selectedListing.listing_id, true);
      break;
    case 'reject-offer':
      await api(`/offers/${target.dataset.id}/reject`, { method: 'POST' });
      pushToast('Offer rejected', 'The buyer has been notified.', 'info');
      await loadAuthedData();
      if (state.selectedListing) await selectListing(state.selectedListing.listing_id, true);
      break;
    case 'close-listing':
      await api(`/listings/${target.dataset.id}`, { method: 'DELETE' });
      pushToast('Listing closed', 'The item is no longer active.', 'info');
      await loadAuthedData();
      break;
    case 'mark-seen':
      await api(`/notifications/${target.dataset.id}/seen`, { method: 'PATCH' });
      await loadNotifications();
      render();
      break;
    case 'delete-notification':
      await api(`/notifications/${target.dataset.id}`, { method: 'DELETE' });
      pushToast('Notification deleted', 'The notification has been removed.', 'info');
      await loadNotifications();
      render();
      break;
    case 'delete-alert':
      await api(`/alerts/${target.dataset.id}`, { method: 'DELETE' });
      pushToast('Alert deleted', 'The private alert has been removed.', 'info');
      await loadAlerts();
      await loadNotifications();
      render();
      break;
    case 'focus-offer':
      state.activeTab = 'browse';
      render();
      document.getElementById('offer-form-anchor')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      break;
    case 'reset-filters':
      resetFilters();
      break;
    case 'go-home-all':
      showAllListingsHome();
      break;
    default:
      break;
  }
}

el.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-action]');
  if (!button) return;
  event.preventDefault();
  try {
    await runAction(button.dataset.action, button);
  } catch (error) {
    state.error = error.message;
    pushToast('Request failed', error.message, 'danger');
    render();
  }
});

el.addEventListener('submit', async (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;
  event.preventDefault();

  try {
    if (form.dataset.form === 'auth') {
      setBusy(true);
      await handleAuthSubmit(form);
      state.error = '';
      return;
    }
    if (form.dataset.form === 'listing') {
      setBusy(true);
      await handleListingSubmit(form);
      return;
    }
    if (form.dataset.form === 'offer') {
      setBusy(true);
      await handleOfferSubmit(form);
      return;
    }
    if (form.dataset.form === 'alert') {
      setBusy(true);
      await handleAlertSubmit(form);
      return;
    }
    if (form.dataset.form === 'filters') {
      await handleFilterSubmit(form);
      return;
    }
    if (form.dataset.form === 'search') {
      await handleSearchSubmit(form);
      return;
    }
  } catch (error) {
    state.error = error.message;
    pushToast('Request failed', error.message, 'danger');
    render();
  } finally {
    if (state.busy) {
      state.busy = false;
      render();
    }
  }
});

el.addEventListener('change', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement || target instanceof HTMLTextAreaElement)) return;
  const form = target.closest('form');
  if (!(form instanceof HTMLFormElement) || form.dataset.form !== 'listing') return;

  if (target.name === 'type') {
    state.listingForm.type = target.value === 'buy' ? 'buy' : 'sell';
    render();
  }
});

async function bootstrap() {
  state.loading = true;
  render();
  try {
    if (state.token) {
      await loadAuthedData();
    } else {
      await loadCategories().catch(() => {
        state.categories = [];
      });
      await loadListings().catch(() => {
        state.listings = [];
      });
    }
    state.error = '';
  } catch (error) {
    state.error = error.message;
    clearSession();
  } finally {
    state.loading = false;
    render();
  }
}

bootstrap();
