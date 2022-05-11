from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import random
import os

app = Flask(__name__)
Bootstrap(app)


# Dog_API
DOG_BREED_ENDPOINT = 'https://api.thedogapi.com/v1/breeds'
API_KEY = os.environ['API_KEY']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
headers = {
    "x-app-key": API_KEY,
}


# User input form
class DogForm(FlaskForm):
    breed = StringField("Enter Breed Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Doggo:
    def __init__(self, name, weight, height, bred_for, breed_group, life_span, img_url):
        self.name = name
        self.weight = weight
        self.height = height
        self.bred_for = bred_for
        self.breed_group = breed_group,
        self.life_span = life_span
        self.img_url = img_url


def similar_size_dogs(input_dog, response):
    similar_dogs_list = []
    lbs = round(int(float(input_dog[-2:])))
    for dog in response:
        w = round(int(float(dog['weight']['imperial'][-2:])))
        weight_range = range(w - 10, w, 1)
        if lbs in weight_range:
            new_dog = {'name': dog['name'],
                       'img_url': dog['image']['url']}
            similar_dogs_list.append(new_dog)
    three_breeds = []
    print(len(similar_dogs_list))
    if len(similar_dogs_list) > 1:
        for i in range(3):
            print(len(similar_dogs_list))
            n = random.randint(0, len(similar_dogs_list) - 1)
            print(n)
            random_dog = similar_dogs_list[n]
            three_breeds.append(random_dog)
            similar_dogs_list.remove(random_dog)
        return three_breeds
    else:
        return similar_dogs_list


@app.route('/', methods=["GET", "POST"])
def home():
    form = DogForm()
    if request.method == "POST":
        if form.validate_on_submit():
            return redirect(url_for('dog_info', name=form.breed.data))
    return render_template('index.html', form=form)


@app.route('/<string:name>', methods=["GET", "POST"])
def dog_info(name):
    form = DogForm()
    response = requests.get(url=DOG_BREED_ENDPOINT, headers=headers)
    if form.validate_on_submit():
        name = form.breed.data
    for dog in response.json():
        if name.lower() == dog['name'].lower():
            similar_dogs = similar_size_dogs(dog['weight']['imperial'], response.json())
            length = len(similar_dogs)
            if 'bred_for' not in dog:
                bred_for = 'Not Bred by Humans'
            else:
                bred_for = dog['bred_for']
            if 'breed_group' not in dog:
                breed_group = 'No Particular Breed Group'
            else:
                breed_group = dog['breed_group']
            dog_displayed = Doggo(
                name=dog['name'],
                weight=dog['weight']['imperial'],
                height=dog['height']['imperial'],
                bred_for=bred_for,
                breed_group=breed_group,
                life_span=dog['life_span'],
                img_url=dog['image']['url']
            )
    return render_template('index.html', form=form, dog=dog_displayed, similar_dogs=similar_dogs, length=length)


if __name__ == "__main__":
    app.run(debug=True)
