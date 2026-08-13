#!/usr/bin/env node
// CDP 诊断:对比"本地浏览器"与"渲染器环境"下页面元素的实测值。
// 用途:素材本地 Chrome 打开正常、HyperFrames 渲染输出异常(字号/布局不同)时,
//       读 .nowrap 等元素的 computed 值,定位差异来源(字体度量、容器宽度等)。
// 用法:
//   1. 后台启动 Chrome: "Google Chrome" --headless=new --remote-debugging-port=9333 \
//        --disable-gpu --no-first-run --user-data-dir=/tmp/chrome-diag "file:///path/index.html"
//   2. node fit-diag.mjs [port=9333] [selector=.nowrap]
import { spawn } from 'child_process';

const PORT = parseInt(process.argv[2] || '9333');
const SEL = process.argv[3] || '.nowrap';

// 若端口无 Chrome,自动拉起(可选):自行改 CHROME 路径
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = process.argv[4];

async function main() {
  // 探测端口
  let targets;
  try {
    targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
  } catch {
    if (!URL) { console.error('端口无 Chrome 且未提供 URL(第 4 参数)'); process.exit(1); }
    console.error('端口无 Chrome,自动拉起…');
    spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`,
      '--disable-gpu', '--no-first-run', '--user-data-dir=/tmp/chrome-diag-' + Date.now(), URL],
      { stdio: 'ignore' });
    await new Promise(r => setTimeout(r, 4000));
    targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
  }
  const page = targets.find(t => t.type === 'page');
  if (!page) { console.error('无 page target'); process.exit(1); }
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  const send = (method, params = {}) => new Promise((resolve) => {
    const mid = ++id;
    pending.set(mid, resolve);
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); }
  };
  await new Promise(r => ws.onopen = r);
  await send('Runtime.enable');
  await new Promise(r => setTimeout(r, 1500));
  const expr = `
    (() => {
      const out = [];
      document.querySelectorAll('${SEL}').forEach(el => {
        const cs = getComputedStyle(el);
        const p = el.parentElement;
        out.push({
          id: el.id || el.className,
          display: cs.display,
          fontSize: cs.fontSize,
          clientW: el.clientWidth,
          scrollW: el.scrollWidth,
          parentW: p ? p.clientWidth : null,
          text: el.textContent.slice(0, 24)
        });
      });
      return JSON.stringify(out);
    })()
  `;
  const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  const data = JSON.parse(res.result.value);
  for (const d of data) {
    console.log(`${(d.id || '').slice(0, 26).padEnd(28)} fs=${d.fontSize.padEnd(7)} client=${String(d.clientW).padStart(4)} scroll=${String(d.scrollW).padStart(4)} parent=${String(d.parentW).padStart(4)} | ${d.text}`);
  }
  process.exit(0);
}
main();
