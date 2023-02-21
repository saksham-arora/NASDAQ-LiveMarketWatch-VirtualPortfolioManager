# NASDAQ-LiveMarketWatch-VirtualPortfolioManager
This project contains a web server and client code using which you can virtually buy/sell stocks listed on NASDAQ stock exchange and see their live prices.

CONTENTS OF THIS FILE
---------------------

 * Introduction
 * Requirements
 * Installation
 * Configuration
 * Execution
 * Author
 * Sources


INTRODUCTION
------------

NASDAQ Live Marketwatch and Portfolio Manager gives you a virtual environment for trading with virtual money but on 
actual live prices on NASDAQ stock market. 
Any user which is first time needs to register and then he/she will be provided with a virtual amount of $10,000
which can be used to buy/sell shares of any listed symbol on NASDAQ. 
Web Server is built using python based based Web Framework Flask and will listen on 127.0.0.1:5000 by default once started

Here are some of the main features:
 * User can see the current price of any symbol by clicking on Quote option in Menu
 * User can buy/sell any stock listed on NASDAQ using his/her virtual money
 * User can see the history of all his trades
 * User can see the portfolio of all the stocks which he currently holds along with details
 * In the portofolio user can see the price and value of every stock updating live in trading hours and can see his profit/loss
 * Portoflio has user friendly color synchronization of green/red to recognize which stock increased from its last price
 * Data storage is persistent i.e. even if the web server is stopped then on restarting all data will be gathered again


REQUIREMENTS
------------

Following packages are required before starting the web server:
   - Python 3.7 or above
   - Pip 20.0 or above (can be installed while installing Python)

   Below mentioned are all python packages which can be installed using pip
   - cs50
   - Flask 
   - Flask-Session
   - requests



INSTALLATION
------------

- clone the Repository
- Install all the mentioned packages mentioned in the requirement section. There is no other specific thing required


CONFIGURATION
-------------

1) Setting up API_KEY to get stocks data:

- Visit iexcloud.io/cloud-login#/register/.
- Enter your email address and a password, and click “Create account”.
- On the next page, scroll down to choose the Start (free) plan.
- Once you’ve confirmed your account via a confirmation email, sign in to iexcloud.io.
- Click API Tokens.
- Copy the key that appears under the Token column (it should begin with pk_).

For MacOs or Linux
- In a terminal window, execute:
export API_KEY=value

For Windows
- In command prompt, execute:
set API_KEY=value

where value is that (pasted) value, without any space immediately before or after the =. You also may wish to paste that value in a text document somewhere, in case you need it again later


2) Configuring Flask:
  For MacOs or Linux, execute following in terminal:
      export FLASK_APP=application.py

  For Windows, execute following in command prompt:
      set FLASK_APP=application.py



EXECUTION:
---------

- Go to the cloned repository and execute following command:
      Flask run
- Open your browser and copy paste following link:
      http://127.0.0.1:5000/
- Web Page will be loaded where you need to register if you are visiting first time and then login
- After login you can try various features like buy/sell/quote/history and also check your portfolio date updating live if it's mrket hours 



SOURCES:
----------

 * NASDAQ Market Data  - https://iexcloud.io/
 * Error Image from Imgur - https://i.imgur.com/Mr4tBkv.jpeg 



