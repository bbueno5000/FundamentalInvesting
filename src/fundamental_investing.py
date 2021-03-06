import datetime
import matplotlib
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as pyplot
import matplotlib.ticker as mpl_ticker
import mpl_finance
import numpy
import pylab
import time
import urllib.request

matplotlib.rcParams.update({'font.size': 9})

even_better = ['AWH', 'AFAM', 'ACAS', 'ASI', 'NLY', 'ANH', 'AIZ', 'AXS', 'BHLB', 'COF', 'CMO', 'DYN', 'FDEF', 'HMN', 'IM', 'IRDM', 'KMPR', 'LNC', 'LMIA', 'MANT', 'MCGC', 'MRH', 'MVC', 'NAVG', 'OVTI', 'PRE', 'PMC', 'PJC', 'PTP', 'BPOP', 'PL', 'RF', 'SKYW', 'STI', 'SPN', 'SYA', 'TECD', 'TSYS', 'TITN', 'TPC', 'UNM', 'VOXX', 'XL']

class ChartingStocks:

    def compute_macd(self, x, slow=26, fast=12):
            """
            Compute MACD using a fast and slow exponential moving average.

            Definitions:
                macd - moving average convergence/divergence
                macd line = 12 ema - 26 ema
                signal line = 9 ema of macd line
                histogram = macd line - signal line
        
            Returns:
                len(x) arrays: value is emaslow, emafast, macd
            """
            exponential_moving_average_slow = self.exponential_moving_average(x, slow)
            exponential_moving_average_fast = self.exponential_moving_average(x, fast)
            return (
                exponential_moving_average_slow, 
                exponential_moving_average_fast, 
                exponential_moving_average_fast - exponential_moving_average_slow
                )

    def exponential_moving_average(self, values, window):
        weights = numpy.exp(numpy.linspace(-1.0, 0.0, window))
        weights /= weights.sum()
        exponential_moving_average = numpy.convolve(
            values, 
            weights, 
            mode='full'
            )[:len(values)]
        exponential_moving_average[:window] = exponential_moving_average[window]
        return exponential_moving_average

    def graph_data(self, ticker_symbol, moving_average_1, moving_average_2):
        try:
            revenue_date, revenue, return_on_capital_date, return_on_capital, income_date, income = FundamentalInvesting().grab_quandl(ticker_symbol)
            print(str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
            url_to_visit = (
                'http://chartapi.finance.yahoo.com/instrument/1.0/' 
                + ticker_symbol 
                + '/chartdata;type=quote;range=10y/csv'
                )
            ticker_symbol_file = []
            try:
                source_code = urllib.request.urlopen(url_to_visit).read().decode()
                split_source = source_code.split('\n')
                for each_line in split_source:
                    split_line = each_line.split(',')
                    if len(split_line) == 6:
                        if 'values' not in each_line:
                            ticker_symbol_file.append(each_line)
            except Exception as exception:
                print(str(exception), ':Failed to organize pulled data.')
        except Exception as exception:
            print(str(exception), ':Failed to pull pricing data')
            date, close_price, high_price, low_price, open_price, volume = numpy.loadtxt(
                ticker_symbol_file, 
                delimiter=',', 
                unpack=True, 
                converters={0: mpl_dates.strpdate2num('%Y%m%d')}
                )
            x = 0
            y = len(date)
            candle_args = []
            while x < y:
                append_line = (
                    date[x], 
                    open_price[x], 
                    close_price[x], 
                    high_price[x], 
                    low_price[x], 
                    volume[x]
                    )
                candle_args.append(append_line)
                x += 1
            average_1 = self.moving_average(close_price, moving_average_1)
            average_2 = self.moving_average(close_price, moving_average_2)
            starting_point = len(date[moving_average_2-1:])
            label_1 = str(moving_average_1) + ' SMA'
            label_2 = str(moving_average_2) + ' SMA'
            figure = pyplot.figure(facecolor='#07000D')
            # axis 1
            axis_1 = pyplot.subplot2grid((9,4), (1,0), rowspan=4, colspan=4, axisbg='#07000D')
            mpl_finance.candlestick_ohlc(
                axis_1, 
                candle_args[-starting_point:], 
                width=0.6, 
                colorup='#53C156', 
                colordown='#FF1717'
                )
            axis_1.plot(
                date[-starting_point:], 
                average_1[-starting_point:], 
                '#E1EDF9', 
                label=label_1, 
                linewidth=1.5
                )
            axis_1.plot(
                date[-starting_point:], 
                average_2[-starting_point:], 
                '#4EE6FD', 
                label=label_2, 
                linewidth=1.5
                )
            axis_1.xaxis.set_major_locator(mpl_ticker.MaxNLocator(10))
            axis_1.xaxis.set_major_formatter(mpl_dates.DateFormatter('%Y-%m-%d'))
            pyplot.gca().yaxis.set_major_locator(mpl_ticker.MaxNLocator(prune='upper'))
            axis_1.grid(True, color='w')
            axis_1.yaxis.label.set_color('w')
            axis_1.spines['bottom'].set_color('#5998FF')
            axis_1.spines['top'].set_color('#5998FF')
            axis_1.spines['left'].set_color('#5998FF')
            axis_1.spines['right'].set_color('#5998FF')
            axis_1.tick_params(axis='x', colors='w')
            axis_1.tick_params(axis='y', colors='w')
            pyplot.ylabel('Stock Price And Volume')
            ma_legend = pyplot.legend(fancybox=True, loc=9, ncol=2, prop={'size': 7})
            ma_legend.get_frame().set_alpha(0.4)
            text_ed = pylab.gca().get_legend().get_texts()
            pylab.setp(text_ed[0:5], color='w')
            # axis 0
            axis_0 = pyplot.subplot2grid(
                (9,4), 
                (0,0), 
                sharex=axis_1, 
                rowspan=1, 
                colspan=4, 
                axisbg='#07000D'
                )
            relative_strength_index = self.relative_strength_index(close_price)
            relative_strength_index_color = '#1A8782'
            positive_color = '#386D13'
            negative_color = '#8F2020'
            axis_0.plot(
                date[-starting_point:], 
                relative_strength_index[-starting_point:], 
                relative_strength_index_color, 
                linewidth=1.5
                )
            axis_0.axhline(70, color=negative_color)
            axis_0.axhline(30, color=positive_color)
            axis_0.fill_between(
                date[-starting_point:],
                relative_strength_index[-starting_point:], 
                70, 
                where=(relative_strength_index[-starting_point:]>=70), 
                facecolor=negative_color, 
                edgecolor=negative_color
                )
            axis_0.fill_between(
                date[-starting_point:], 
                relative_strength_index[-starting_point:], 
                30, 
                where=(relative_strength_index[-starting_point:]<=30), 
                facecolor=positive_color, 
                edgecolor=negative_color
                )
            axis_0.spines['bottom'].set_color('#5998ff')
            axis_0.spines['top'].set_color('#5998ff')
            axis_0.spines['left'].set_color('#5998ff')
            axis_0.spines['right'].set_color('#5998ff')
            axis_0.text(
                0.015, 
                0.95, 
                'RSI (14)', 
                va='top', 
                color='w', 
                transform=axis_0.transAxes
                )
            axis_0.tick_params(axis='x', colors='w')
            axis_0.tick_params(axis='y', colors='w')
            axis_0.set_yticks([30, 70])
            # axis 1 volume
            volume_minimum = 0
            axis_1_volume = axis_1.twinx()
            axis_1_volume.fill_between(
                date[-starting_point:], 
                volume_minimum, 
                volume[-starting_point:], 
                facecolor='#00ffe8', 
                alpha=0.5
                )
            axis_1_volume.axes.yaxis.set_ticklabels([])
            axis_1_volume.grid(False)
            axis_1_volume.spines['bottom'].set_color('#5998ff')
            axis_1_volume.spines['top'].set_color('#5998ff')
            axis_1_volume.spines['left'].set_color('#5998ff')
            axis_1_volume.spines['right'].set_color('#5998ff')
            axis_1_volume.set_ylim(0, 2*volume.max())
            axis_1_volume.tick_params(axis='x', colors='w')
            axis_1_volume.tick_params(axis='y', colors='w')
            # axis 2
            axis_2 = pyplot.subplot2grid(
                (9, 4), 
                (5, 0), 
                sharex=axis_1, 
                rowspan=1, 
                colspan=4, 
                axisbg='#07000d'
                )
            fill_color = '#00ffe8'
            num_slow = 26
            num_fast = 12
            num_ema = 9
            ema_slow, ema_fast, macd = self.compute_macd(close_price)
            ema9 = self.exponential_moving_average(macd, num_ema)
            axis_2.plot(date[-starting_point:], macd[-starting_point:], color='#4EE6FD', lw=2)
            axis_2.plot(date[-starting_point:], ema9[-starting_point:], cplor='#E1EDF9', lw=1)
            axis_2.text(
                0.015, 
                0.95, 
                'MACD 12, 26, 9', 
                va='top', 
                color='w', 
                transform=axis_2.transAxes
                )
            axis_2.fill_between(
                date[-starting_point:], 
                macd[-starting_point:] - ema9[-starting_point:], 
                0, 
                alpha=0.5, 
                facecolor=fill_color, 
                edgecolor=fill_color
                )
            axis_2.spines['bottom'].set_color('#5998ff')
            axis_2.spines['top'].set_color('#5998ff')
            axis_2.spines['left'].set_color('#5998ff')
            axis_2.spines['right'].set_color('#5998ff')
            axis_2.tick_params(axis='x', colors='w')
            axis_2.tick_params(axis='y', colors='w')
            pyplot.gca().yaxis.set_major_locator(mpl_ticker.MaxNLocator(prune='upper'))
            axis_2.yaxis.set_major_locator(mpl_ticker.MaxNLocator(nbins=5, prune='upper'))
            # axis 3
            axis_3 = pyplot.subplot2grid(
                (9,4), 
                (6,0), 
                sharex=axis_1, 
                rowspan=1, 
                colspan=4, 
                axisbg='#07000d'
                )
            axis_3.spines['bottom'].set_color("#5998ff")
            axis_3.spines['top'].set_color("#5998ff")
            axis_3.spines['left'].set_color("#5998ff")
            axis_3.spines['right'].set_color("#5998ff")
            axis_3.tick_params(axis='x', colors='w')
            axis_3.tick_params(axis='y', colors='w')
            axis_3.plot(income_date, income, '#4ee6FD')
            pyplot.plot('N.I.', color='w')
            axis_3.grid(True, color='w')
            axis_3.yaxis.set_major_locator(
                mpl_ticker.MaxNLocator(nbins=4, prune='upper')
                )
            #axis 4
            axis_4 = pyplot.subplot2grid(
                (9,4), 
                (7,0), 
                sharex=axis_1, 
                rowspan=1, 
                colspan=4, 
                axisbg='#07000d'
                )
            axis_4.spines['bottom'].set_color("#5998ff")
            axis_4.spines['top'].set_color("#5998ff")
            axis_4.spines['left'].set_color("#5998ff")
            axis_4.spines['right'].set_color("#5998ff")
            axis_4.tick_params(axis='x', colors='w')
            axis_4.tick_params(axis='y', colors='w')
            axis_4.plot(revenue_date, revenue, '#4ee6FD')
            pyplot.plot('Rev.', color='w')
            axis_4.grid(True, color='w')
            axis_4.yaxis.set_major_locator(
                mpl_ticker.MaxNLocator(nbins=4, prune='upper')
                )
            # axis 5
            axis_5 = pyplot.subplot2grid(
                (9,4), 
                (8,0), 
                sharex=axis_1, 
                rowspan=1, 
                colspan=4, 
                axisbg='#07000d'
                )
            axis_5.spines['bottom'].set_color("#5998ff")
            axis_5.spines['top'].set_color("#5998ff")
            axis_5.spines['left'].set_color("#5998ff")
            axis_5.spines['right'].set_color("#5998ff")
            axis_5.tick_params(axis='x', colors='w')
            axis_5.tick_params(axis='y', colors='w')
            axis_5.plot(return_on_capital_date, return_on_capital, '#4ee6FD')
            pyplot.plot('R.O.C.', color='w')
            axis_5.grid(True, color='w')
            axis_5.yaxis.set_major_locator(
                mpl_ticker.MaxNLocator(nbins=4, prune='upper')
                )
            for label in axis_5.xaxis.get_ticklabels():
                label.set_rotation(45)
            # super
            pyplot.suptitle(ticker_symbol, color='w')
            pyplot.setp(axis_0.get_xticklabels(), visible=False)
            pyplot.setp(axis_1.get_xticklabels(), visible=False)
            pyplot.setp(axis_2.get_xticklabels(), visible=False)
            pyplot.setp(axis_3.get_xticklabels(), visible=False)
            pyplot.setp(axis_4.get_xticklabels(), visible=False)
            axis_1.annotate(
                'Big News!', 
                (date[510], average_1[520]), 
                xytext=(0.8, 0.8), 
                textcoords='axes fraction',
                arrowprops=dict(facecolor='white', shrink=0.05),
                fontsize='14',
                color='w',
                horizontalalignment='right', 
                verticalalignment='bottom'
                )
            pyplot.subplots_adjust(
                left=0.9, 
                bottom=0.14, 
                right=0.94, 
                top=0.95, 
                wspace=0.2, 
                hspace=0
                )
            pyplot.show()
            figure.savefig('example.png', facecolor=figure.get_facecolor())
        except Exception as e:
            print('main loop', str(e))

    def moving_average(self, values, window):
        weights = numpy.repeat(1.0, window) / window
        smas = numpy.convolve(values, weights, 'valid')
        return smas

    def relative_strength_index(self, prices, n=14):
        deltas = numpy.diff(prices)
        seed = deltas[:n+1]
        up = seed[seed>=0].sum() / n
        down = -seed[seed<0].sum() / n
        relative_strength = up / down
        relative_strength_index = numpy.zeros_like(prices)
        relative_strength_index[:n] = 100.0 - 100.0 / (1.0 + relative_strength)
        for i in range(n, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                up_value = delta
                down_value = 0.0
            else:
                up_value = 0.0
                down_value = -delta
            up = (up * (n-1) + up_value) / n
            down = (down * (n-1) + down_value) / n
            relative_strength = up / down
            relative_strength_index[i] = 100.0 - 100.0 / (1.0 + relative_strength)
        return relative_strength_index

class FundamentalInvesting:

    def grab_quandl(self, ticker_symbol):
        net_income_array = []
        revenue_array = []
        return_on_capital_array = []
        end_link = 'sort_order=asc'
        try:
            net_income = urllib.request.urlopen(
                'http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_' 
                + ticker_symbol.upper() 
                + '_NET_INC.csv?&' + end_link
                ).read()
            revenue = urllib.request.urlopen(
                'http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_' 
                + ticker_symbol.upper() 
                + '_REV_LAST.csv?&' + end_link
                ).read()
            return_on_capital = urllib.request.urlopen(
                'http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_' 
                + ticker_symbol.upper() 
                + '_ROC.csv?&' + end_link
                ).read()
            split_net_income = net_income.split('\n')
            print('Net Income:')
            for each_net_income in split_net_income[1:-1]:
                print(each_net_income)
                net_income_array.append(each_net_income)
            print('___________')
            split_revenue = revenue.split('\n')
            print('Revenue:')
            for each_revenue in split_revenue[1:-1]:
                print(each_revenue)
                revenue_array.append(each_revenue)
            print('___________')
            split_return_on_capital = return_on_capital.split('\n')
            print('Return On Capital:')
            for each_return_on_capital in split_return_on_capital[1:-1]:
                print(each_return_on_capital)
                return_on_capital_array.append(each_return_on_capital)
            income_date, income = numpy.loadtxt(
                net_income_array, 
                delimiter=',', 
                unpack=True,
                converters={0: mpl_dates.strpdate2num('%Y-%m-%d')}
                )
            revenue_date, revenue = numpy.loadtxt(
                revenue_array, 
                delimiter=',',
                unpack=True, 
                converters={0: mpl_dates.strpdate2num('%Y-%m-%d')}
                )
            return_on_capital_date, return_on_capital = numpy.loadtxt(
                return_on_capital_array, 
                delimiter=',',
                unpack=True,
                converters={0: mpl_dates.strpdate2num('%Y-%m-%d')}
                )
            #axis_1 = pyplot.subplot2grid((6,6), (0,0), rowspan=2, colspan=6)
            #axis_1.plot(income_date, income)
            #pyplot.ylabel('Net Income')
            #axis_2 = pyplot.subplot2grid((6,6), (2,0), sharex=axis_1, rowspan=2, colspan=6)
            #axis_2.plot(revenue_date, revenue)
            #pyplot.ylabel('Revenue')
            #axis_3 = pyplot.subplot2grid((6,6), (4,0), sharex=axis_1, rowspan=2, colspan=6)
            #axis_3.plot(return_on_capital_date, return_on_capital)
            #pyplot.ylabel('ROC')
            #axis_1.xaxis.set_major_formatter(mpl_dates.DateFormatter('%Y-%m-%d'))
            #pyplot.subplots_adjust(hspace=0.53)
            #pyplot.suptitle(ticker_symbol)
            #pyplot.show()
        except Exception as exception:
            print('failed the main quandl loop:', str(exception))
        return revenue_date, revenue, return_on_capital_date, return_on_capital, income_date, income

    def screener(self, ticker_symbol):
        """
        Definitions:
            pbr - price to book ratio
            pe12t - trailing price/earnings (12 months)
            peg5 - price/earnings to growth ratio (5 years expected)
        """
        try:
            source_code = urllib.request.urlopen('http://finance.yahoo.com' + ticker_symbol).read()
            pbr = source_code.split('Price/Book')[1].split('</td>')[0]
            if float(pbr) < 1:
                peg5 = source_code.split(
                    'PEG Ratio (5 yr expected)<font size="-1"><sup>1</sup></font>:</td><td class="yfnc_tabledata1">'
                    )[1].split('</td>')[0]
                if 0 < float(peg5) < 2:
                    debt_equity_ratio = source_code.split(
                        'Total Debt/Equity (mrq):</td><td class="yfnc_tabledata1">'
                        )[1].split('</td>')[0]
                    pe12t = source_code.split(
                        'Trailing P/E (ttm, intraday):</td><td class="yfnc_tabledata1">'
                        )[1].split('</td>')[0]
                    if float(pe12t) < 15:
                        print('______________________________________')
                        print('')
                        print(ticker_symbol, 'meets requirements')
                        print('price to book:', pbr)
                        print('PEG forward 5 years', peg5)
                        print('Trailing PE (12mo):',pe12t)
                        print('Debt to Equity:', debt_equity_ratio)
                        print('______________________________________')
                        if show_charts.lower() == 'y':
                            try:
                                ChartingStocks().graph_data(ticker_symbol, 25, 50)
                            except Exception as exception:
                                print('Failed to graph:', str(exception))
        except Exception as exception:
            print('error:main loop:', str(exception))

    def parse_russell(self):
        ticker_symbols = []		
        try:
            read_file = open('data/russell3000.txt','r').read()
            split_file = read_file.split('\n')
            for line in split_file:
                split_line = line.split(' ')
                ticker_symbol = split_line[-1]
                ticker_symbols.append(ticker_symbol)
                print(ticker_symbols)
        except Exception:
            pass

if __name__ == '__main__':
    show_charts = input('Would you like to show the financial data (Quandl) charts? (Y/N): ')
    if show_charts.lower()=='y':
        print('okay, charts will be shown')
    elif show_charts.lower()=='n':
        print('okay, charts will NOT be shown.')
    else:
        print('invalid input, charts will NOT be shown.')
    fundamental_investing = FundamentalInvesting()
    for each_stock in even_better:
        fundamental_investing.screener(each_stock)