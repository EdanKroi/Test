import pandas as pd
import yfinance as yf


def compute_tsx60_graham_screen():
    """Return full and passing Graham screen DataFrames for the S&P/TSX 60."""
    wiki_url = "https://en.wikipedia.org/wiki/S%26P/TSX_60"
    tables = pd.read_html(wiki_url, header=0)

    tsx_df = None
    for t in tables:
        cols = [str(c).lower() for c in t.columns]
        if 'symbol' in cols and 'company' in cols:
            tsx_df = t.copy()
            break
    if tsx_df is None:
        raise ValueError("Could not find TSX 60 constituents table with 'Symbol' & 'Company' columns")

    symbol_col = next(c for c in tsx_df.columns if str(c).lower() in ('symbol', 'ticker'))
    company_col = next(c for c in tsx_df.columns if 'company' in str(c).lower())
    sector_col = next((c for c in tsx_df.columns if 'gics' in str(c).lower() or 'sector' in str(c).lower()), None)

    tsx_df = tsx_df[[symbol_col, company_col] + ([sector_col] if sector_col else [])].copy()
    tsx_df.rename(columns={symbol_col: 'Ticker', company_col: 'Company', sector_col: 'Sector'} if sector_col else {symbol_col: 'Ticker', company_col: 'Company'}, inplace=True)
    tsx_df['Ticker'] = tsx_df['Ticker'].astype(str).str.strip() + '.TO'

    tickers = tsx_df['Ticker'].tolist()

    data = []
    for symbol in tickers:
        try:
            info = yf.Ticker(symbol).info
            pe = info.get('trailingPE')
            pb = info.get('priceToBook')
            if pe is not None and pb is not None and pb > 0:
                product = pe * pb
                passes = (product <= 22.5)
            else:
                product = None
                passes = None
        except Exception:
            pe = pb = product = None
            passes = None

        entry = {
            'Ticker':       symbol,
            'Company':      tsx_df.loc[tsx_df['Ticker'] == symbol, 'Company'].values[0],
            'P/E (TTM)':    pe,
            'P/B (mrq)':    pb,
            'P/E×P/B':      product,
            'Passes ≤22.5': passes
        }
        if 'Sector' in tsx_df.columns:
            entry['Sector'] = tsx_df.loc[tsx_df['Ticker'] == symbol, 'Sector'].values[0]
        data.append(entry)

    df = pd.DataFrame(data).set_index('Ticker')
    df = df[df['P/B (mrq)'] > 0]
    df_pass = df[df['Passes ≤22.5'] == True]
    return df, df_pass


def main():
    df, df_pass = compute_tsx60_graham_screen()

    pd.set_option('display.max_rows', len(df))
    print("\nAll TSX 60 companies with P/B > 0:\n", df)
    print("\nCompanies passing Graham's screen (P/E×P/B ≤ 22.5):\n", df_pass)
    print(f"\nTotal passing companies: {len(df_pass)}")

    df.to_csv('tsx60_graham_screen.csv')
    df_pass.to_csv('tsx60_graham_screen_pass.csv')


if __name__ == '__main__':
    main()
