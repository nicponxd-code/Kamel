:root{--bg:#f2f2f6;--teal:#0aa6a6;--panel:#fff;--border:#d6d6de;--text:#111;--muted:#666;--red:#ef4444;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,system-ui,Segoe UI,Roboto,Arial,sans-serif}
.hidden{display:none}

/* Top bar */
.topbar{position:sticky;top:0;z-index:5;background:var(--teal);color:#fff;padding:10px 12px;display:flex;align-items:center;justify-content:space-between;gap:10px}
.brand{display:flex;align-items:center;gap:10px;min-width:0}
.logo{width:28px;height:28px;border-radius:6px;background:rgba(255,255,255,.18)}
.title{font-weight:800}
.subtitle{font-size:12px;opacity:.9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.top-actions{display:flex;gap:8px}
.btn,.btn-ghost,.iconbtn{border:1px solid rgba(255,255,255,.35);background:rgba(255,255,255,.18);color:#fff;padding:8px 10px;border-radius:10px;font-weight:700;cursor:pointer}
.btn:active,.btn-ghost:active,.iconbtn:active{transform:translateY(1px)}

/* Home */
.home{min-height:calc(100vh - 56px);padding-bottom:70px}
.homeHeader{background:var(--teal);color:#fff;padding:14px 14px 12px}
.homeTitle{font-weight:900;font-size:18px}
.homeSub{font-size:12px;opacity:.9;margin-top:4px}
.homeGrid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}
.homeTile{background:#fff;border:1px solid var(--border);border-radius:12px;padding:10px;text-align:left;cursor:pointer}
.homeThumb{height:80px;border-radius:10px;background:#f7f7fb;display:flex;align-items:center;justify-content:center;margin-bottom:8px}
.homeThumb svg{width:110px;height:60px}
.homeLabel{font-weight:800;font-size:13px}

/* Bottom nav */
.bottomNav{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:10px 8px;z-index:10}
.navItem{border:0;background:transparent;color:var(--muted);font-weight:700}
.navActive{color:var(--teal)}

/* Calc panel */
.wrap{max-width:1200px;margin:0 auto;padding:12px}
.panel{background:#fff;border:1px solid var(--border);border-radius:12px;padding:12px;margin:12px 0}
.grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:12px}
@media (max-width:980px){.grid{grid-template-columns:1fr}}

h2{margin:0 0 10px;font-size:15px}
h3{margin:0 0 8px;font-size:13px;color:var(--muted)}
label{display:block;font-size:13px;margin:10px 0}
input,select{width:100%;padding:10px;border:1px solid var(--border);border-radius:10px;font-size:14px;background:#fff}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.row3{grid-template-columns:1fr 1fr 1fr}
@media (max-width:980px){.row3{grid-template-columns:1fr}}
.checkbox{display:flex;gap:10px;align-items:center}
.checkbox input{width:auto}
.box{border:1px solid var(--border);border-radius:12px;padding:10px;margin:10px 0}
.suggestions{font-size:12px;color:var(--muted);margin-top:10px}
.status{font-size:13px;color:var(--muted);margin-top:10px}
.results,.steps{font-size:13px;line-height:1.45}
.templates{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.template{border:1px solid var(--border);border-radius:12px;padding:10px}
.template-title{font-size:12px;color:var(--muted);margin-bottom:6px}
.svgHost{border:1px solid var(--border);border-radius:12px;padding:10px;background:#fcfdff;overflow:auto}

.computeBtn{width:100%;margin-top:8px;border:0;background:var(--teal);color:#fff;padding:12px 12px;border-radius:12px;font-weight:900;font-size:15px;cursor:pointer}
.computeBtn:active{transform:translateY(1px)}
