# cs50-finance-solution
This is my solution to cs50 week 9 finance lab work 

## Getting started 
### Configurating
- Visit <a href="iexcloud.io/cloud-login#/register/" target="_blank"> iexcloud </a>
- Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.
- Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.
- Once you’ve confirmed your account via a confirmation email, visit <a href="https://iexcloud.io/console/tokens" target="_blank"> tokens</a>.
- Copy the key that appears under the Token column (it should begin with pk_).
- In your terminal window, execute:
```bash
   $ export API_KEY=value
```
### Running 
Start Flask’s built-in web server (within `finance/`):
```
   $ flask run
```
