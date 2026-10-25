/**
 * CLOUD-M7 Interactive High-Performance Frontend Engine
 * Powered by Vis-Network WebGL/Canvas, Lucide Icons, and Express JSON Bridge.
 */

// Global State
let currentAnalysis = null;
let network = null;
let rawEventsData = [];

// DOM Element References
const datasetSelect = document.getElementById('dataset-select');
const btnReload = document.getElementById('btn-reload');
const navTabs = document.querySelectorAll('.nav-tab');
const tabPanes = document.querySelectorAll('.tab-pane');

// Stat Cards
const statEvents = document.getElementById('stat-events');
const statCrossFlows = document.getElementById('stat-cross-flows');
const statPathHops = document.getElementById('stat-path-hops');
const statNoisePruned = document.getElementById('stat-noise-pruned');
const statChokePoints = document.getElementById('stat-choke-points');
const statSqlLatency = document.getElementById('stat-sql-latency');

// Graph Canvas & Sidebar
const graphCanvas = document.getElementById('graph-canvas');
const nodeDetails = document.getElementById('node-details');
const timelineBody = document.getElementById('timeline-body');

// Ingestion & Normalizer
const uploadInput = document.getElementById('upload-input');
const btnUpload = document.getElementById('btn-upload');
const eventsTableBody = document.getElementById('events-table-body');

// Novelty Containers
const n1HistoryBody = document.getElementById('n1-history-body');
const n1VectorsContainer = document.getElementById('n1-vectors-container');
const n2ChokeBody = document.getElementById('n2-choke-body');
const n3BridgeBody = document.getElementById('n3-bridge-body');
const n4PoliciesContainer = document.getElementById('n4-policies-container');
const n4ScriptPreview = document.getElementById('n4-script-preview');
const btnDownloadScript = document.getElementById('btn-download-script');
const n5MitreBody = document.getElementById('n5-mitre-body');

// SQL & Hardware
const sqlInput = document.getElementById('sql-input');
const btnRunSql = document.getElementById('btn-run-sql');
const sqlThead = document.getElementById('sql-thead');
const sqlTbody = document.getElementById('sql-tbody');
const sqlPerfBadge = document.getElementById('sql-perf-badge');
const btnTriggerHardware = document.getElementById('btn-trigger-hardware');
const hardwareEventsContainer = document.getElementById('hardware-events-container');

// ============================================================================
// INITIALIZATION
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupEventListeners();
  loadAnalysis(datasetSelect.value);
});

function setupEventListeners() {
  datasetSelect.addEventListener('change', () => loadAnalysis(datasetSelect.value));
  btnReload.addEventListener('click', () => loadAnalysis(datasetSelect.value, true));
  btnUpload.addEventListener('click', handleFileUpload);
  btnRunSql.addEventListener('click', executeSql);
  sqlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') executeSql();
  });
  btnTriggerHardware.addEventListener('click', handleHardwareTrigger);
  btnDownloadScript.addEventListener('click', handleDownloadScript);
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================
function setupNavigation() {
  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-tab');

      navTabs.forEach(t => {
        t.classList.remove('tab-active');
        t.classList.add('text-gray-400');
      });
      tab.classList.add('tab-active');
      tab.classList.remove('text-gray-400');

      tabPanes.forEach(pane => pane.classList.add('hidden'));
      const activePane = document.getElementById(targetId);
      if (activePane) {
        activePane.classList.remove('hidden');
      }

      if (targetId === 'tab-graph' && network) {
        setTimeout(() => network.fit(), 50);
      }
      lucide.createIcons();
    });
  });
}

// ============================================================================
// API: LOAD DATASET ANALYSIS
// ============================================================================
async function loadAnalysis(datasetName, force = false) {
  showLoadingState();
  try {
    const url = `/api/analyze?dataset=${encodeURIComponent(datasetName)}${force ? '&force=true' : ''}`;
    const res = await fetch(url);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.message || 'Analysis failed');
    }
    const data = await res.json();
    currentAnalysis = data;
    rawEventsData = data.events_preview || [];

    populateDashboard(data);
  } catch (err) {
    console.error('Error fetching analysis:', err);
    alert('Failed to load dataset: ' + err.message);
  } finally {
    hideLoadingState();
  }
}

function showLoadingState() {
  btnReload.disabled = true;
  btnReload.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Analyzing...</span>';
  lucide.createIcons();
}

function hideLoadingState() {
  btnReload.disabled = false;
  btnReload.innerHTML = '<i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i><span>Reload</span>';
  lucide.createIcons();
}

// ============================================================================
// POPULATE ALL DASHBOARD TABS
// ============================================================================
function populateDashboard(data) {
  // 1. Stat Cards
  const summary = data.summary || {};
  statEvents.textContent = (summary.total_events || 0).toLocaleString();
  statCrossFlows.textContent = (summary.cross_tier_flows || 0).toLocaleString();
  statPathHops.textContent = (summary.path_length || 0).toLocaleString();
  statNoisePruned.textContent = `${(summary.noise_reduction_pct || 0).toFixed(1)}%`;
  
  const chokeCount = (data.novelty2_chokepoints?.choke_points || []).filter(c => c.containment_efficiency_pct >= 60 || c.is_cut_vertex).length;
  statChokePoints.textContent = chokeCount;
  statSqlLatency.textContent = `${data.parquet_storage?.query_latency_ms || 1.8} ms`;

  // 2. Render Vis-Network Graph
  renderGraph(data.graph);

  // 3. Render Reconstructed Attack Path Timeline
  renderTimeline(data.reconstructed_timeline || []);

  // 4. Render Ingestion Normalizer Events Table
  renderEventsTable(data.events_preview || []);

  // 5. Render Novelty 1: Iterative Multi-Root Discovery
  renderNovelty1(data.novelty1_iterative || {});

  // 6. Render Novelty 2: Choke Points & Articulation Vertices
  renderNovelty2(data.novelty2_chokepoints || {});

  // 7. Render Novelty 3: Causal Bridge Imputation
  renderNovelty3(data.novelty3_causal_bridge || {});

  // 8. Render Novelty 4: Active Remediation
  renderNovelty4(data.novelty4_remediation || {});

  // 9. Render Novelty 5: MITRE ATT&CK Mapping
  renderNovelty5(data.novelty5_mitre || {});

  // Refresh Lucide Icons
  lucide.createIcons();
}

// ============================================================================
// 1. VIS-NETWORK GRAPH RENDERING
// ============================================================================
function renderGraph(graphData) {
  if (!graphData || !graphData.nodes || !graphCanvas) return;

  const nodes = new vis.DataSet(graphData.nodes);
  const edges = new vis.DataSet(graphData.edges);

  const data = { nodes, edges };
  const options = {
    nodes: {
      shape: 'dot',
      font: {
        face: 'JetBrains Mono',
        size: 11,
        color: '#E5E7EB',
        strokeWidth: 2,
        strokeColor: '#111827'
      },
      borderWidth: 2,
      shadow: {
        enabled: true,
        color: 'rgba(0,0,0,0.5)',
        size: 8,
        x: 2,
        y: 2
      }
    },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 0.7 } },
      font: { face: 'JetBrains Mono', size: 9, color: '#9CA3AF', strokeWidth: 0 },
      smooth: { type: 'continuous', roundness: 0.2 },
      color: { inherit: false }
    },
    physics: {
      solver: 'forceAtlas2Based',
      forceAtlas2Based: {
        gravitationalConstant: -40,
        centralGravity: 0.015,
        springLength: 95,
        springConstant: 0.08,
        damping: 0.4
      },
      stabilization: { iterations: 100 }
    },
    interaction: {
      hover: true,
      tooltipDelay: 120,
      zoomView: true,
      dragView: true
    }
  };

  if (network) {
    network.destroy();
  }

  network = new vis.Network(graphCanvas, data, options);

  // Click on node to inspect metadata
  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const selectedId = params.nodes[0];
      const nodeObj = graphData.nodes.find(n => n.id === selectedId);
      displayNodeDetails(nodeObj, graphData);
    }
  });
}

function displayNodeDetails(node, graphData) {
  if (!node) return;

  const inEdges = graphData.edges.filter(e => e.to === node.id).length;
  const outEdges = graphData.edges.filter(e => e.from === node.id).length;

  const tierBadgeColor = node.tier === 'Edge' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                        node.tier === 'Fog' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
                        'bg-purple-500/20 text-purple-300 border-purple-500/30';

  nodeDetails.innerHTML = `
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <span class="px-2 py-0.5 text-[11px] font-semibold border rounded-full ${tierBadgeColor}">
          ${node.tier} Tier
        </span>
        ${node.is_choke ? '<span class="px-2 py-0.5 text-[11px] font-bold bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 rounded-full">★ CHOKE POINT</span>' : ''}
        ${node.is_attack ? '<span class="px-2 py-0.5 text-[11px] font-bold bg-red-500/20 text-red-300 border border-red-500/30 rounded-full">ATTACK TELEMETRY</span>' : '<span class="px-2 py-0.5 text-[11px] font-semibold bg-gray-800 text-gray-400 rounded-full">BENIGN AUDIT</span>'}
      </div>

      <div class="bg-gray-900/80 p-3 rounded-lg border border-gray-800 space-y-2">
        <div>
          <span class="text-gray-500 text-[10px] block uppercase font-mono">Canonical UUID</span>
          <span class="font-mono text-cyan-300 break-all text-[11px]">${node.id}</span>
        </div>
        <div>
          <span class="text-gray-500 text-[10px] block uppercase font-mono">Host Identifier</span>
          <span class="font-mono text-gray-200">${node.host || 'N/A'}</span>
        </div>
        <div>
          <span class="text-gray-500 text-[10px] block uppercase font-mono">Event Action</span>
          <span class="font-mono font-bold text-white">${node.action || 'Unknown'}</span>
        </div>
        <div>
          <span class="text-gray-500 text-[10px] block uppercase font-mono">Target Entity / Socket / Path</span>
          <span class="font-mono text-amber-300 break-all">${node.entity || 'N/A'}</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2 text-center">
        <div class="bg-gray-900/60 p-2 rounded-lg border border-gray-800">
          <span class="text-gray-500 text-[10px] block uppercase">Inflow Degree</span>
          <span class="text-sm font-bold text-blue-400">${inEdges}</span>
        </div>
        <div class="bg-gray-900/60 p-2 rounded-lg border border-gray-800">
          <span class="text-gray-500 text-[10px] block uppercase">Outflow Degree</span>
          <span class="text-sm font-bold text-indigo-400">${outEdges}</span>
        </div>
      </div>
    </div>
  `;
}

// ============================================================================
// RECONSTRUCTED ATTACK TIMELINE TABLE
// ============================================================================
function renderTimeline(steps) {
  if (!timelineBody) return;
  if (steps.length === 0) {
    timelineBody.innerHTML = `<tr><td colspan="7" class="py-4 text-center text-gray-500">No attack progression steps reconstructed for this dataset.</td></tr>`;
    return;
  }

  timelineBody.innerHTML = steps.map(s => {
    const tierBadge = s.tier === 'Edge' ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700/50' :
                      s.tier === 'Fog' ? 'bg-amber-900/50 text-amber-300 border border-amber-700/50' :
                      'bg-purple-900/50 text-purple-300 border border-purple-700/50';

    return `
      <tr class="hover:bg-gray-900/40 transition">
        <td class="py-2.5 px-3 font-mono font-bold text-red-400">${s.order}</td>
        <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-semibold ${tierBadge}">${s.tier}</span></td>
        <td class="py-2.5 px-3 font-mono text-gray-300">${s.host_id}</td>
        <td class="py-2.5 px-3 text-gray-400 font-mono">${s.event_type}</td>
        <td class="py-2.5 px-3 font-mono font-semibold text-white">${s.action}</td>
        <td class="py-2.5 px-3 font-mono text-amber-300 text-[11px] truncate max-w-xs">${s.entity}</td>
        <td class="py-2.5 px-3 text-gray-300">${s.description}</td>
      </tr>
    `;
  }).join('');
}

// ============================================================================
// CANONICAL EVENTS TABLE PREVIEW
// ============================================================================
function renderEventsTable(events) {
  if (!eventsTableBody) return;
  if (events.length === 0) {
    eventsTableBody.innerHTML = `<tr><td colspan="9" class="py-4 text-center text-gray-500">No events available.</td></tr>`;
    return;
  }

  eventsTableBody.innerHTML = events.map(e => `
    <tr class="hover:bg-gray-900/40 transition text-[11px]">
      <td class="py-2 px-3 font-mono text-cyan-400">${e.uuid.slice(0, 8)}...</td>
      <td class="py-2 px-3 font-mono text-gray-400">${e.timestamp}</td>
      <td class="py-2 px-3"><span class="px-1.5 py-0.5 rounded text-[10px] bg-gray-800 text-gray-300">${e.tier}</span></td>
      <td class="py-2 px-3 font-mono text-gray-300">${e.host_id}</td>
      <td class="py-2 px-3 text-gray-400">${e.event_type}</td>
      <td class="py-2 px-3 font-mono font-semibold text-white">${e.action}</td>
      <td class="py-2 px-3 font-mono text-amber-300 truncate max-w-xs">${e.entity}</td>
      <td class="py-2 px-3">
        ${e.is_attack ? '<span class="px-1.5 py-0.5 rounded text-[10px] bg-red-900/60 text-red-300 font-semibold border border-red-700/50">ATTACK</span>' : '<span class="px-1.5 py-0.5 rounded text-[10px] bg-gray-800 text-gray-400">BENIGN</span>'}
      </td>
      <td class="py-2 px-3 font-mono text-[10px] text-gray-500">${e.tamper_hash}</td>
    </tr>
  `).join('');
}

// ============================================================================
// NOVELTY 1: ITERATIVE DISCOVERY
// ============================================================================
function renderNovelty1(n1) {
  if (!n1HistoryBody || !n1VectorsContainer) return;

  const history = n1.history || [];
  n1HistoryBody.innerHTML = history.map(h => `
    <tr class="hover:bg-gray-900/40 transition">
      <td class="py-2 px-2.5 font-mono font-bold text-indigo-400">Iter ${h.iteration}</td>
      <td class="py-2 px-2.5">
        ${h.converged ? '<span class="px-1.5 py-0.5 text-[10px] bg-emerald-900/50 text-emerald-300 rounded font-semibold">Converged</span>' : '<span class="px-1.5 py-0.5 text-[10px] bg-blue-900/50 text-blue-300 rounded font-semibold">Expanding</span>'}
      </td>
      <td class="py-2 px-2.5 font-mono text-gray-200">+${h.new_nodes_discovered} (${h.total_discovered_nodes})</td>
      <td class="py-2 px-2.5 font-mono font-bold text-amber-300">${h.marginal_impact_gain_pct}%</td>
      <td class="py-2 px-2.5 text-gray-400 text-[11px]">${h.reason}</td>
    </tr>
  `).join('');

  const vectors = n1.vectors || [];
  if (vectors.length === 0) {
    n1VectorsContainer.innerHTML = `<div class="p-3 bg-gray-900/60 rounded-lg text-gray-500 text-xs">No multi-root vectors isolated.</div>`;
    return;
  }

  n1VectorsContainer.innerHTML = vectors.map(v => `
    <div class="bg-gray-900/70 p-3 rounded-lg border border-indigo-900/30 space-y-1.5">
      <div class="flex items-center justify-between">
        <span class="font-mono text-xs font-bold text-indigo-300 flex items-center gap-1.5">
          <i data-lucide="git-commit" class="w-3.5 h-3.5 text-indigo-400"></i> ${v.vector_id}
        </span>
        <span class="px-2 py-0.5 text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 rounded-full border border-indigo-500/30">
          Impact: ${v.impact_score}
        </span>
      </div>
      <div class="text-[11px] text-gray-300">
        <span class="text-gray-500">Entrypoint:</span> <code class="text-amber-300 font-mono">[${v.entry_tier}] ${v.entry_host}</code> &bull; <code class="text-white">${v.entry_entity}</code>
      </div>
      <div class="text-[11px] text-gray-400">
        <span class="text-gray-500">Trajectory Length:</span> ${v.path_length} hops &bull; ${v.description}
      </div>
    </div>
  `).join('');
}

// ============================================================================
// NOVELTY 2: CHOKE POINTS
// ============================================================================
function renderNovelty2(n2) {
  if (!n2ChokeBody) return;
  const chokePoints = n2.choke_points || [];

  if (chokePoints.length === 0) {
    n2ChokeBody.innerHTML = `<tr><td colspan="7" class="py-4 text-center text-gray-500">No cut-vertices or choke points detected.</td></tr>`;
    return;
  }

  n2ChokeBody.innerHTML = chokePoints.map(cp => {
    const isCut = cp.is_cut_vertex;
    const effBadge = cp.containment_efficiency_pct >= 90 ? 'bg-emerald-900/50 text-emerald-300 border-emerald-700/50' :
                     cp.containment_efficiency_pct >= 60 ? 'bg-yellow-900/50 text-yellow-300 border-yellow-700/50' :
                     'bg-gray-800 text-gray-400 border-gray-700';

    return `
      <tr class="hover:bg-gray-900/40 transition">
        <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-gray-800 text-gray-300">${cp.tier}</span></td>
        <td class="py-2.5 px-3 font-mono text-gray-300">${cp.host_id}</td>
        <td class="py-2.5 px-3 font-mono text-amber-300 text-[11px]">${cp.action} &bull; ${cp.entity}</td>
        <td class="py-2.5 px-3 font-mono font-bold">
          <span class="px-2 py-0.5 rounded text-[11px] border ${effBadge}">${cp.containment_efficiency_pct}%</span>
        </td>
        <td class="py-2.5 px-3 font-mono text-gray-300">${cp.paths_severed} / ${cp.total_paths}</td>
        <td class="py-2.5 px-3">
          ${isCut ? '<span class="px-2 py-0.5 rounded text-[10px] bg-red-900/50 text-red-300 font-bold border border-red-700/50">YES (CUT-VERTEX)</span>' : '<span class="px-2 py-0.5 rounded text-[10px] bg-gray-800 text-gray-500">NO</span>'}
        </td>
        <td class="py-2.5 px-3 text-gray-300 text-[11px]">${cp.mitigation_recommendation}</td>
      </tr>
    `;
  }).join('');
}

// ============================================================================
// NOVELTY 3: CAUSAL BRIDGE IMPUTATION
// ============================================================================
function renderNovelty3(n3) {
  if (!n3BridgeBody) return;
  const bridges = n3.bridges || [];

  if (bridges.length === 0) {
    n3BridgeBody.innerHTML = `<tr><td colspan="6" class="py-4 text-center text-gray-500">No missing causal bridges inferred. Graph continuity is unbroken.</td></tr>`;
    return;
  }

  n3BridgeBody.innerHTML = bridges.map(b => `
    <tr class="hover:bg-gray-900/40 transition">
      <td class="py-2 px-3 font-mono text-cyan-300 text-[11px]">${b.source_uuid.slice(0, 8)}... (${b.source_host})</td>
      <td class="py-2 px-3 font-mono text-indigo-300 text-[11px]">${b.target_uuid.slice(0, 8)}... (${b.target_host})</td>
      <td class="py-2 px-3 font-mono text-gray-300">${b.time_delta_sec}s</td>
      <td class="py-2 px-3 font-mono text-amber-300">${(b.endpoint_similarity * 100).toFixed(0)}%</td>
      <td class="py-2 px-3 font-mono font-bold text-pink-400">${b.confidence_pct}%</td>
      <td class="py-2 px-3 text-gray-300 text-[11px]">${b.rationale}</td>
    </tr>
  `).join('');
}

// ============================================================================
// NOVELTY 4: ACTIVE REMEDIATION
// ============================================================================
function renderNovelty4(n4) {
  if (!n4PoliciesContainer || !n4ScriptPreview) return;
  const policies = n4.policies || [];

  if (policies.length === 0) {
    n4PoliciesContainer.innerHTML = `<div class="p-3 bg-gray-900/60 rounded-lg text-gray-500 text-xs">No active remediation policies synthesized.</div>`;
  } else {
    n4PoliciesContainer.innerHTML = policies.map(p => `
      <div class="bg-gray-900/80 p-3.5 rounded-lg border border-emerald-900/40 space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30 uppercase">
              ${p.mechanism}
            </span>
            <span class="text-xs font-mono font-semibold text-gray-200">[${p.target_tier}] ${p.target_host}</span>
          </div>
          <span class="text-xs font-mono font-bold text-emerald-400">RPS: ${p.rps_score.toFixed(1)}</span>
        </div>
        <p class="text-xs text-gray-300">${p.description}</p>
        <div class="bg-gray-950 p-2 rounded font-mono text-[11px] text-cyan-300 border border-gray-800 break-all select-all">
          ${p.command}
        </div>
        <div class="flex items-center justify-between text-[11px] text-gray-400">
          <span>Containment: <strong class="text-emerald-400">${p.containment_efficacy_pct}%</strong></span>
          <span>Collateral Disruption (CDI): <strong class="text-amber-400">${p.collateral_disruption_index}</strong></span>
        </div>
      </div>
    `).join('');
  }

  n4ScriptPreview.textContent = n4.deployment_script || '# No deployment script generated.';
}

function handleDownloadScript() {
  if (!currentAnalysis || !currentAnalysis.novelty4_remediation?.deployment_script) {
    alert('No containment script available to download.');
    return;
  }
  const scriptContent = currentAnalysis.novelty4_remediation.deployment_script;
  const blob = new Blob([scriptContent], { type: 'text/x-sh;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `cloud_m7_active_containment_${Date.now()}.sh`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ============================================================================
// NOVELTY 5: MITRE ATT&CK MAPPING
// ============================================================================
function renderNovelty5(n5) {
  if (!n5MitreBody) return;
  const matches = n5.matches || [];

  if (matches.length === 0) {
    n5MitreBody.innerHTML = `<tr><td colspan="6" class="py-4 text-center text-gray-500">No MITRE ATT&CK motifs mapped.</td></tr>`;
    return;
  }

  n5MitreBody.innerHTML = matches.map(m => `
    <tr class="hover:bg-gray-900/40 transition">
      <td class="py-2.5 px-3">
        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
          ${m.tactic_name}
        </span>
      </td>
      <td class="py-2.5 px-3 font-mono font-semibold text-white">
        <span class="text-cyan-400">${m.technique_id}</span> &bull; ${m.technique_name}
      </td>
      <td class="py-2.5 px-3 font-mono text-gray-300">${m.tier}</td>
      <td class="py-2.5 px-3 font-mono text-gray-400 text-[11px]">${m.host_id}</td>
      <td class="py-2.5 px-3 font-mono font-bold text-emerald-400">${m.confidence_pct}%</td>
      <td class="py-2.5 px-3 text-gray-300 text-[11px]">${m.reasoning}</td>
    </tr>
  `).join('');
}

// ============================================================================
// PARQUET + DUCKDB ZERO-SERVER SQL
// ============================================================================
async function executeSql() {
  const query = sqlInput.value.trim();
  if (!query) return;

  btnRunSql.disabled = true;
  btnRunSql.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Executing...</span>';
  lucide.createIcons();

  try {
    const res = await fetch('/api/sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const result = await res.json();
    if (result.status === 'error') {
      throw new Error(result.message);
    }

    sqlPerfBadge.textContent = `⚡ Executed in ${result.latency_ms} ms (${result.row_count} rows returned)`;

    // Render table head
    sqlThead.innerHTML = `<tr>${result.columns.map(c => `<th class="py-2 px-3">${c}</th>`).join('')}</tr>`;

    // Render table body
    if (result.rows.length === 0) {
      sqlTbody.innerHTML = `<tr><td colspan="${result.columns.length}" class="py-3 text-center text-gray-500">0 rows returned.</td></tr>`;
    } else {
      sqlTbody.innerHTML = result.rows.map(row => `
        <tr class="hover:bg-gray-900/40 transition">
          ${result.columns.map(col => `<td class="py-2 px-3 text-gray-300">${row[col] !== null ? row[col] : '<span class="text-gray-600">NULL</span>'}</td>`).join('')}
        </tr>
      `).join('');
    }
  } catch (err) {
    alert('SQL Execution Failed: ' + err.message);
    sqlPerfBadge.textContent = `❌ Error: ${err.message}`;
  } finally {
    btnRunSql.disabled = false;
    btnRunSql.innerHTML = '<i data-lucide="play" class="w-4 h-4"></i><span>Execute SQL</span>';
    lucide.createIcons();
  }
}

// ============================================================================
// HARDWARE TESTBED TRIGGER
// ============================================================================
async function handleHardwareTrigger() {
  btnTriggerHardware.disabled = true;
  btnTriggerHardware.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Interrogating Probe...</span>';
  lucide.createIcons();

  try {
    const res = await fetch('/api/hardware/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count: 5 })
    });
    const result = await res.json();

    if (result.status !== 'success') {
      throw new Error(result.message || 'Probe response error');
    }

    hardwareEventsContainer.innerHTML = result.events.map((e, idx) => {
      const isAttack = e.payload?.is_attack;
      return `
        <div class="bg-gray-900/80 p-3 rounded-lg border ${isAttack ? 'border-red-500/50 bg-red-950/10' : 'border-gray-800'} space-y-1">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 text-[10px] font-bold bg-rose-500/20 text-rose-300 rounded border border-rose-500/30">
                Raspberry Pi Edge Probe (${e.host_id})
              </span>
              <span class="font-mono text-xs font-semibold text-gray-300">${e.event_type} &bull; ${e.payload?.action}</span>
            </div>
            ${isAttack ? '<span class="px-2 py-0.5 text-[10px] font-bold bg-red-600 text-white rounded">TAMPER ATTACK DETECTED</span>' : '<span class="px-2 py-0.5 text-[10px] font-semibold bg-emerald-900/60 text-emerald-300 rounded">GENUINE SENSOR</span>'}
          </div>
          <div class="text-[11px] text-gray-300 font-mono">
            <span class="text-gray-500">Target Entity:</span> ${e.payload?.entity}
            ${e.payload?.cpu_temp_c ? `&bull; <span class="text-amber-400 font-semibold">CPU Temp: ${e.payload.cpu_temp_c}&deg;C</span>` : ''}
          </div>
          <div class="text-[10px] font-mono text-gray-500 break-all">
            <span class="text-gray-400">HMAC-SHA256 Signature:</span> ${e.tamper_hash}
          </div>
        </div>
      `;
    }).join('');

  } catch (err) {
    alert('Hardware probe interrogation failed: ' + err.message);
  } finally {
    btnTriggerHardware.disabled = false;
    btnTriggerHardware.innerHTML = '<i data-lucide="zap" class="w-4 h-4"></i><span>Trigger Live Hardware Telemetry Cycle (5 Events)</span>';
    lucide.createIcons();
  }
}

// ============================================================================
// RAW SECURITY DATASET UPLOAD
// ============================================================================
async function handleFileUpload() {
  const file = uploadInput.files[0];
  if (!file) {
    alert('Please select a file to upload first.');
    return;
  }

  btnUpload.disabled = true;
  btnUpload.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Normalizing Schema...</span>';
  lucide.createIcons();

  const formData = new FormData();
  formData.append('dataset_file', file);

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    if (result.status === 'error') {
      throw new Error(result.message);
    }

    // Add option to select dropdown
    const opt = document.createElement('option');
    opt.value = result.dataset_key;
    opt.textContent = `Uploaded: ${file.name} (${result.detected_format})`;
    opt.selected = true;
    datasetSelect.appendChild(opt);

    currentAnalysis = result;
    populateDashboard(result);

    alert(`Successfully normalized ${file.name} using adapter: ${result.detected_format}!\n${result.summary.total_events} canonical events ingested.`);
  } catch (err) {
    alert('Upload & Normalization failed: ' + err.message);
  } finally {
    btnUpload.disabled = false;
    btnUpload.innerHTML = '<i data-lucide="check-circle" class="w-4 h-4"></i><span>Upload & Normalize</span>';
    lucide.createIcons();
  }
}
