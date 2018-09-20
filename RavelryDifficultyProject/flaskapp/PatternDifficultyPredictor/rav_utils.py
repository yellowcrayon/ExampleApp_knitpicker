import requests as rq
import pandas as pd
import numpy as np
import re
from sklearn.externals import joblib
# from src.model import build_important_feature_extractor

# Import the model and the important feature extractor
MODEL = joblib.load('models/05_weighted_linreg.pkl')
# top_f_pipeline = build_important_feature_extractor(MODEL, 10)
top_f_pipeline = joblib.load('models/05_feature_extractor.pkl')


def get_rav_credentials():
    # Open my Ravelry authentication values
    path = 'data/RavelrySecret.txt'  # Path to the file that holds
    # my keys--the username and password given to me by Ravelry for my Basic Auth, read only app
    mode = 'r'  # read mode--I'll only need to read the username and password from the file

    keys = []  # The list where I'll store my username and password
    with open(path, mode) as f:  # Open the file
        for line in f:
            keys.append(line)  # The first line is the username, and the second line is the password--add each of these
            # lines to the keys list

    user = keys[0].rstrip()  # The username is held in the first element of the keys list
    pswd = keys[1].rstrip()  # The password is the second element of the keys list
    authTuple = (user, pswd)

    return authTuple


def query_rav_api(endpoint, addStr, authTuple):
    baseUrl = 'https://api.ravelry.com/'
    queryStr = baseUrl + endpoint + addStr
    response = rq.get(queryStr, auth=authTuple)
    return response


def getNestedAttributes(Dict, attrList, levelKey, attrKey):
    """ Take a dictionary of nested dictionaries, go down each level of the nested dictionary and construct a list of
    all the values (attributes) that correspond to attrKey.

    Dict is the dictionary of data.
    attrList is the list of attributes associated with attrKey.
    levelKey is the dictionary key that contains another dictionary within it.
    attrKey is the dictionary key that contains the data we want from each level of the nested dictionaries.
    This function adds onto the existing list, attrList, and simply returns True when it reaches the end of the nested dictionaries.
    This function assumes that there are only a handful of nested dictionaries inside Dict, so recursion is appropriate.

    Example:
    myDict = [{'permalink': 'shawl-wrap', 'id': 350, 'parent': {'permalink': 'neck-torso', 'id': 338, 'parent': {'permalink': 'accessories', 'id': 337, 'parent': {'permalink': 'categories', 'id': 301, 'name': 'Categories'}, 'name': 'Accessories'}, 'name': 'Neck / Torso'}, 'name': 'Shawl / Wrap'}]
    myList = []
    getNestedAttribute(myDict,myList,'parent','name') """

    try:
        tempDict = Dict.get(levelKey)  # Look for the next level of dictionaries.
        # This will return the value if there is another level, and None if there is not.

        tempVal = Dict.get(attrKey)  # Look for the attribute of interest at this dictionary level.
        # If the attribute is not available, we'll get a None in its place.

        if tempDict is None:  # If we've reached the inner-most dictionary.
            attrList.append(tempVal)  # Simply append the final attribute at this level.
            return True  # Return True (attrList is modified in place, and doesn't need to be returned).

        else:  # If there are more levels within the nested dictionary.
            attrList.append(tempVal)  # Append the value associated with attrKey from this level of the dictionary.
            return getNestedAttributes(tempDict, attrList, levelKey,
                                       attrKey)  # Go down one level in the nested dictionary and look for more data.

    except:  # If anything goes wrong, return False
        return False


def makeAttrList(dictList, attr):
    # dictList is a list of dictionaries.
    # attr is the dictionary key whose values you want to pick out and put in a list.
    # attrList is the final list of all attributes associated with the attr key.
    try:
        attrList = []
        for el in dictList:
            attrList.append(el.get(attr))  # Appends None if that key is not found
        return attrList

    except:  # If anything goes wrong, return None
        return None


def te(codeChunk, func):
    # This function tries to apply a function to an input.
    # If it is unsuccessful, it returns None.
    try:
        return func(codeChunk)
    except:
        return None


def parse_rav_pattern_response(patternData):
    # This function will take in the json data from a single pattern ID,
    # and return a dictionary with the pattern attributes I want to store.

    try:

        patternDict = {}  # Initialize an empty dictionary--this is where we'll store all of the data

        # Single item bools--must convert to int
        patternDict['downloadable'] = te(patternData.get('downloadable'), int)         # Int; whether the pattern can be downloaded (on Ravelry or on another site)
        patternDict['ravelry_download'] = te(patternData.get('ravelry_download'), int) # Int; whether the pattern is available as a download from Ravelry (free or for money)
        patternDict['free'] = te(patternData.get('free'), int)                         # Int; whether the pattern is available for no cost

        # Single item ints
        patternDict['queued_projects_count'] = te(patternData.get('queued_projects_count'), int) # Int; number of user queues the pattern is in
        patternDict['rating_count'] = te(patternData.get('rating_count'), int)                   # Int; number of times the pattern has been rated
        patternDict['id'] = te(patternData.get('id'), int)                                       # Int; pattern ID
        patternDict['favorites_count'] = te(patternData.get('favorites_count'), int)             # Int; number of times the pattern has been favorited
        patternDict['difficulty_count'] = te(patternData.get('difficulty_count'), int)           # Int; number of difficulty ratings the pattern has received
        patternDict['projects_count'] = te(patternData.get('projects_count'), int)               # Int; number of projects made from this pattern
        patternDict['comments_count'] = te(patternData.get('comments_count'), int)               # Int; number of comments that have been made on this pattern

        # Single item floats
        patternDict['rating_average'] = te(patternData.get('rating_average'), float) # Float; the pattern's average rating on a scale from 0 to 5 stars
        patternDict['yardage_max'] = te(patternData.get('yardage_max'), float)       # Float; a number describing the estimated maximum yarn yardage a patter will take to make
        patternDict['yardage'] = te(patternData.get('yardage'), float)               # Float; estimated yarn yardage the patter will use
        patternDict['gauge'] = te(patternData.get('gauge'), float)                   # Float; e.g. 16.0
        patternDict['price'] = te(patternData.get('price'), float)                   # Float; the pattern price, currency is given by 'currency'

        # Single item strings
        patternDict['sizes_available'] = te(patternData.get('sizes_available'), str)               # String; description of sizes the pattern can be made to
        patternDict['row_gauge'] = te(patternData.get('row_gauge'), str)                           # String; the pattern's row gauge (not sure what the range of values are)
        patternDict['permalink'] = te(patternData.get('permalink'), str)                           # String; the pattern's url--add to 'https://www.ravelry.com/patterns/library/'
        patternDict['gauge_pattern'] = te(patternData.get('gauge_pattern'), str)                   # String; e.g. 'Stockinette Stitch with yarn held double'
        patternDict['gauge_description'] = te(patternData.get('gauge_description'), str)           # String; e.g. 16 stitches and 24 rows = 4 inches in Stockinette Stitch with yarn held double
        patternDict['yarn_weight_description'] = te(patternData.get('yarnWeightDescription'), str) # String, e.g. 'Fingering (14 wpi)'
        patternDict['yardage_description'] = te(patternData.get('yardage_description'), str)       # String; string describing yardage
        patternDict['currency_symbol'] = te(patternData.get('currency_symbol'), str)               # String; currency symbol, e.g. $
        patternDict['currency'] = te(patternData.get('currency'), str)                             # String; a string describing the currency, e.g. USD
        patternDict['name'] = te(patternData.get('name'), str)                                     # String; the pattern name
        patternDict['difficulty_average'] = te(patternData.get('difficulty_average'), str)         # String; the average difficulty rating of the pattern, on a scale from 0 to 10, with ? as unknown
        patternDict['published'] = te(patternData.get('published'), str)                           # String; the date the pattern was published in the form yyyy/mm/dd
        patternDict['created_at'] = te(patternData.get('created_at'), str)                         # String; the date the pattern page was created
        patternDict['updated_at'] = te(patternData.get('updated_at'), str)                         # String; the most recent date that the pattern page was updated on
        patternDict['generally_available'] = te(patternData.get('generally_available'), str)       # String; Ravelry's best estimate of the date when this pattern first became available to the public (not necessarily related to the pattern page creation date)
        patternDict['printings'] = te(patternData.get('printings'), str)                           # String; Data dump of where the pattern has been published
        patternDict['personal_attributes'] = te(patternData.get('personal_attributes'), str)       # String; ? not sure what personal attributes is yet, scraping it just in case.
        patternDict['photos'] = te(patternData.get('photos'), str)                                 # String; Data dump of photo info and urls.
        patternDict['photos2'] = patternData.get('photos')
        patternDict['pattern_needle_sizes'] = te(patternData.get('pattern_needle_sizes'), str)     # String; Data dump of pattern needle and hook size info.
        patternDict['yarn_weight'] = te(patternData.get('yarn_weight'), str)                       # String; Data dump of yarn weight info.

        # Items from 'pattern_author'
        tempData = patternData.get('pattern_author', {})  # Data on the pattern's author
        patternDict['author_patterns_count'] = te(tempData.get('patterns_count'), int)      # Int; number of patterns by the author
        patternDict['author_favorites_count'] = te(tempData.get('favorites_count'), int)    # Int; number of times the author has been favorited
        patternDict['author_id'] = te(tempData.get('id'), int)                              # Int; author ID
        patternDict['author_name'] = te(tempData.get('name'), str)                          # String; author name
        patternDict['author_permalink'] = te(tempData.get('permalink'), str)                # String; permalink to the pattern author's Ravelry page (/designers/{permalink})
        tempData = tempData.get('users',[]) # Pattern author site user info, a list of dictionaries; if the 'users' key is not found, return an empty list so that the following lines can still run
        patternDict['author_users_usernames'] = te(makeAttrList(tempData, 'username'), str) # String; list of author usernames
        patternDict['author_users_ids'] = te(makeAttrList(tempData, 'id'), str)             # String; list of author usernames

        # Items from 'photos'
        tempData = patternData.get('photos', {})  # If the 'photos' key doesn't exist, return an empty list so that the following line can still run
        patternDict['num_photos'] = len(tempData) # Int; the number of photos the pattern has

        # Items from 'pattern_type'
        tempData = patternData.get('pattern_type', {})
        patternDict['pattern_type_permalink'] = te(tempData.get('permalink'), str) # String; a word that describes the type of pattern, e.g. 'pullover'
        patternDict['pattern_type_name'] = te(tempData.get('name'), str)           # String; another descriptive word
        patternDict['pattern_type_clothing'] = te(tempData.get('clothing'), int)  # Bool; whether or not the pattern is considered clothing

        # Items from 'craft'
        tempData = patternData.get('craft', {})
        patternDict['craft_permalink'] = te(tempData.get('permalink'), str) # String; a word describing the craft
        patternDict['craft_name'] = te(tempData.get('name'), str)           # String; also a word describing the craft

        # Items from 'pattern_categories'
        tempData = patternData.get('pattern_categories', {})
        tempList = []  # Start a temporary, empty list
        for el in tempData: # Each element of tempData is a nested dictionary (dictionary of dictionaries)
            getNestedAttributes(el, tempList, 'parent', 'name')  # This function appends all the names of the pattern categories onto tempList
        patternDict['pattern_categories_name'] = te(tempList, str) # String; the list of category names

        # Items from 'notes'
        tempData = patternData.get('notes', '')  # if the 'notes' key is not found, return an empty string so the following lines can still run
        if not tempData:  # If tempData is type None, we can't take its len, so set notes_length to 0 instead
                          # and store the notes as an empty string.
            patternDict['notes_length'] = 0
            patternDict['notes'] = ''
        else:
            patternDict['notes_length'] = len(tempData)  # Int; the number of characters in the pattern notes
            patternDict['notes'] = te(tempData, str)     # String; The text of the pattern description on the pattern page.

        # Items from 'pattern_attributes'
        tempData = patternData.get('pattern_attributes', [])  # tempData will be a list of dictionaries
        patternDict['pattern_attributes_permalinks'] = te(makeAttrList(tempData, 'permalink'), str) # String; the list of attribute descriptors

        # Items from 'packs'
        tempData = patternData.get('packs', [])  # A list of data about the suggested yarn for the pattern
        patternDict['packs_colorways'] = te(makeAttrList(tempData, 'colorway'), str)   # String; list of colorways of suggested yarns
        patternDict['packs_yarn_names'] = te(makeAttrList(tempData, 'yarn_name'), str) # String; list of yarn names
        patternDict['packs_yarn_ids'] = te(makeAttrList(tempData, 'yarn_id'), str)     # String; list of yarn company names

        # If everything goes to plan, return the dictionary of data that we made!
        return patternDict

    except:

        return None


def find_pat_id_from_url(pattern_permalink):
    """ Input a pattern permalink and return the pattern's ID as a string.

    pattern_permalink is the last bit of the pattern page url, e.g. for the pattern webpage url
    'https://www.ravelry.com/patterns/library/mysteries-she-wrote', the permalink is 'mysteries-she-wrote'."""

    base_url = 'https://www.ravelry.com/patterns/library/'
    query_str = base_url + pattern_permalink
    response = rq.get(query_str)
    pat = 'pattern_(?P<ID>[0-9]+)_difficulty'
    match = re.search(pat, response.text)
    id_str = match.group('ID')
    return id_str


def get_pattern_data(pattern_permalink, authTuple):

    # Look for the pattern ID from within the pattern web page
    pattern_id = find_pat_id_from_url(pattern_permalink)

    # Query the Ravelry API using the pattern id, get the API's response.
    endpoint = 'patterns/'
    addStr = pattern_id + '.json'
    response = query_rav_api(endpoint, addStr, authTuple)

    # Parse the API response into a dictionary
    pattern_data = response.json()['pattern']
    pattern_dict = parse_rav_pattern_response(pattern_data)

    # Wrap each value in pattern_dict with a list, the convert pattern_dict into a pandas dataframe
    pattern_dict = {key: [value,] for key, value in pattern_dict.items()}
    pattern_df = pd.DataFrame(pattern_dict)

    return pattern_df


def make_difficulty_prediction(pattern_data):
    temp1 = MODEL.predict(pattern_data)

    # Round to the nearest integer
    temp2 = int(round(temp1[0], 0))

    # Bound the prediction between 1 and 10
    if temp2 < 1:
        difficulty_prediction = 1
    elif temp2 > 10:
        difficulty_prediction = 10
    else:
        difficulty_prediction = temp2

    return str(difficulty_prediction)


def get_top_features(pattern_data):

    top_features = top_f_pipeline.transform(pattern_data)

    # top_features is already sorted by absolute value, so these two lists will automatically be sorted from left to
    # right by their absolute values, too!
    difficult_features = top_features[0][:][top_features[0, :, 1] >= 0]
    easy_features      = top_features[0][:][top_features[0, :, 1] <= 0]

    # Extract just the string names of the sorted features
    # Also convert all first letters in the strings into capital letters
    difficult_names = [el.title() for el in difficult_features[:, 0]]
    easy_names = [el.title() for el in easy_features[:, 0]]

    return {'difficult_features': difficult_names, 'easy_features': easy_names}


def get_pattern_permalink(pattern_url):
    # pat = 'patterns/library/(?P<ID>[-A-Za-z0-1]+)'
    pat = 'patterns/library/(?P<ID>[^/]+)'
    match = re.search(pat, pattern_url)
    if match:
        pattern_permalink = match.group('ID')
        return pattern_permalink
    else:
        # A secondary pattern to try to find the pattern url from project pages.
        # Remember though that even though every project has a name permalink that we'll find here, not every project
        # has a pattern associated with it. We'll have to handle that case in a different function, because we can't
        # tell from the url whether there is an actual pattern page or not.
        pat = 'projects/[^/]+/(?P<ID>[^/]+)'
        match = re.search(pat, pattern_url)
        if match:
            pattern_permalink = match.group('ID')
            return pattern_permalink
        else:
            return None


if __name__ == '__main__':
    # Test the functions
    authTuple = get_rav_credentials()
    pattern_data = get_pattern_data('mysteries-she-wrote', authTuple)

    # print(pattern_data.values)
    # print(make_difficulty_prediction(pattern_data))
    # print(pattern_data['author_name'].values[0])
    # pattern_photo_url = pattern_data['photos2'].values[0][0]['medium_url']
    # print(pattern_photo_url)

    # top_features = top_f_pipeline.transform(pattern_data)
    # print(top_features)
    # print(type(top_features))
    # print(top_features[0][0][0])
    # print(top_features[0][0][1])
    # print(top_features[0][0])
    # print(top_features[0, 0, :])
    # print(type(top_features[0][0:][0]))
    # print(pd.DataFrame(top_features))
    # print(top_features[0, :, 0])
    # print(top_features[0, :, 1])
    #
    # top_feature_names = top_features[0, :, 0]
    # top_feature_values = top_features[0, :, 1]
    #
    # top_features_sorted = [(y, x) for y, x in sorted(zip(top_feature_values, top_feature_names))]
    # print(top_features_sorted)
    #
    # easy_features = [(y, x) for y, x in top_features]
    # print('\n')

    # top_features is already sorted by absolute value, so these two lists will automatically be sorted from left to
    # right by their absolute values, too!
    # print(top_features[0][:][top_features[0, :, 1] >= 0])
    # print(top_features[0][:][top_features[0, :, 1] <= 0])

    # top_feature_dict = get_top_features(pattern_data)
    # difficult_features = top_feature_dict['difficult_features']
    # easy_features = top_feature_dict['easy_features']

    # pattern_url = 'https://www.ravelry.com/patterns/library/mysteries-she-wrote'
    # print(get_pattern_permalink(pattern_url))

    pattern_url = 'https://www.ravelry.com/patterns/library/124-1-bohemian-oasis'
    print(get_pattern_permalink(pattern_url))
