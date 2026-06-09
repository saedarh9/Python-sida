"""
Swing trading-strategi: RSI(2) mean reversion med trendfilter.

Regler (long-only):
  KÖP  nästa dags öppning när:  RSI(2) < 10  OCH  stängning > SMA(200)
  SÄLJ nästa dags öppning när:  RSI(2) > 70  ELLER  positionen hållits 10 dagar

Strategin handlar typiskt 1-4 gånger i månaden per ticker. Kör den på
3-5 tickers samtidigt så får du i snitt minst en trade i veckan.

Körning:
  python strategy.py --ticker AAPL            # riktig data via yfinance
  python strategy.py --ticker AAPL MSFT SPY   # flera tickers
  python strategy.py --csv mindata.csv        # egen CSV (Date,Open,High,Low,Close)
  python strategy.py --demo                   # syntetisk demodata (offline)

OBS: Detta är ett utbildningsverktyg för backtesting. Historisk avkastning
är ingen garanti för framtida resultat. Handla aldrig för pengar du inte
har råd att förlora.
"""

import argparse
import sys

import numpy as np
import pandas as pd

# Strategiparametrar
RSI_PERIOD = 2
RSI_BUY = 10        # köp när RSI(2) är under denna nivå (översålt)
RSI_SELL = 70       # sälj när RSI(2) är över denna nivå
TREND_SMA = 200     # handla bara i riktning med långsiktig trend
MAX_HOLD_DAYS = 10  # tidsstopp: sälj efter max så här många dagar
COMMISSION = 0.001  # courtage per affär (0,1 % per sida)


def rsi(close: pd.Series, period: int) -> pd.Series:
    """Relative Strength Index (Wilder-utjämning)."""
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def load_yfinance(ticker: str, start: str) -> pd.DataFrame:
    import yfinance as yf

    df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if df.empty:
        raise RuntimeError(f"Ingen data för {ticker} (nätverk blockerat eller okänd ticker)")
    return df[["Open", "High", "Low", "Close"]]


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    return df[["Open", "High", "Low", "Close"]]


def generate_demo_data(days: int = 2500, seed: int = 42) -> pd.DataFrame:
    """Syntetisk aktiekurs med trend, mean reversion och volatilitetskluster,
    så att backtesten kan demonstreras utan internetuppkoppling."""
    rng = np.random.default_rng(seed)
    drift = 0.0006
    vol = 0.011 * (1 + 0.4 * np.sin(np.linspace(0, 20, days)) ** 2)
    shocks = rng.normal(drift, vol)
    # lätt negativ autokorrelation gör att översålda lägen tenderar att studsa,
    # vilket är det beteende i riktiga index som strategin utnyttjar
    returns = shocks - 0.15 * np.concatenate([[0], shocks[:-1]])
    close = 100 * np.exp(np.cumsum(returns))
    gap = rng.normal(0, 0.003, days)
    open_ = np.concatenate([[100.0], close[:-1]]) * (1 + gap)
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.004, days)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.004, days)))
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close}, index=dates)


def backtest(df: pd.DataFrame, name: str) -> dict:
    """Backtestar strategin på OHLC-data. Order läggs på signaldagens
    stängning och fylls på NÄSTA dags öppning (ingen lookahead-bias)."""
    df = df.copy()
    df["rsi"] = rsi(df["Close"], RSI_PERIOD)
    df["sma"] = df["Close"].rolling(TREND_SMA).mean()

    trades = []
    in_position = False
    entry_price = entry_date = None
    hold_days = 0

    for i in range(TREND_SMA, len(df) - 1):
        row = df.iloc[i]
        next_open = df["Open"].iloc[i + 1]
        next_date = df.index[i + 1]

        if not in_position:
            if row["rsi"] < RSI_BUY and row["Close"] > row["sma"]:
                entry_price = next_open * (1 + COMMISSION)
                entry_date = next_date
                in_position, hold_days = True, 0
        else:
            hold_days += 1
            if row["rsi"] > RSI_SELL or hold_days >= MAX_HOLD_DAYS:
                exit_price = next_open * (1 - COMMISSION)
                trades.append({
                    "entry_date": entry_date, "exit_date": next_date,
                    "entry": entry_price, "exit": exit_price,
                    "return_pct": (exit_price / entry_price - 1) * 100,
                    "days_held": hold_days,
                })
                in_position = False

    return summarize(trades, df, name)


def summarize(trades: list, df: pd.DataFrame, name: str) -> dict:
    if not trades:
        print(f"\n{name}: inga trades genererades (för lite data?)")
        return {"name": name, "trades": []}

    t = pd.DataFrame(trades)
    returns = t["return_pct"] / 100
    equity = (1 + returns).cumprod()
    wins = returns[returns > 0]
    losses = returns[returns <= 0]
    weeks = (df.index[-1] - df.index[TREND_SMA]).days / 7
    bh = df["Close"].iloc[-1] / df["Close"].iloc[TREND_SMA] - 1
    peak = equity.cummax()
    max_dd = ((equity - peak) / peak).min()
    profit_factor = wins.sum() / abs(losses.sum()) if len(losses) and losses.sum() != 0 else float("inf")

    print(f"\n{'=' * 52}\n  {name}\n{'=' * 52}")
    print(f"  Antal trades:        {len(t)}")
    print(f"  Trades per vecka:    {len(t) / weeks:.2f}")
    print(f"  Träffsäkerhet:       {len(wins) / len(t) * 100:.1f} %")
    print(f"  Snittvinst:          {wins.mean() * 100:+.2f} %" if len(wins) else "  Snittvinst:          -")
    print(f"  Snittförlust:        {losses.mean() * 100:+.2f} %" if len(losses) else "  Snittförlust:        -")
    print(f"  Profit factor:       {profit_factor:.2f}")
    print(f"  Total avkastning:    {(equity.iloc[-1] - 1) * 100:+.1f} %")
    print(f"  Max drawdown:        {max_dd * 100:.1f} %")
    print(f"  Köp & behåll (jmf):  {bh * 100:+.1f} %")
    print(f"\n  Senaste 5 trades:")
    for _, tr in t.tail(5).iterrows():
        print(f"    {tr['entry_date'].date()} -> {tr['exit_date'].date()}"
              f"  {tr['return_pct']:+6.2f} %  ({tr['days_held']} dagar)")
    return {"name": name, "trades": trades, "total_return": equity.iloc[-1] - 1}


def current_signal(df: pd.DataFrame, name: str) -> None:
    """Visar om strategin ger köpsignal på senaste stängningen."""
    r = rsi(df["Close"], RSI_PERIOD).iloc[-1]
    sma = df["Close"].rolling(TREND_SMA).mean().iloc[-1]
    close = df["Close"].iloc[-1]
    if r < RSI_BUY and close > sma:
        print(f"  >>> {name}: KÖPSIGNAL nu (RSI2={r:.1f}, kurs {close:.2f} > SMA200 {sma:.2f})")
    else:
        print(f"  {name}: ingen signal (RSI2={r:.1f}, kurs {close:.2f}, SMA200 {sma:.2f})")


def main() -> None:
    p = argparse.ArgumentParser(description="Backtest av RSI(2) mean reversion-strategi")
    p.add_argument("--ticker", nargs="+", help="t.ex. AAPL MSFT SPY eller VOLV-B.ST")
    p.add_argument("--csv", help="sökväg till CSV med kolumnerna Date,Open,High,Low,Close")
    p.add_argument("--demo", action="store_true", help="kör på syntetisk demodata (offline)")
    p.add_argument("--start", default="2015-01-01", help="startdatum för historik")
    args = p.parse_args()

    datasets = []
    if args.demo:
        datasets.append(("DEMO (syntetisk data)", generate_demo_data()))
    elif args.csv:
        datasets.append((args.csv, load_csv(args.csv)))
    elif args.ticker:
        for tk in args.ticker:
            try:
                datasets.append((tk, load_yfinance(tk, args.start)))
            except Exception as e:
                print(f"Kunde inte hämta {tk}: {e}", file=sys.stderr)
    else:
        p.error("ange --ticker, --csv eller --demo")

    if not datasets:
        sys.exit("Ingen data kunde laddas.")

    for name, df in datasets:
        backtest(df, name)

    print(f"\n{'=' * 52}\n  Aktuella signaler\n{'=' * 52}")
    for name, df in datasets:
        current_signal(df, name)
    print("\nOBS: Backtest på historisk data. Inga garantier för framtida resultat.")


if __name__ == "__main__":
    main()
