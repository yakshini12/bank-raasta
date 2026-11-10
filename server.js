const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');

const ROOT = __dirname;
const PUBLIC = path.join(ROOT, 'public');
const MAX_BODY = 20 * 1024 * 1024;

function loadEnv() {
  const file = path.join(ROOT, '.env');
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (match && process.env[match[1]] === undefined) {
      process.env[match[1]] = match[2].replace(/^(['"])(.*)\1$/, '$2');
    }
  }
}
loadEnv();

function json(res, status, value) {
  const data = Buffer.from(JSON.stringify(value));
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': data.length,
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  });
  res.end(data);
}

function readBody(req, limit = MAX_BODY) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', chunk => {
      size += chunk.length;
      if (size > limit) {
        reject(Object.assign(new Error('The upload is too large.'), { statusCode: 413 }));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

async function transcribe(req, res) {
  if (!process.env.GNANI_API_KEY) {
    return json(res, 503, { error: 'Gnani is not configured. Add GNANI_API_KEY to your local .env file.' });
  }
  const contentType = req.headers['content-type'] || '';
  if (!contentType.startsWith('multipart/form-data;')) return json(res, 400, { error: 'Choose an audio file to transcribe.' });
  try {
    const response = await fetch('https://api.vachana.ai/stt/v3', {
      method: 'POST',
      headers: { 'Content-Type': contentType, 'X-API-Key-ID': process.env.GNANI_API_KEY },
      body: await readBody(req),
      signal: AbortSignal.timeout(45000)
    });
    const data = await response.text();
    res.writeHead(response.status, {
      'Content-Type': response.headers.get('content-type') || 'application/json',
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff'
    });
    res.end(data);
  } catch (error) {
    json(res, error.statusCode || 502, { error: error.message || 'Speech recognition failed.' });
  }
}

async function synthesize(req, res) {
  if (!process.env.GNANI_API_KEY) return json(res, 503, { error: 'Gnani is not configured. Add GNANI_API_KEY to your local .env file.' });
  try {
    const input = JSON.parse((await readBody(req, 16 * 1024)).toString('utf8'));
    const text = String(input.text || '').trim();
    const language = String(input.language || 'hi-IN');
    if (!text || text.length > 1800) return json(res, 400, { error: 'Speech text must be 1–1,800 characters.' });
    if (!['hi-IN', 'en-IN'].includes(language)) return json(res, 400, { error: 'This prototype currently speaks Hindi and English.' });

    const response = await fetch('https://api.vachana.ai/api/v1/tts/inference', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key-ID': process.env.GNANI_API_KEY },
      body: JSON.stringify({
        text,
        voice: language === 'hi-IN' ? 'Shivani' : 'Avinash',
        model: 'timbre-v3.0',
        language,
        speed: 0.94,
        audio_config: { sample_rate: 24000, num_channels: 1, sample_width: 2, encoding: 'linear_pcm', container: 'wav' }
      }),
      signal: AbortSignal.timeout(45000)
    });
    const audio = Buffer.from(await response.arrayBuffer());
    res.writeHead(response.status, {
      'Content-Type': response.headers.get('content-type') || (response.ok ? 'audio/wav' : 'application/json'),
      'Content-Length': audio.length,
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff'
    });
    res.end(audio);
  } catch (error) {
    json(res, error.statusCode || 502, { error: error.message || 'Speech playback could not be created.' });
  }
}

const contentTypes = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml' };
function serveStatic(req, res) {
  const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
  const file = path.resolve(PUBLIC, relative);
  if (!file.startsWith(PUBLIC + path.sep)) return json(res, 403, { error: 'Forbidden.' });
  fs.readFile(file, (error, data) => {
    if (error) return json(res, 404, { error: 'Not found.' });
    res.writeHead(200, {
      'Content-Type': contentTypes[path.extname(file)] || 'application/octet-stream',
      'Content-Length': data.length,
      'Cache-Control': 'no-cache',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer'
    });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const route = new URL(req.url, 'http://localhost').pathname;
  if (req.method === 'GET' && route === '/api/health') return json(res, 200, { gnaniConfigured: Boolean(process.env.GNANI_API_KEY) });
  if (req.method === 'POST' && route === '/api/stt') return transcribe(req, res);
  if (req.method === 'POST' && route === '/api/tts') return synthesize(req, res);
  if (req.method !== 'GET' && req.method !== 'HEAD') return json(res, 405, { error: 'Method not allowed.' });
  serveStatic(req, res);
});

const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 3003);
server.listen(port, host, () => {
  console.log(`Bank Raasta is running at http://${host}:${port}`);
  console.log(`Gnani voice: ${process.env.GNANI_API_KEY ? 'configured' : 'not configured (sample mode)'}`);
});
