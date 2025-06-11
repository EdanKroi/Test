import pandas as pd
import yfinance as yf


def compute_sp500_graham_screen():
    """Return full and passing Graham screen DataFrames for the S&P 500."""
    wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500_df = pd.read_html(wiki_url, header=0)[0]
    sp500_df['Base'] = sp500_df['Security'].str.replace(r"\s+Class.*$", "", regex=True)
    sp500_df = sp500_df.drop_duplicates(subset='Base', keep='first')
    sp500_df = sp500_df[~sp500_df['Symbol'].str.contains(r"[\.-]")]
    tickers = sp500_df['Symbol'].tolist()

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

        data.append({
            'Ticker':       symbol,
            'P/E (TTM)':    pe,
            'P/B (mrq)':    pb,
            'P/E×P/B':      product,
            'Passes ≤22.5': passes
        })

    df = pd.DataFrame(data).set_index('Ticker')
    df = df[df['P/B (mrq)'] > 0]
    df_pass = df[df['Passes ≤22.5'] == True]
    return df, df_pass


def main():
    df, df_pass = compute_sp500_graham_screen()

    pd.set_option('display.max_rows', len(df))
    print("\nAll companies with P/B > 0:\n", df)
    print("\nCompanies passing Graham's screen (P/E×P/B ≤ 22.5):\n", df_pass)
    print(f"\nTotal passing companies: {len(df_pass)}")

    df.to_csv('sp500_graham_screen.csv')
    df_pass.to_csv('sp500_graham_screen_pass.csv')


if __name__ == '__main__':
    main()
