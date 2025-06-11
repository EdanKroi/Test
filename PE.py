import pandas as pd
import yfinance as yf

def main():
    # 1) Fetch S&P 500 table
    wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500_df = pd.read_html(wiki_url, header=0)[0]

    # 2) Collapse any remaining classes by company base name
    sp500_df['Base'] = sp500_df['Security'].str.replace(r"\s+Class.*$", "", regex=True)
    sp500_df = sp500_df.drop_duplicates(subset='Base', keep='first')

    # 3) Remove share-class tickers by symbol punctuation
    sp500_df = sp500_df[~sp500_df['Symbol'].str.contains(r"[\.-]")]

    # 4) Extract cleaned ticker list
    tickers = sp500_df['Symbol'].tolist()
    print(f"Total tickers after cleaning: {len(tickers)}")  # should print 500

    # 5) Fetch P/E, P/B and compute Graham product (only if P/B > 0)
    data = []
    for symbol in tickers:
        try:
            info = yf.Ticker(symbol).info
            pe = info.get('trailingPE')
            pb = info.get('priceToBook')
            # Only compute and flag if pb > 0
            if pe is not None and pb is not None and pb > 0:
                product = pe * pb
                passes = (product <= 22.5)
            else:
                product = None
                passes = None
        except Exception:
            pe = pb = product = None
            passes = None

        data.append({
            'Ticker':       symbol,
            'P/E (TTM)':    pe,
            'P/B (mrq)':    pb,
            'P/E×P/B':      product,
            'Passes ≤22.5': passes
        })

    # 6) Build DataFrame
    df = pd.DataFrame(data).set_index('Ticker')

    # 7) Remove entries with non-positive P/B
    df = df[df['P/B (mrq)'] > 0]

    # 8) Display all rows
    pd.set_option('display.max_rows', len(df))
    print("\nAll companies with P/B > 0:\n", df)

    # 9) Filter and display only passing companies
    df_pass = df[df['Passes ≤22.5'] == True]
    print("\nCompanies passing Graham's screen (P/E×P/B ≤ 22.5):\n", df_pass)
    print(f"\nTotal passing companies: {len(df_pass)}")

    # 10) Export full and filtered lists to CSV
    df.to_csv('sp500_graham_screen.csv')
    df_pass.to_csv('sp500_graham_screen_pass.csv')

if __name__ == '__main__':
    main()
