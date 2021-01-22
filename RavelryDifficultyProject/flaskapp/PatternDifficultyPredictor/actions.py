from flask import Flask, render_template, request
from flaskapp.PatternDifficultyPredictor.rav_utils import get_pattern_data, make_difficulty_prediction, \
    get_rav_credentials, get_top_features, get_pattern_permalink


app = Flask(__name__)


@app.route('/')
# @app.route('/index')
def pattern_input():
    return render_template("webpage5.html")


@app.route('/', methods=['GET', 'POST'])
def get_difficulty_prediction():

    try:

        # Get user input on webpage
        pattern_url = request.form['pattern url']

        # Get the permalink from the url
        pattern_permalink = get_pattern_permalink(pattern_url)

        # Get authentications
        auth_tuple = get_rav_credentials()

        # Scrape pattern data from the Ravelry API
        pattern_data = get_pattern_data(pattern_permalink, auth_tuple)

        # Make a difficulty prediction based on the pattern data
        difficulty_prediction = make_difficulty_prediction(pattern_data)

        # Get the top features for the prediction
        top_feature_dict = get_top_features(pattern_data)
        difficult_features = top_feature_dict['difficult_features']
        easy_features = top_feature_dict['easy_features']

        # Get pattern info for display
        author_name = pattern_data['author_name'].values[0]
        pattern_name = pattern_data['name'].values[0]
        pattern_photo_data = pattern_data['photos2']
        try:
            pattern_photo_url = pattern_photo_data.values[0][0]['small_url']
        except:  # If something goes wrong with the photo, we can just display an empty photo.
            pattern_photo_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/240px-No_image_available.svg.png'

        return render_template("webpage5.html", prediction=difficulty_prediction, pattern_author=author_name,
                               pattern_name=pattern_name, pattern_photo_url=pattern_photo_url,
                               difficult_features=difficult_features, easy_features=easy_features)

    except:
        print('exception')
        difficulty_prediction = -5
        return render_template("webpage5.html", prediction=difficulty_prediction, pattern_author=None,
                               pattern_name=None, pattern_photo_url=None,
                               difficult_features=None, easy_features=None)

if __name__ == '__main__':
    app.run()
