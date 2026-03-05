/**
 * AI360 TRADING — APPSCRIPT v12.0 FINAL
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 *
 * COMPLETE CHANGELOG:
 *   v9  — Fixed 4 bugs: wrong SL (AA→ATR), duplicate col Y logic, VALUE BUY signal, AVOID filter
 *   v10 — Fixed Q2/Q4→T2/T4, pad(17→20), Risk ₹ calc, 3 workflow modes, 5+10 slots
 *   v11 — MIN_PRIORITY 20→18, HOLD signal added, CMP cap ₹10k→₹5k, MIN_RR 2.0→1.3,
 *          type-specific ATR targets (Intraday×2, Swing×3, Positional×4)
 *   v12 — Market regime filter, volume confirmation (1.2×avg), sector exposure cap (max 2),
 *          stale waiting refresh, weekly P&L summary (Friday auto), Google error suppressor
 *
 * ALERTLOG COLUMN MAP (1-based sheet col):
 *   A=1   Signal Time (IST)
 *   B=2   Symbol
 *   C=3   Live Price          ← VLOOKUP formula (auto)
 *   D=4   Priority Score      ← from Nifty200
 *   E=5   Trade Type          ← Intraday / Swing / Positional / Options Alert
 *   F=6   Strategy            ← FINAL_ACTION from Nifty200
 *   G=7   Breakout Stage      ← from Nifty200 col W
 *   H=8   Initial SL          ← ATR-based, AppScript writes ONCE
 *   I=9   Target              ← type-specific ATR multiplier
 *   J=10  RR Ratio            ← calculated
 *   K=11  Trade Status        ← Python writes TRADED / EXITED
 *   L=12  Entry Price         ← Python writes when TRADED (blank for WAITING)
 *   M=13  Entry Time          ← Python writes when TRADED (blank for WAITING)
 *   N=14  Days in Trade       ← Formula (auto)
 *   O=15  Trailing SL         ← Python updates live (AppScript NEVER touches)
 *   P=16  P/L %               ← Formula (auto)
 *   Q=17  ATH Warning         ← Formula (auto)
 *   R=18  Risk ₹              ← Formula (auto)
 *   S=19  Position Size       ← Formula (auto)
 *   T=20  SYSTEM CONTROL      ← T2=YES/NO automation switch, T4=memory string
 *
 * NIFTY200 COLUMN MAP (0-based array index):
 *   r[0]  A   NSE_SYMBOL         r[1]  B   SECTOR
 *   r[2]  C   CMP                r[3]  D   %Change
 *   r[4]  E   20_DMA             r[5]  F   50_DMA
 *   r[6]  G   200_DMA            r[7]  H   SMA_Structure
 *   r[8]  I   52_Weeks_Low       r[9]  J   52_Weeks_High
 *   r[10] K   %up_from_52W_Low   r[11] L   %down_from_52W_High
 *   r[12] M   %Dist_from_20DMA   r[13] N   Avg_Volume(20D)
 *   r[14] O   Volume_vs_Avg%  ← volume confirmation filter
 *   r[15] P   FII_Buy_Zone       r[16] Q   FII_Rating
 *   r[17] R   Leader_Type        r[18] S   Signal_Score
 *   r[19] T   FINAL_ACTION    ← strategy signal
 *   r[20] U   RS                 r[21] V   Sector_Trend
 *   r[22] W   Breakout_Stage     r[23] X   Retest%
 *   r[24] Y   Trade_Type      ← read directly
 *   r[25] Z   Priority_Score  ← filter >= 18
 *   r[26] AA  Pivot_Support      r[27] AB  VCP_Status
 *   r[28] AC  ATR(14)         ← SL + Target calc
 *   r[29] AD  Days_Since_Low
 *
 * SL + TARGET (ATR-based, type-specific):
 *   Intraday   → SL = CMP - ATR×1.5 | Target = CMP + ATR×2  | RR ≈ 1.33
 *   Swing      → SL = CMP - ATR×2.0 | Target = CMP + ATR×3  | RR ≈ 1.50
 *   Positional → SL = MAX(CMP-ATR×2.5, 20DMA) | Target = CMP+ATR×4 | RR ≈ 1.60
 *   Value Buy  → SL = MAX(CMP-ATR×2.5, 50DMA) | Target = CMP+ATR×4
 *
 * FILTERS (in order):
 *   1. FINAL_ACTION must be valid signal (col T)
 *   2. Priority >= 18 (col Z)
 *   3. Stale refresh log if waiting > 3 days
 *   4. CMP > 0 and ATR > 0
 *   5. Volume >= 1.2× average (col O)
 *   6. CMP <= ₹5,000 (min 2 shares)
 *   7. ATH buffer >= 3% (col J)
 *   8. Trade_Type != AVOID / NO TRADE (col Y)
 *   9. Sector exposure < 2 per sector
 *   10. RR >= 1.3
 *
 * MARKET REGIME:
 *   Nifty50 row in Nifty200 (row 2) — if CMP < 20DMA → no new entries
 *   Existing TRADED rows always monitored regardless of regime
 *
 * PYTHON HANDSHAKE:
 *   AppScript → K="⏳ WAITING", H=InitialSL, I=Target, L="", M=""
 *   Python    → reads C (live price), writes K="🟢 TRADED (PAPER)", L=CMP, M=timestamp, O=InitialSL
 *   Python    → updates O (Trailing SL) as price rises — AppScript NEVER overwrites O
 *   Python    → writes K="EXITED" on SL/target/hard-loss hit
 *   AppScript → sees EXITED on next scan, removes row, fills next best candidate
 *
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

const CONFIG = {
  TELEGRAM_TOKEN : "hidden",          // Replace with your token
  CHAT_ID        : "hidden",          // Replace with your chat ID
  SHEET_NAME     : "Nifty200",        // Master screener sheet name
  LOG_SHEET      : "AlertLog",        // Trade entry/monitoring sheet
  HISTORY_SHEET  : "History",         // Closed trades history sheet
  IST_ZONE       : "GMT+5:30",

  MAX_TRADES     : 5,                 // Max active traded positions
  MAX_WAITING    : 10,                // Always keep 10 waiting candidates
  MIN_PRIORITY   : 18,                // Min priority (18+ for more candidates)
  MIN_RR         : 1.3,               // Min RR — 1.3 allows all trade types to qualify
  ATH_BUFFER_PCT : 3.0,               // Skip if within 3% of 52W High
  CAPITAL        : 10000,             // ₹ per trade
  MAX_CMP        : 5000,              // Skip stocks above ₹5000 (min 2 shares at ₹10k)

  // Type-specific ATR multipliers — longer hold = bigger target
  // Intraday:   SL=ATR×1.5  Target=ATR×2   RR=1.33
  // Swing:      SL=ATR×2.0  Target=ATR×3   RR=1.50
  // Positional: SL=ATR×2.5  Target=ATR×4   RR=1.60
  ATR_SL_INTRADAY   : 1.5,
  ATR_SL_SWING      : 2.0,
  ATR_SL_POSITIONAL : 2.5,
  ATR_TGT_INTRADAY  : 2,
  ATR_TGT_SWING     : 3,
  ATR_TGT_POSITIONAL: 4,

  TOTAL_COLS     : 19,                // A–S data grid (T = system control)
  LOG_ROWS       : 15,                // Rows 2–16 (5 traded + 10 waiting)
};

// ── MENU ─────────────────────────────────────────────────────────────────────
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 AI360 TRADING')
    .addItem('🔄 MANUAL SYNC',       'unifiedManager')
    .addItem('📊 DAILY SUMMARY',     'sendDailySummary')
    .addItem('📅 WEEKLY SUMMARY',    'sendWeeklySummary')
    .addSeparator()
    .addItem('🧹 FRESH CLEAN START', 'freshCleanStart')
    .addToUi();
}

// ── DAILY SUMMARY ─────────────────────────────────────────────────────────────
function sendDailySummary() {
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.LOG_SHEET);
  const data     = logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();
  const traded   = data.filter(r => _isTraded(r[10])).length;
  const waiting  = data.filter(r => _isWaiting(r[10])).length;
  _sendTelegram(
    `📊 <b>MARKET SUMMARY</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `🔹 <b>Active Trades:</b> ${traded}/${CONFIG.MAX_TRADES}\n` +
    `🔸 <b>Waiting Slots:</b> ${waiting}\n` +
    `💰 <b>Capital Deployed:</b> ₹${traded * CONFIG.CAPITAL}\n` +
    `✅ <i>System: Online</i>`
  );
}

// ── MAIN CONTROLLER ───────────────────────────────────────────────────────────
function unifiedManager() {
  try {
    _runUnifiedManager();
  } catch(e) {
    // Catch Google server errors (INTERNAL, storage blips) silently
    // These are Google infrastructure failures, not code bugs
    // Script will retry automatically on next 5-min trigger
    const msg = e.toString();
    if (msg.includes("INTERNAL") || msg.includes("storage") || msg.includes("server error")) {
      Logger.log("[GOOGLE ERROR] Transient server error — will retry next trigger: " + msg);
      return; // Silent exit — no email notification
    }
    // Real errors still throw so you get notified
    throw e;
  }
}

function _runUnifiedManager() {
  const now      = new Date();
  const timeStr  = Utilities.formatDate(now, CONFIG.IST_ZONE, "HH:mm");
  const today    = Utilities.formatDate(now, CONFIG.IST_ZONE, "yyyy-MM-dd");
  const dow      = now.getDay(); // 0=Sun, 5=Fri
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.LOG_SHEET);

  // Morning cleanup 9:05–9:15 IST, once per day
  if (timeStr >= "09:05" && timeStr <= "09:15") {
    const mem = (logSheet.getRange("T4").getValue() || "").toString();
    if (!mem.includes(today + "_CLEANED")) {
      clearWaitingRowsOnly();
      logSheet.getRange("T4").setValue(mem + "," + today + "_CLEANED");
    }
  }

  // Friday 15:30–15:45 IST: send weekly summary
  if (dow === 5 && timeStr >= "15:30" && timeStr <= "15:45") {
    const mem = (logSheet.getRange("T4").getValue() || "").toString();
    if (!mem.includes(today + "_WEEKLY")) {
      sendWeeklySummary();
      logSheet.getRange("T4").setValue(mem + "," + today + "_WEEKLY");
    }
  }

  runPriorityScanner();
} // end _runUnifiedManager

// ── PRIORITY SCANNER ──────────────────────────────────────────────────────────
function runPriorityScanner() {
  const ss          = SpreadsheetApp.getActiveSpreadsheet();
  const logSheet    = ss.getSheetByName(CONFIG.LOG_SHEET);
  const inputSheet  = ss.getSheetByName(CONFIG.SHEET_NAME);

  // ── Automation gate: T2 must be YES ──
  const switchVal = (logSheet.getRange("T2").getValue() || "").toString().toUpperCase();
  if (switchVal !== "YES") {
    Logger.log("[SKIP] Automation OFF — set T2=YES to enable");
    return;
  }

  const inputData  = inputSheet.getDataRange().getValues();
  // Read 19 cols A–S. Col T (system control) is never touched by the grid read/write.
  const currentLog = logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();
  const nowTime    = Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "yyyy-MM-dd HH:mm:ss");

  const alreadyTraded = new Set();
  const sectorCount   = {};   // track sector exposure in active trades

  // ── Step 1: Keep only active TRADED rows (drop EXITED, drop WAITING) ──
  const finalTraded = currentLog.filter(r => {
    const sym    = (r[1] || "").toString().trim();
    const status = (r[10] || "").toString().toUpperCase();
    if (sym && _isTraded(status)) {
      alreadyTraded.add(sym);
      // Track sector of active trades for exposure cap
      // Sector is not stored in AlertLog — look it up from Nifty200
      const nRow = inputData.find(nr => nr[0] === sym);
      if (nRow) {
        const sec = (nRow[1] || "UNKNOWN").toString().trim();
        sectorCount[sec] = (sectorCount[sec] || 0) + 1;
      }
      return true;
    }
    return false;
  });

  // Hard cap check — if already at MAX_TRADES, still fill WAITING slots (10 backup candidates)
  // Only skip the entire scan if we somehow exceed MAX_TRADES (safety)
  if (finalTraded.length > CONFIG.MAX_TRADES) {
    Logger.log(`[WARN] Traded rows ${finalTraded.length} exceeds MAX_TRADES ${CONFIG.MAX_TRADES}`);
    _restoreFormulas(logSheet);
    return;
  }

  // ── Market Regime Filter: Nifty50 must be above its 20-DMA ──────────────
  // If Nifty50 < 20-DMA → bearish market → stop ALL new WAITING entries
  // Existing TRADED rows are kept and monitored normally
  // Source: row 1 of Nifty200 sheet must be "NIFTY50" with CMP in col C and 20_DMA in col E
  let marketBullish = true;
  try {
    const niftyRow = inputData[1]; // row index 1 = sheet row 2 = Nifty50 index row
    if (niftyRow && niftyRow[0] && niftyRow[0].toString().includes("NIFTY")) {
      const niftyCmp  = parseFloat(niftyRow[2]) || 0;   // col C = CMP
      const nifty20d  = parseFloat(niftyRow[4]) || 0;   // col E = 20_DMA
      if (niftyCmp > 0 && nifty20d > 0) {
        marketBullish = niftyCmp >= nifty20d;
        Logger.log(`[REGIME] Nifty50 CMP=${niftyCmp} | 20DMA=${nifty20d} | Bullish=${marketBullish}`);
      }
    }
  } catch(e) {
    Logger.log("[REGIME] Could not read Nifty50 row — defaulting to bullish: " + e);
  }

  if (!marketBullish) {
    Logger.log("[REGIME] BEARISH — skipping new candidate scan. Existing trades monitored.");
    _restoreFormulas(logSheet);
    // Still write back existing traded rows so formulas stay fresh
    let bearGrid = finalTraded.concat([]);
    while (bearGrid.length < CONFIG.LOG_ROWS) bearGrid.push(new Array(CONFIG.TOTAL_COLS).fill(""));
    logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).clearContent();
    logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).setValues(bearGrid);
    _restoreFormulas(logSheet);
    // Send bearish alert only ONCE per day — memory flag in T4
    const bearMem = (logSheet.getRange("T4").getValue() || "").toString();
    const bearFlag = today + "_BEARISH";
    if (!bearMem.includes(bearFlag)) {
      _sendTelegram(`⚠️ <b>MARKET REGIME: BEARISH</b>\nNifty50 ₹${niftyCmp.toFixed(0)} below 20-DMA ₹${nifty20d.toFixed(0)}\nNo new entries today. Existing trades monitored normally.`);
      logSheet.getRange("T4").setValue(bearMem + "," + bearFlag);
    }
    return;
  }

  // ── Step 2: Scan Nifty200 for new WAITING candidates ──
  // Valid FINAL_ACTION signals — what qualifies for AlertLog
  // HOLD added: stocks in uptrend but consolidating = valid swing candidates
  // RISKY excluded: weak structure, skip
  const validSignals = [
    "🎯 RETEST BUY",      // Price retesting 30d high — highest conviction
    "🟢 STRONG BUY",      // Sector Leader + Strong Bull + Tailwind
    "💎 BASE PREPARED",   // VCP compression + days since low — breakout imminent
    "💰 VALUE BUY",       // Strong Bull + >10% below 52W high — deep discount
    "➖ HOLD",            // Uptrend but consolidating — valid if priority qualifies
  ];
  const candidates   = [];

  for (let i = 1; i < inputData.length; i++) {
    const r = inputData[i];
    if (!r[0] || alreadyTraded.has(r[0])) continue;

    const signal   = (r[19] || "").toString().trim();
    const priority = parseFloat(r[25]) || 0;

    if (!validSignals.includes(signal) || priority < CONFIG.MIN_PRIORITY) continue;

    // ── Stale waiting check: if stock already in WAITING >3 days, refresh it ──
    // AppScript re-scans and recalculates fresh SL/target from current price.
    // The old row gets replaced automatically in Step 4 write.
    // Just log for visibility — no skip needed (fresh calc happens below).
    const existingWait = currentLog.find(lr =>
      (lr[1] || "").toString().trim() === r[0].toString().trim() &&
      _isWaiting((lr[10] || "").toString().toUpperCase())
    );
    if (existingWait && existingWait[0]) {
      try {
        const ageDays = (new Date() - new Date(existingWait[0])) / 86400000;
        if (ageDays > 3) Logger.log(`[STALE REFRESH] ${r[0]}: was waiting ${ageDays.toFixed(1)} days — recalculating`);
      } catch(e) {}
    }

    const cmp    = parseFloat(r[2])  || 0;   // C  CMP
    const atr    = parseFloat(r[28]) || 0;   // AC ATR(14)
    const high52 = parseFloat(r[9])  || 0;   // J  52_Weeks_High
    const dma20  = parseFloat(r[4])  || 0;   // E  20_DMA
    const dma50  = parseFloat(r[5])  || 0;   // F  50_DMA

    if (cmp <= 0 || atr <= 0) continue;

    // ── Volume check: skip if volume < 1.2× average ──
    // r[14] = col O = Volume_vs_Avg% (e.g. 150 means 150% = 1.5× average)
    const volVsAvg = parseFloat(r[14]) || 0;
    if (volVsAvg > 0 && volVsAvg < 120) {
      Logger.log(`[VOL SKIP] ${r[0]}: Volume ${volVsAvg.toFixed(0)}% of avg — below 120% threshold`);
      continue;
    }

    // ── Price cap: skip if CMP > ₹5000 (min 2 shares needed at ₹10k capital) ──
    if (cmp > CONFIG.MAX_CMP) {
      Logger.log(`[PRICE SKIP] ${r[0]}: CMP ₹${cmp} > ₹${CONFIG.MAX_CMP} cap — fewer than 2 shares`);
      continue;
    }

    // ── ATH Check: skip if within 3% of 52W High ──
    if (high52 > 0) {
      const pctFromATH = ((high52 - cmp) / high52) * 100;
      if (pctFromATH < CONFIG.ATH_BUFFER_PCT) {
        Logger.log(`[ATH SKIP] ${r[0]}: ${pctFromATH.toFixed(1)}% below 52W High — too close`);
        continue;
      }
    }

    // ── Trade Type: READ directly from col Y (r[24]) — already calculated in Nifty200 ──
    // Values: "⚡ INTRADAY" / "🎯 SWING (Breakout)" / "📊 SWING (Trend)" /
    //         "💰 POSITIONAL (Value)" / "📈 POSITIONAL (Growth)" / "🚫 AVOID" / "⏸️ NO TRADE"
    const niftyTradeType = (r[24] || "").toString().trim();

    // Skip AVOID and NO TRADE from Nifty200's own classification
    if (niftyTradeType.includes("AVOID") || niftyTradeType.includes("NO TRADE")) {
      Logger.log(`[SKIP] ${r[0]}: Nifty200 Trade_Type = ${niftyTradeType}`);
      continue;
    }

    // Map Nifty200 trade type to our display labels + ATR multiplier for SL
    const { ttype } = _mapTradeType(niftyTradeType, priority, atr, cmp);

    // ── Initial SL + Target — type-specific ATR multipliers ──────────────────
    // Intraday:   SL=ATR×1.5  Target=ATR×2   RR≈1.33
    // Swing:      SL=ATR×2.0  Target=ATR×3   RR≈1.50
    // Positional: SL=ATR×2.5  Target=ATR×4   RR≈1.60
    // DMA floor for Positional only (support-based tighter SL = better RR)
    let sl, target;
    if (niftyTradeType.includes("POSITIONAL (Value)")) {
      // Value buy: 50_DMA as floor
      const rawSl = cmp - atr * CONFIG.ATR_SL_POSITIONAL;
      sl     = (dma50 > 0 && dma50 < cmp) ? parseFloat(Math.max(rawSl, dma50).toFixed(2)) : parseFloat(rawSl.toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_POSITIONAL).toFixed(2));
    } else if (niftyTradeType.includes("POSITIONAL")) {
      // Positional: 20_DMA as floor
      const rawSl = cmp - atr * CONFIG.ATR_SL_POSITIONAL;
      sl     = (dma20 > 0 && dma20 < cmp) ? parseFloat(Math.max(rawSl, dma20).toFixed(2)) : parseFloat(rawSl.toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_POSITIONAL).toFixed(2));
    } else if (niftyTradeType.includes("SWING")) {
      sl     = parseFloat((cmp - atr * CONFIG.ATR_SL_SWING).toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_SWING).toFixed(2));
    } else {
      // Intraday
      sl     = parseFloat((cmp - atr * CONFIG.ATR_SL_INTRADAY).toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_INTRADAY).toFixed(2));
    }

    // Safety: SL must be below CMP
    if (sl >= cmp) sl = parseFloat((cmp * 0.97).toFixed(2));

    // ── Sector exposure cap: max 2 stocks per sector across traded + waiting ──
    const sector = (r[1] || "UNKNOWN").toString().trim();
    if ((sectorCount[sector] || 0) >= 2) {
      Logger.log(`[SECTOR SKIP] ${r[0]}: Sector "${sector}" already has ${sectorCount[sector]} positions`);
      continue;
    }

    // ── RR check: enforce minimum 1.3 ──
    const risk   = cmp - sl;
    const reward = target - cmp;
    const rrNum  = (risk > 0) ? (reward / risk) : 0;
    if (rrNum < CONFIG.MIN_RR) {
      Logger.log(`[RR SKIP] ${r[0]}: RR 1:${rrNum.toFixed(1)} < minimum 1:${CONFIG.MIN_RR} | SL ₹${sl} CMP ₹${cmp}`);
      continue;
    }
    const rrStr = "1:" + rrNum.toFixed(1);

    candidates.push({
      priority,
      sector,
      row: [
        nowTime,             // A  Signal Time
        r[0],                // B  Symbol
        "",                  // C  Live Price — VLOOKUP restored
        priority,            // D  Priority Score
        ttype,               // E  Trade Type — from Nifty200 col Y (r[24]) ✅
        signal,              // F  Strategy (FINAL_ACTION)
        r[22] || "",         // G  Breakout Stage
        sl,                  // H  Initial SL — ATR-based ✅
        target,              // I  Target (CMP + ATR×3)
        rrStr,               // J  RR Ratio
        "⏳ WAITING",        // K  Trade Status
        "",                  // L  Entry Price — Python fills when TRADED
        "",                  // M  Entry Time  — Python fills when TRADED
        "",                  // N  Days in Trade — formula
        "",                  // O  Trailing SL  — Python owns
        "",                  // P  P/L%         — formula
        "",                  // Q  ATH Warning  — formula
        "",                  // R  Risk ₹       — formula
        "",                  // S  Position Size — formula
      ]
    });
  }

  // ── Step 3: Sort by priority, fill MAX_WAITING (10) waiting slots ──
  // Sector cap enforced: max 2 total (traded + waiting) per sector
  candidates.sort((a, b) => b.priority - a.priority);
  const waitingSectorCount = Object.assign({}, sectorCount); // copy traded sector counts
  const finalWaiting = [];
  for (const c of candidates) {
    if (finalWaiting.length >= CONFIG.MAX_WAITING) break;
    const sec = c.sector || "UNKNOWN";
    if ((waitingSectorCount[sec] || 0) >= 2) continue;  // sector full
    waitingSectorCount[sec] = (waitingSectorCount[sec] || 0) + 1;
    finalWaiting.push(c.row);
  }
  let   finalGrid    = finalTraded.concat(finalWaiting);

  // Pad to LOG_ROWS rows × TOTAL_COLS cols
  while (finalGrid.length < CONFIG.LOG_ROWS) {
    finalGrid.push(new Array(CONFIG.TOTAL_COLS).fill(""));
  }

  // ── Step 4: Write cols A–S (19 cols). Col T is NEVER touched. ──
  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).clearContent();
  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).setValues(finalGrid);

  // ── Step 5: Restore all formulas ──
  _restoreFormulas(logSheet);

  Logger.log(`[DONE] Traded=${finalTraded.length} | New waiting=${finalWaiting.length}`);
}

// ── FORMULA RESTORE ───────────────────────────────────────────────────────────
// Called after every write. Restores all formula columns.
// Never touches col O (Trailing SL) or col T (System Control).
function _restoreFormulas(logSheet) {
  const endRow = CONFIG.LOG_ROWS + 1; // rows 2 to 16 (LOG_ROWS=15 → endRow=16)

  for (let i = 2; i <= endRow; i++) {
    const sym    = (logSheet.getRange(i, 2).getValue() || "").toString().trim();
    const status = (logSheet.getRange(i, 11).getValue() || "").toString().toUpperCase();
    const traded = _isTraded(status);

    // ── Col C: Live Price VLOOKUP — always restore ──
    if (sym) {
      logSheet.getRange(i, 3).setFormula(
        `=IFERROR(VLOOKUP(B${i},'${CONFIG.SHEET_NAME}'!A:C,3,FALSE),"")`
      );
    } else {
      logSheet.getRange(i, 3).setValue("");
    }

    // ── Col N: Days in Trade ──
    // Only meaningful when Entry Time (col M) is filled = TRADED rows
    // Formula: integer days since entry. Shows "—" for WAITING.
    if (traded && sym) {
      logSheet.getRange(i, 14).setFormula(
        `=IF(M${i}<>"",MAX(0,INT(NOW()-DATEVALUE(TEXT(M${i},"yyyy-mm-dd")))),"—")`
      );
    } else {
      logSheet.getRange(i, 14).setValue("—");
    }

    // ── Col P: P/L % ──
    // Formula: ((LivePrice - EntryPrice) / EntryPrice) × 100
    // Blank for WAITING to avoid #DIV/0 from empty col L
    if (traded && sym) {
      logSheet.getRange(i, 16).setFormula(
        `=IF(AND(L${i}<>"",C${i}<>"",L${i}<>0),ROUND(((C${i}-L${i})/L${i})*100,2),"")`
      );
    } else {
      logSheet.getRange(i, 16).setValue("");
    }

    // ── Col Q: ATH Warning ──
    // 52W_High is column J in Nifty200 = 10th column → VLOOKUP col 10
    // Shows for both WAITING and TRADED rows
    if (sym) {
      logSheet.getRange(i, 17).setFormula(
        `=IF(B${i}="","",IFERROR(` +
        `IF(((VLOOKUP(B${i},'${CONFIG.SHEET_NAME}'!A:J,10,FALSE)-C${i})/` +
        `VLOOKUP(B${i},'${CONFIG.SHEET_NAME}'!A:J,10,FALSE))*100<3,` +
        `"⚠️ NEAR ATH","✅ OK"),"—"))`
      );
    } else {
      logSheet.getRange(i, 17).setValue("");
    }

    // ── Col R: Risk ₹ ──
    // Actual rupees at risk = (Entry - InitialSL) × position size
    // Uses Entry Price (L) if TRADED, CMP (C) if WAITING
    if (sym) {
      logSheet.getRange(i, 18).setFormula(
        `=IF(AND(H${i}<>"",H${i}<>0),` +
        `IF(L${i}<>"",` +
        `ROUND((L${i}-H${i})*ROUND(${CONFIG.CAPITAL}/L${i},0),0),` +
        `IF(C${i}<>"",ROUND((C${i}-H${i})*ROUND(${CONFIG.CAPITAL}/C${i},0),0),"—")),` +
        `"—")`
      );
    } else {
      logSheet.getRange(i, 18).setValue("");
    }

    // ── Col S: Position Size ──
    // Shares to buy = ₹10,000 / Entry Price
    // Uses Entry Price (L) if TRADED, CMP (C) if WAITING
    if (sym) {
      logSheet.getRange(i, 19).setFormula(
        `=IF(L${i}<>"",ROUND(${CONFIG.CAPITAL}/L${i},0),` +
        `IF(C${i}<>"",ROUND(${CONFIG.CAPITAL}/C${i},0),"—"))`
      );
    } else {
      logSheet.getRange(i, 19).setValue("");
    }
  }
}

// ── TRADE TYPE MAPPER ─────────────────────────────────────────────────────────
// Reads Trade_Type already calculated in Nifty200 col Y (r[24]).
// Maps to display label for AlertLog col E.
// Also returns ATR SL multiplier for each type.
//
// Nifty200 col Y values → AlertLog display:
//   "⚡ INTRADAY"            → "⚡ Intraday"      SL: ATR×1.5
//   "🎯 SWING (Breakout)"    → "🔄 Swing"         SL: ATR×2.0
//   "📊 SWING (Trend)"       → "🔄 Swing"         SL: ATR×2.0
//   "💰 POSITIONAL (Value)"  → "📈 Positional"    SL: ATR×2.0 or 50DMA
//   "📈 POSITIONAL (Growth)" → "📈 Positional"    SL: ATR×2.5 or 20DMA
//   High priority + high ATR → "📊 Options Alert" SL: ATR×2.0
function _mapTradeType(niftyType, priority, atr, cmp) {
  const atrPct = (atr / cmp) * 100;
  if (priority >= 28 && atrPct > 2.0) return { ttype: "📊 Options Alert" };
  if (niftyType.includes("INTRADAY"))  return { ttype: "⚡ Intraday"   };
  if (niftyType.includes("SWING"))     return { ttype: "🔄 Swing"      };
  if (niftyType.includes("POSITIONAL"))return { ttype: "📈 Positional" };
  if (priority >= 26) return { ttype: "📈 Positional" };
  if (priority >= 22) return { ttype: "🔄 Swing"      };
  return               { ttype: "⚡ Intraday"          };
}

// ── MORNING CLEANUP ───────────────────────────────────────────────────────────
// Clears WAITING rows. Keeps TRADED rows with all their data intact.
// Preserves Entry Price (L), Entry Time (M), Trailing SL (O) for active trades.
function clearWaitingRowsOnly() {
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.LOG_SHEET);
  const data     = logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();

  // Keep only rows where status = TRADED (not EXITED, not WAITING, not blank)
  const traded = data.filter(r =>
    _isTraded((r[10] || "").toString().toUpperCase())
  );

  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).clearContent();

  if (traded.length > 0) {
    logSheet.getRange(2, 1, traded.length, CONFIG.TOTAL_COLS).setValues(traded);
  }

  // Restore formulas for remaining rows
  _restoreFormulas(logSheet);
  Logger.log(`[MORNING CLEANUP] Kept ${traded.length} active trades. WAITING rows cleared.`);
}

// ── FRESH CLEAN START ─────────────────────────────────────────────────────────
// Use only for full reset. Clears everything including active trades.
function freshCleanStart() {
  const ui       = SpreadsheetApp.getUi();
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.LOG_SHEET);

  const confirm = ui.alert(
    '🧹 FRESH CLEAN START',
    'This will clear ALL rows 2–11 including active TRADED rows.\n\n' +
    '✅ Clears all data (A–S)\n' +
    '✅ Restores all VLOOKUP formulas (col C)\n' +
    '✅ Clears T4 memory string\n' +
    '🔒 T2 automation switch — NOT touched\n\n' +
    'WARNING: Any active trades will be lost from AlertLog.\n' +
    'Make sure History sheet is up to date first.\n\n' +
    'Are you sure?',
    ui.ButtonSet.YES_NO
  );
  if (confirm !== ui.Button.YES) {
    ui.alert('❌ Cancelled. No changes made.');
    return;
  }

  // Clear all 19 cols × 10 rows
  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).clearContent();

  // Restore formulas (VLOOKUP + formula cols)
  _restoreFormulas(logSheet);

  // Clear memory in T4 — resets all Python flags
  // T2 (automation switch YES/NO) is NOT touched
  logSheet.getRange("T4").clearContent();

  ui.alert(
    '✅ FRESH CLEAN COMPLETE\n\n' +
    '• All rows cleared ✅\n' +
    '• Formulas restored ✅\n' +
    '• T4 memory cleared ✅\n' +
    '• T2 switch: untouched ✅\n\n' +
    'Click 🔄 MANUAL SYNC to fill fresh candidates.'
  );
}

// ── WEEKLY SUMMARY ─────────────────────────────────────────────────────────
// Fires every Friday 15:30–15:45 IST automatically.
// Reads History sheet for the week's closed trades.
function sendWeeklySummary() {
  const ss        = SpreadsheetApp.getActiveSpreadsheet();
  const hist      = ss.getSheetByName(CONFIG.HISTORY_SHEET);
  const logSheet  = ss.getSheetByName(CONFIG.LOG_SHEET);
  const now       = new Date();
  const today     = Utilities.formatDate(now, CONFIG.IST_ZONE, "yyyy-MM-dd");

  // Get Mon of this week
  const day  = now.getDay(); // 5=Fri
  const diff = day - 1;      // days since Monday
  const mon  = new Date(now); mon.setDate(now.getDate() - diff);
  const monStr = Utilities.formatDate(mon, CONFIG.IST_ZONE, "yyyy-MM-dd");

  const allHist = hist ? hist.getDataRange().getValues() : [];
  const weekRows = allHist.slice(1).filter(r => r[3] >= monStr && r[3] <= today);

  const wins   = weekRows.filter(r => (r[6] || "").toString().toUpperCase().includes("WIN"));
  const losses = weekRows.filter(r => (r[6] || "").toString().toUpperCase().includes("LOSS"));
  const totalPL = weekRows.reduce((s, r) => s + (parseFloat(r[16]) || 0), 0);
  const winRate = weekRows.length > 0 ? Math.round((wins.length / weekRows.length) * 100) : 0;

  // Best and worst trade
  let best = null, worst = null;
  for (const r of weekRows) {
    const pl = parseFloat(r[16]) || 0;
    if (!best  || pl > (parseFloat(best[16])  || 0)) best  = r;
    if (!worst || pl < (parseFloat(worst[16]) || 0)) worst = r;
  }

  // Open trades P/L
  const logData = logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();
  const openTrades = logData.filter(r => _isTraded((r[10] || "").toString().toUpperCase()));

  let msg = `📅 <b>WEEKLY REPORT — w/e ${today}</b>\n` +
            `━━━━━━━━━━━━━━━━━━━━\n` +
            `📊 Trades: ${weekRows.length} | ✅ Wins: ${wins.length} | ❌ Losses: ${losses.length}\n` +
            `🎯 Win Rate: ${winRate}%\n` +
            `💰 Weekly P/L: <b>₹${totalPL >= 0 ? '+' : ''}${Math.round(totalPL).toLocaleString()}</b>\n`;

  if (best)  msg += `🏆 Best:  <b>${best[0]}</b> ${best[5]} = ₹${Math.round(parseFloat(best[16]) || 0)}\n`;
  if (worst) msg += `💀 Worst: <b>${worst[0]}</b> ${worst[5]} = ₹${Math.round(parseFloat(worst[16]) || 0)}\n`;

  msg += `\n📌 Open positions: ${openTrades.length}/${CONFIG.MAX_TRADES}`;

  _sendTelegram(msg);
  Logger.log(`[WEEKLY] Sent weekly summary — ${weekRows.length} trades this week`);
}

// ── HELPERS ───────────────────────────────────────────────────────────────────
function _isTraded(status) {
  const s = status.toString().toUpperCase();
  return s.includes("TRADED") && !s.includes("EXITED");
}

function _isWaiting(status) {
  return status.toString().toUpperCase().includes("WAITING");
}

// ── TELEGRAM ─────────────────────────────────────────────────────────────────
function _sendTelegram(msg) {
  try {
    UrlFetchApp.fetch(
      `https://api.telegram.org/bot${CONFIG.TELEGRAM_TOKEN}/sendMessage`,
      {
        method      : "post",
        contentType : "application/json",
        payload     : JSON.stringify({
          chat_id    : CONFIG.CHAT_ID,
          text       : msg,
          parse_mode : "HTML"
        })
      }
    );
  } catch (e) {
    Logger.log("Telegram error: " + e.toString());
  }
}
