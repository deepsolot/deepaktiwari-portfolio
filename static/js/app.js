let currentLeads = [];
let activeLeadId = null;
let currentLanguage = 'followup';
let filterTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
  loadLeads();
});

function debounceFilter() {
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(() => {
    loadLeads();
  }, 250);
}

// Fetch leads with active filters
async function loadLeads() {
  const category = document.getElementById('filter-category').value;
  const locality = document.getElementById('filter-locality').value;
  const status = document.getElementById('filter-status').value;
  const noWebOnly = document.getElementById('filter-no-web').checked;
  const search = document.getElementById('filter-search').value.trim();

  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (locality) params.append('locality', locality);
  if (status) params.append('status', status);
  if (noWebOnly) params.append('no_website', 'true');
  if (search) params.append('search', search);

  try {
    const res = await fetch(`/api/leads?${params.toString()}`);
    const data = await res.json();
    if (data.status === 'success') {
      currentLeads = data.leads;
      updateStats(data.stats);
      renderLeads(currentLeads);
    }
  } catch (err) {
    console.error('Error fetching leads:', err);
    showToast('Failed to load leads from server.', 'error');
  }
}

// Update Header Statistics
function updateStats(stats) {
  if (!stats) return;
  document.getElementById('stat-total').textContent = stats.total_leads || 0;
  document.getElementById('stat-no-web').textContent = stats.no_website_leads || 0;
  document.getElementById('stat-contacted').textContent = stats.contacted_leads || 0;
  document.getElementById('stat-converted').textContent = stats.converted_leads || 0;
}

// Render Lead Cards
function renderLeads(leads) {
  const container = document.getElementById('leads-container');
  const countText = document.getElementById('leads-count-text');
  countText.textContent = `Showing ${leads.length} verified Varanasi businesses`;

  if (!leads || leads.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: var(--bg-card); border-radius: var(--radius-md); border: 1px dashed var(--border-color);">
        <p style="font-size: 2rem; margin-bottom: 12px;">🔍</p>
        <h3 style="color: #fff; margin-bottom: 8px;">No Businesses Found Matching Filter</h3>
        <p style="color: var(--text-secondary); max-width: 450px; margin: 0 auto 16px;">Try adjusting your search criteria, untick "Only No-Website", or use the live scanner above to discover new leads.</p>
        <button class="btn btn-secondary" onclick="resetFilters()">Reset All Filters</button>
      </div>
    `;
    return;
  }

  container.innerHTML = leads.map(lead => {
    const tagClass = getTagClass(lead.category);
    const isNoWeb = !lead.has_website;
    const statusClass = `status-${lead.status || 'new'}`;
    const cleanPhone = (lead.phone || '').replace(/\s+/g, '');

    return `
      <div class="lead-card" id="card-${lead.id}">
        <div>
          <div class="lead-top">
            <div class="lead-title-area">
              <h3>${escapeHtml(lead.name)}</h3>
              <span class="badge-tag ${tagClass}">${escapeHtml(lead.category)}</span>
            </div>
            <span class="status-pill ${statusClass}">${formatStatus(lead.status)}</span>
          </div>

          <div class="lead-web-status">
            ${isNoWeb 
              ? `<span class="badge-noweb">🚫 NO WEBSITE (🔥 High Priority Target)</span>`
              : `<span class="badge-hasweb">🌐 Has Website: <a href="${lead.website_url}" target="_blank" style="color:inherit; text-decoration:underline;">Visit</a></span>`
            }
          </div>

          <div class="lead-details">
            <div class="lead-detail-row">
              <span>📍</span>
              <span><strong>${escapeHtml(lead.locality)}</strong> • ${escapeHtml(lead.address || 'Varanasi')}</span>
            </div>
            <div class="lead-detail-row">
              <span>📱</span>
              <span><strong>Phone:</strong> ${escapeHtml(lead.phone || 'N/A')}</span>
              ${lead.phone ? `<button class="btn-copy-sm" onclick="copyText('${cleanPhone}', 'Phone number copied!')">📋</button>` : ''}
            </div>
            <div class="lead-detail-row">
              <span>⭐</span>
              <span><strong>${lead.rating || 4.2} / 5.0</strong> (${lead.reviews_count || 30} reviews on Google)</span>
            </div>
            <div class="pain-point-quote">
              🎯 <strong>Opportunity:</strong> ${escapeHtml(lead.pain_point || 'Needs a modern web presence to capture direct tourist sales.')}
            </div>
          </div>
        </div>

        <div class="lead-footer">
          <select class="custom-select-sm" onchange="quickUpdateStatus('${lead.id}', this.value)">
            <option value="new" ${lead.status === 'new' ? 'selected' : ''}>New</option>
            <option value="messaged" ${lead.status === 'messaged' ? 'selected' : ''}>Messaged</option>
            <option value="follow_up" ${lead.status === 'follow_up' ? 'selected' : ''}>Follow Up</option>
            <option value="converted" ${lead.status === 'converted' ? 'selected' : ''}>Won 🎉</option>
          </select>

          <button class="btn btn-whatsapp" onclick="openPitchModal('${lead.id}')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.664-.699c.969.586 1.761.88 2.796.88 3.179 0 5.767-2.587 5.767-5.766.001-3.187-2.575-5.766-5.767-5.766zm9.969 5.766c0 5.518-4.482 10-10 10-1.745 0-3.385-.453-4.819-1.246l-5.181 1.308 1.332-4.862c-.911-1.503-1.432-3.268-1.432-5.2 0-5.518 4.482-10 10-10 5.518 0 10 4.482 10 10z"/></svg>
            Pitch on WhatsApp
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function resetFilters() {
  document.getElementById('filter-category').value = '';
  document.getElementById('filter-locality').value = '';
  document.getElementById('filter-status').value = '';
  document.getElementById('filter-search').value = '';
  document.getElementById('filter-no-web').checked = false;
  loadLeads();
}

function getTagClass(category) {
  if (!category) return 'tag-general';
  if (category.includes('Hotel')) return 'tag-hotel';
  if (category.includes('Restaurant')) return 'tag-restaurant';
  if (category.includes('Silk') || category.includes('Saree')) return 'tag-silk';
  if (category.includes('Tour') || category.includes('Travel')) return 'tag-tour';
  if (category.includes('Health') || category.includes('Clinic')) return 'tag-health';
  return 'tag-general';
}

function formatStatus(status) {
  switch (status) {
    case 'messaged': return '💬 Messaged';
    case 'follow_up': return '⏰ Follow Up';
    case 'converted': return '🏆 Converted';
    default: return '🆕 New';
  }
}

// Quick inline status update
async function quickUpdateStatus(leadId, newStatus) {
  try {
    const res = await fetch('/api/lead/update_status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: leadId, status: newStatus })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(`Status updated to ${newStatus}`, 'success');
      loadLeads();
    }
  } catch (err) {
    console.error('Update error:', err);
    showToast('Failed to update status', 'error');
  }
}

// Live Scanner
async function triggerScanner() {
  const category = document.getElementById('scan-category').value;
  const locality = document.getElementById('scan-locality').value;
  const btn = document.getElementById('btn-scan');
  const btnText = document.getElementById('scan-btn-text');

  btn.disabled = true;
  btnText.innerHTML = `Scanning <strong>${locality}</strong> for <em>${category}</em>...`;

  try {
    const res = await fetch('/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, locality, max_results: 8 })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(`Scan complete! Found ${data.new_leads_found} new businesses in ${locality}.`, 'success');
      loadLeads();
    }
  } catch (err) {
    console.error('Scan error:', err);
    showToast('Scanner encountered an issue, check network.', 'error');
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Discover New Leads in Varanasi';
  }
}

// Open Pitch Modal
async function openPitchModal(leadId) {
  activeLeadId = leadId;
  const lead = currentLeads.find(l => l.id === leadId);
  if (!lead) return;

  document.getElementById('modal-biz-name').textContent = lead.name;
  document.getElementById('modal-biz-meta').textContent = `${lead.category} • ${lead.locality}`;
  document.getElementById('modal-phone-display').textContent = lead.phone || 'No Phone';
  document.getElementById('modal-pain-point').textContent = lead.pain_point || 'No specific pain point recorded.';
  document.getElementById('modal-status-select').value = lead.status || 'messaged';

  await fetchPitchText();
  document.getElementById('pitch-modal').classList.add('active');
}

function closePitchModal() {
  document.getElementById('pitch-modal').classList.remove('active');
  activeLeadId = null;
}

// Language / Template switch inside pitch modal
async function switchLanguage(lang) {
  currentLanguage = lang;
  document.querySelectorAll('.lang-pill').forEach(btn => {
    const onclickStr = btn.getAttribute('onclick') || '';
    btn.classList.toggle('active', onclickStr.includes(`'${lang}'`));
  });
  await fetchPitchText();
}

async function fetchPitchText() {
  if (!activeLeadId) return;
  try {
    const res = await fetch('/api/pitch/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_id: activeLeadId, language: currentLanguage })
    });
    const data = await res.json();
    if (data.status === 'success') {
      document.getElementById('modal-pitch-text').value = data.message;
    }
  } catch (err) {
    console.error('Error generating pitch:', err);
  }
}

// Launch WhatsApp
async function launchWhatsApp() {
  if (!activeLeadId) return;
  const lead = currentLeads.find(l => l.id === activeLeadId);
  if (!lead || !lead.phone) {
    showToast('This business does not have a valid phone number.', 'error');
    return;
  }

  const customMessage = document.getElementById('modal-pitch-text').value;
  const cleanPhone = lead.phone.replace(/\D/g, '');
  const finalPhone = cleanPhone.length === 10 ? `91${cleanPhone}` : cleanPhone;

  const encodedMsg = encodeURIComponent(customMessage);
  const waUrl = `https://web.whatsapp.com/send?phone=${finalPhone}&text=${encodedMsg}`;

  // Update lead status to messaged
  const newStatus = document.getElementById('modal-status-select').value || 'messaged';
  await quickUpdateStatus(activeLeadId, newStatus);

  // Open WhatsApp in new tab
  window.open(waUrl, '_blank');
  closePitchModal();
  showToast(`WhatsApp opened for ${lead.name}! Status updated to "${newStatus}".`, 'success');
}

function copyModalPitch() {
  const text = document.getElementById('modal-pitch-text').value;
  copyText(text, 'Pitch message copied to clipboard!');
}

function copyText(text, message) {
  navigator.clipboard.writeText(text).then(() => {
    showToast(message || 'Copied to clipboard!', 'success');
  }).catch(() => {
    showToast('Failed to copy', 'error');
  });
}

// Add Lead Modal handlers
function openAddLeadModal() {
  document.getElementById('add-lead-modal').classList.add('active');
}

function closeAddLeadModal() {
  document.getElementById('add-lead-modal').classList.remove('active');
  document.getElementById('add-lead-form').reset();
}

async function submitNewLead(e) {
  e.preventDefault();
  const name = document.getElementById('add-name').value.trim();
  const phone = document.getElementById('add-phone').value.trim();
  const category = document.getElementById('add-category').value;
  const locality = document.getElementById('add-locality').value;
  const address = document.getElementById('add-address').value.trim();
  const has_web = document.querySelector('input[name="has_web"]:checked').value === 'true';
  const notes = document.getElementById('add-notes').value.trim();

  try {
    const res = await fetch('/api/lead/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name, phone, category, locality, address,
        has_website: has_web,
        notes: notes || 'Manually added lead'
      })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(`Added "${name}" to Varanasi leads!`, 'success');
      closeAddLeadModal();
      loadLeads();
    }
  } catch (err) {
    console.error('Error adding lead:', err);
    showToast('Failed to add lead.', 'error');
  }
}

// Toast notification
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.style.borderLeftColor = type === 'success' ? 'var(--accent-whatsapp)' : (type === 'error' ? 'var(--accent-danger)' : 'var(--accent-blue)');
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}
