# Finance-app
This project is a finance application that uses <a href="iexcloud.io/cloud-login#/register/" target="_blank"> iexcloud </a> to get current stock prices for users to buy, and sell with an inital auto balance. This project is a solution to cs50 week 9 lab work.

## GETTING STARTED
### Prequisites and local deployment
Developers using this project should already have Python3, pip and node installed on their local machines.

# API Reference
### Configurating
- Visit <a href="iexcloud.io/cloud-login#/register/" target="_blank"> iexcloud </a>
- Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.
- Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.
- Once you’ve confirmed your account via a confirmation email, visit <a href="https://iexcloud.io/console/tokens" target="_blank"> tokens</a>.
- Copy the key that appears under the Token column (it should begin with pk_).
- save the key in a file and use it to run the application

### Running
-Clone this project to your machine using the command on your terminal:
```
   git clone https://github.com/deen257/cs50-finance-solution
```
- In your terminal window, execute:
```bash
   $ export API_KEY=value
```
-Start Flask’s built-in web server (within `finance/`):

```
   $ flask run
```

## Authors
DEEN

