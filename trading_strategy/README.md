# Swing trading-strategi: RSI(2) mean reversion

En komplett, backtestbar tradingstrategi i Python som ger dig konkreta
köp- och säljsignaler ungefär en gång i veckan eller oftare.

## Strategin i korthet

Strategin bygger på en av de mest väldokumenterade effekterna på börsen:
**kortsiktig mean reversion** — aktier och index som fallit kraftigt på
några dagar tenderar att studsa tillbaka, *så länge den långsiktiga trenden
pekar uppåt*.

Reglerna (long-only):

| Regel | Villkor |
|---|---|
| **KÖP** | RSI(2) < 10 (kraftigt översålt) **och** stängningskurs > 200-dagars glidande medelvärde |
| **SÄLJ** | RSI(2) > 70 (studsen har kommit) **eller** positionen hållits 10 handelsdagar |

Ordern läggs på signaldagens stängning och fylls på nästa dags öppning —
backtesten innehåller alltså ingen lookahead-bias, och courtage på 0,1 %
per sida är inräknat.

## Så får du minst en trade i veckan

En enskild ticker ger typiskt 1–4 signaler per månad. Kör strategin på
3–5 likvida tickers samtidigt (t.ex. indexfonder/ETF:er och stora bolag)
så landar du i snitt på en trade i veckan eller mer:

```bash
pip install yfinance pandas numpy

# Amerikanska tickers
python strategy.py --ticker SPY QQQ AAPL MSFT

# Svenska aktier (Stockholmsbörsen har suffixet .ST)
python strategy.py --ticker VOLV-B.ST INVE-B.ST ERIC-B.ST

# Utan internet / med egen data
python strategy.py --demo
python strategy.py --csv mindata.csv   # kolumner: Date,Open,High,Low,Close
```

Skriptet visar för varje ticker: antal trades, trades per vecka,
träffsäkerhet, profit factor, total avkastning, max drawdown, jämförelse
mot köp & behåll — och om det finns en **köpsignal just nu**.

## Hur du använder det i praktiken

1. **Backtesta först.** Kör skriptet på de tickers du vill handla och
   minst 8–10 års historik. Handla inget som inte ser bra ut historiskt
   (profit factor > 1,3 och en drawdown du tål är en rimlig miniminivå).
2. **Kör skriptet varje kväll efter börsens stängning.** Får du en
   köpsignal lägger du ordern till nästa dags öppning.
3. **Riskera lite per trade.** En vanlig tumregel är max 1–2 % av kapitalet
   i risk per position. Aldrig belåning när du börjar.
4. **Följ reglerna mekaniskt.** Strategins värde ligger i att den tar bort
   känslor — om du börjar avvika från reglerna har du ingen strategi längre.
5. **För journal.** Logga varje trade och jämför mot backtesten. Avviker
   verkligheten kraftigt — sluta och utvärdera.

## Ärliga ord om att "tjäna på börsen"

- **Ingen strategi garanterar vinst.** Den här typen av mean reversion har
  fungerat historiskt på indexnivå, men alla strategier har förlustperioder
  och kan sluta fungera.
- **Fler trades ≠ mer vinst.** Courtage och spread äter avkastning. Att du
  *vill* ha en trade i veckan är ett aktivitetsmål, inte ett vinstmål —
  låt strategin styra, inte rastlösheten.
- **Det som faktiskt avgör långsiktigt resultat** är riskhantering och
  disciplin, inte signalen i sig.
- Börja gärna med **papper/demo-konto i 2–3 månader** innan du sätter in
  riktiga pengar.

Detta är ett utbildningsverktyg och inte finansiell rådgivning. Handla
aldrig för pengar du inte har råd att förlora.
