from flask import Flask, render_template

from PE import compute_sp500_graham_screen
from Cad import compute_tsx60_graham_screen

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sp500')
def sp500():
    df, df_pass = compute_sp500_graham_screen()
    return render_template(
        'results.html',
        title='S&P 500 Graham Screen',
        full=df.to_html(classes='data'),
        passed=df_pass.to_html(classes='data')
    )


@app.route('/tsx60')
def tsx60():
    df, df_pass = compute_tsx60_graham_screen()
    return render_template(
        'results.html',
        title='S&P/TSX 60 Graham Screen',
        full=df.to_html(classes='data'),
        passed=df_pass.to_html(classes='data')
    )


if __name__ == '__main__':
    app.run(debug=True)
