import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__author__ = 'Eric Zeng'
__email__ = 'ericzeng@seas.upenn.edu'


def fico():
    # data import
    data = pd.read_excel(
        'Undergraduate Analyst Data Challenge.xlsx', sheetname=2)

    # filter by issued/rejected
    issued = data[data['Loan Issued'].isin([1])]
    rejected = data[data['Loan Issued'].isin([0])]

    fico = pd.DataFrame({'LOANID': data['LOANID'],
                         'Rejected': rejected['ORIGINAL_FICO_SCORE'],
                         'Issued': issued['ORIGINAL_FICO_SCORE'],
                         'Rejected_c': rejected['CURRENT_FICO_SCORE'],
                         'Issued_c': issued['CURRENT_FICO_SCORE']})

    print(fico.describe())
    print(fico.loc[fico['LOANID'] == 73622])

    # plot issued/rejected FICO score scatter
    issuedPlot = fico.plot(y='Issued', x='LOANID',
                           kind='scatter', color='blue', label='Issued')
    fico.plot(y='Rejected', x='LOANID', kind='scatter',
              color='red', ax=issuedPlot, label='Rejected')
    plt.title('Original FICO Scores of Loans')
    plt.ylabel('Original FICO')
    plt.axes().axes.get_xaxis().set_visible(False)

    issuedPlot_c = fico.plot(y='Issued_c', x='LOANID',
                             kind='scatter', color='blue', label='Issued')
    fico.plot(y='Rejected_c', x='LOANID', kind='scatter',
              color='red', ax=issuedPlot_c, label='Rejected')
    plt.title('Current FICO Scores of Loans')
    plt.ylabel('Current FICO')
    plt.axes().axes.get_xaxis().set_visible(False)

    delta_i = fico.plot(y='Issued', x='Issued_c',
                        kind='scatter', color='Blue', label='Issued')
    delta_r = fico.plot(y='Rejected', x='Rejected_c',
                        kind='scatter', color='Red', label='Rejected',
                        ax=delta_i)
    fico.loc[fico['LOANID'] == 73622].plot(
        y='Rejected', x='Rejected_c', kind='scatter', color='Green',
        ax=delta_r, label='Loan 73622')
    plt.xlabel('Current FICO')
    plt.ylabel('Original FICO')
    plt.title('Original vs Current FICO Scores of Loans')

    return pd.DataFrame({'Loan ID': data['LOANID'],
                         'Term Length': data['ORIG_TERM'],
                         'Balance': data['CURRENT_BAL'],
                         'APR': data['NOTE_RATE'] / 100,
                         'ZIP': data['PROP_ZIP']})


def employ():
    # 10466 zip of interest
    data = pd.read_excel(
        'Undergraduate Analyst Data Challenge.xlsx', sheetname=4, index_col=0)

    # remove null data
    data.drop(11208, inplace=True)

    employment = pd.DataFrame({'Employment': data['POPULATION_EMPLOYED'],
                               'Unemployment': data['POPULATION_UNEMPLOYED']})

    # describe data, zip of interest, and graph
    print(employment.describe())
    print('Zip of Interest:')
    print(employment.loc[10466])
    employment.plot(y='Employment', kind='hist', bins=24,
                    color='DarkBlue', legend=False)
    plt.title('Employment')
    plt.xlabel('Employment Percentage')
    employment.plot(y='Unemployment', kind='hist',
                    bins=24, color='DarkRed', legend=False)
    plt.title('Unemployment')
    plt.xlabel('Unemployment Percentage')

    # get household income data for use in payments()
    freeCash = pd.DataFrame({'Free Cash': data[
        'HOUSEHOLD_MEDIANINCOME'] - data['HOUSEHOLD_EXPEND_HOUSEHOLD']})
    freeCash.reset_index(level=0, inplace=True)

    return freeCash


def crime():
    # 10466 zip of interest
    data = pd.read_excel(
        'Undergraduate Analyst Data Challenge.xlsx', sheetname=5, index_col=0)

    crimes = pd.DataFrame({'Grand Larceny': data['GRAND LARCENY'],
                           'All Felonies': data['ALLFELONIES']})

    # describe data, zip of interest, and graph
    print(crimes.describe())
    print('ZIP of interest:')
    print(crimes.loc[10466])
    crimes.plot(y='All Felonies', kind='hist',
                bins=24, color='purple', legend=False)
    plt.title('All Felonies')
    plt.xlabel('Number of Felonies')

    crimes.plot(y='Grand Larceny', kind='hist',
                bins=24, color='Orange', legend=False)
    plt.title('Grand Larceny')
    plt.xlabel('Number of Grand Larceny Felonies')


def delqent():
    # 10466 zip of interest
    data = pd.read_excel(
        'Undergraduate Analyst Data Challenge.xlsx', sheetname=3)

    delq = pd.DataFrame({'Neighborhood': data['NEIGHBORHOODNAME'],
                         'Delinquency': data['DELINQUENCY'] * 100})

    # describe and plot
    print(delq.describe())
    print('Zip of Interest:')
    print(delq.loc[delq['Neighborhood'] ==
                   'Eastchester-Edenwald-Baychester'])
    delq.plot(y='Delinquency', kind='hist',
              bins=24, color='green', legend=False)
    plt.title('Delinquency on Payments')
    plt.xlabel('% of Homes Delinquent')


def pay(payments, incomes):
    # determine monthly payment needed at given APR, curent balance, and term
    # Source: https://www.thebalance.com/loan-payment-calculations-315564
    monthlyPayments = pd.DataFrame({'Loan ID': payments['Loan ID'],
                                    'ZIP': payments['ZIP'],
                                    'Monthly Due': payments['Balance'] /
                                    ((((1 + payments['APR'] / 12)
                                       ** payments['Term Length']) - 1) /
                                     (payments['APR'] / 12 *
                                        (1 + payments['APR'] / 12) **
                                        payments['Term Length']))})

    # remove null data
    monthlyPayments = monthlyPayments[monthlyPayments['Loan ID'] != 349324]

    # Series containing matching median FC in each loan's ZIP
    incomesSorted = pd.Series(name='FC')
    for i in monthlyPayments.iterrows():
        incomesSorted.set_value(i[0], incomes.loc[
                                incomes['PROP_ZIP'] ==
                                int(i[1]['ZIP'])]['Free Cash'].values[0])

    # add to monthlypayments, divide incomesSorted by 12 to get Monthly FC
    monthlyPayments['Monthly FC'] = incomesSorted / 12
    # Outlook: percentage of monthly FC used to pay loan
    monthlyPayments['Outlook'] = 100 * monthlyPayments[
        'Monthly Due'] / monthlyPayments['Monthly FC']

    # describe and plots
    print(monthlyPayments.describe())
    print(monthlyPayments.loc[monthlyPayments['Loan ID'] == 73622])

    all = monthlyPayments.plot(
        y='Outlook', x='Loan ID', kind='scatter', color='DarkBlue')
    monthlyPayments.loc[monthlyPayments['Loan ID'] == 73622].plot(
        y='Outlook', x='Loan ID', kind='scatter', ax=all, color='Green', label='Loan 73622')
    plt.title('Percent of Monthly Free Cash Spent on Loan Payment (Lower is better)')
    plt.ylabel('Outlook (%)')
    plt.axes().axes.get_xaxis().set_visible(False)


if __name__ == "__main__":
    payments = fico()
    print()

    incomes = employ()
    print()

    crime()
    print()

    delqent()
    print()

    pay(payments, incomes)
    print()

    plt.show()
