/**
 * CLOUD-M7 Fast Node.js Web Dashboard Server
 * Powered by Express.js, Vis-Network, Tailwind CSS, DuckDB & Python Bridge.
 */

const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3001;

// Directories
const CAPSTONE_DIR = path.resolve(__dirname, '..');
const UPLOADS_DIR = path.resolve(__dirname, 'uploads');
const PYTHON_PATH = path.resolve(CAPSTONE_DIR, '.venv', 'Scripts', 'python.exe');

// In-memory Cache for instant responses
const cache = {};

// Ensure upload directory exists
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

// Multer storage for uploaded datasets
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) => {
    const safeName = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
    cb(null, `${Date.now()}_${safeName}`);
  }
});
const upload = multer({ storage });

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

/**
 * Spawns the Python Bridge API and returns parsed JSON.
 */
function runPythonBridge(args) {
  return new Promise((resolve, reject) => {
    const pythonExe = fs.existsSync(PYTHON_PATH) ? PYTHON_PATH : 'python';
    const py = spawn(pythonExe, ['-m', 'cloud_m7.bridge_api', ...args], {
      cwd: CAPSTONE_DIR,
      env: { ...process.env, PYTHONPATH: CAPSTONE_DIR }
    });

    let stdout = '';
    let stderr = '';

    py.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    py.stderr.on('data', (chunk) => { stderr += chunk.toString(); });

    py.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(stderr || `Python bridge failed with exit code ${code}`));
      }
      try {
        const json = JSON.parse(stdout);
        resolve(json);
      } catch (err) {
        reject(new Error(`Failed to parse bridge output: ${err.message}\nRaw: ${stdout.slice(0, 500)}`));
      }
    });
  });
}

// ============================================================================
// API ROUTES
// ============================================================================

// 1. Health & Info
app.get('/api/health', (req, res) => {
  res.json({
    status: 'online',
    version: '1.0.0',
    framework: 'CLOUD-M7 Node.js High-Speed Dashboard',
    node_version: process.version,
    port: PORT
  });
});

// 2. Full Analysis (Cached & Instant)
app.get('/api/analyze', async (req, res) => {
  const dataset = req.query.dataset || 'synthetic';
  const force = req.query.force === 'true';

  if (!force && cache[dataset]) {
    return res.json({ ...cache[dataset], from_cache: true });
  }

  try {
    const data = await runPythonBridge(['--action', 'analyze', '--dataset', dataset]);
    cache[dataset] = data;
    res.json(data);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// 3. File Upload & Normalization
app.post('/api/upload', upload.single('dataset_file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ status: 'error', message: 'No file uploaded.' });
  }

  const uploadedPath = req.file.path;

  try {
    const data = await runPythonBridge(['--action', 'analyze', '--dataset', uploadedPath]);
    const datasetKey = `custom_${req.file.originalname}`;
    cache[datasetKey] = data;
    res.json({ ...data, dataset_key: datasetKey });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// 4. Zero-Server SQL Execution via DuckDB
app.post('/api/sql', async (req, res) => {
  const query = req.body.query;
  if (!query) {
    return res.status(400).json({ status: 'error', message: 'Missing SQL query.' });
  }

  try {
    const result = await runPythonBridge(['--action', 'sql', '--query', query]);
    res.json(result);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// 5. Hardware Probe Telemetry Trigger
app.post('/api/hardware/trigger', async (req, res) => {
  const count = req.body.count || 5;
  try {
    const result = await runPythonBridge(['--action', 'hardware', '--count', String(count)]);
    res.json(result);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Start Server
app.listen(PORT, () => {
  console.log(`========================================================================`);
  console.log(`  CLOUD-M7 HIGH-SPEED NODE.JS DASHBOARD`);
  console.log(`  Server listening at: http://localhost:${PORT}`);
  console.log(`  Zero-Lag UI powered by Express, Vis.js, Tailwind, DuckDB & Python`);
  console.log(`========================================================================`);
});
