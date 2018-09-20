Note that this app is incomplete and WILL NOT RUN, because I have removed the contents of the file RavelrySecret.txt in the data folder. RavelrySecret.txt in the real app contains my app developer username and password that allows me to access the Ravelry API. If you want to make your own app that queries the Ravelry API, you will need to fill in these values with your own username and password.

This code is a simplified version of the code that runs my app, [knitpicker.site](knitpicker.site). Knitpicker is an app that helps knitters find the right pattern for their skill level by predicting and explaining knitting pattern difficulty. The app predicts the difficulty of knitting (and crochet) patterns from the social media website [ravelry.com](ravelry.com).

The purpose of posting this code is to show how I structured my knitpicker Flask app folder. The app takes inputs from a user on the home page, then queries the [Ravelry api](https://www.ravelry.com/api#patterns_patterns) to retrieve information about a knitting pattern. The app organizes the information it retrieved, then puts that information into a machine learning model. The model computes some outputs, which are then displayed on the website.

The files actions.py and rav_utils.py perform the back end computations in python.

The file webpage5.html contains both the css and html for the website. The css is all at the top of webpage5 and is separated from the html, but it the css could (and probably should) be placed into its own file.

The models folder contains the models that compute the website output. Both the model and the feature extractor were implemented as scikit-learn pipelines before I exported them using pickle.

There is one image file, knit-pattern-green-7, which provides the website header image.
