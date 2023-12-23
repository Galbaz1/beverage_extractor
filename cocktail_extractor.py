from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from menu import menu

from openai import OpenAI
import instructor
import os
import json




# This enables response_model keyword
# from client.chat.completions.create
client = instructor.patch(OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY_HERE"))

class CocktailCategory(str, Enum):
    """Act as a knowledgeable cocktail mixologist. Your task is to classify cocktails into their appropriate glassware category. Choose one. Incase it's not a cocktail, but another beverage or a menu category choose 'NO_COCKTAIL'."""
    NO_COCKTAIL = "No Cocktail"
    ROCKS = "Rocks"
    HURRICANE = "Hurricane"
    MARTINI = "Martini"
    HIGHBALL = "Highball"
    COUPE = "Coupe"
    COLLINS = "Collins"
    MULE = "Mule"
    SHOT = "Shot"
    FLUTE= "Flute"
    SNIFFER = "Sniffer"
    UNKNOWN = "Unknown"

class Cocktails(BaseModel):
    """Your task is to meticulously extract information from a cocktail menu. For each cocktail listed, identify and list its name, ingredients, and price. Based on the name and ingredients, provide a short description of the tasting notes, including the flavors and nuances one might experience while drinking it. Than add a short description of the overall aroma and taste profile of the cocktail, drawing on the ingredients and their interplay to give a vivid sensory impression."""
    name: str = Field(..., description="The name of the cocktail. If it's not a cocktail, but another beverage or a menu category, leave empty.")
    ingredients: list[str] = Field(..., description="List of ingredients in the cocktail. If it's not a cocktail, but another beverage or a menu category, leave empty.")
    price: Optional[float] = Field(default=None, description="Price of the cocktail.")
    ingredient_notes: list[str] = Field(..., description="Describe the aroma and flavor notes each ingredient contributes to the cocktail, taking into account its relative contribution. Focus on how the ingredient's characteristics influence the overall balance and sensory experience of the drink. For instance, if an ingredient is a minor addition, its notes should be described as subtle; conversely, for a dominant ingredient, detail its prominent impact on the cocktail's taste and aroma. If it's not a cocktail, but another beverage or a menu category, leave empty.")
    tasting_notes: list[str] = Field(..., description="Provide a comprehensive description of the cocktail's tasting experience. This should include a detailed assessment of the flavor profile, aroma, mouthfeel, and aftertaste. Consider how the individual ingredients combine to create the overall taste, and mention any unique or distinguishing characteristics. The description should convey the full sensory experience of the cocktail, allowing the reader to imagine its taste and aroma vividly. If it's not a cocktail, but another beverage or a menu category, leave empty.")
    category: CocktailCategory 



menu = menu 


class CocktailClassifier:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def classify_cocktail(self, cocktail):
        print(f"Classifying the menu: {cocktail[:50]}...")
        classification = self.client.chat.completions.create(
            model=self.model_name,
            response_model=Cocktails,
            messages=[
                {"role": "system", "content": "your task is to extract the cocktails from the menu into one of the following categories: Rocks, Hurricane, Martini, Highball, Coupe, Collins, Mule, Shot, Flute, Sniffer, Unknown. Then, extract the information, and finally, use everything to write professional tasting notes.  Please return all possible fields."},
                {"role": "user", "content": f"cocktail : {cocktail}"}
            ],
        )
        return classification.model_dump()

classifier = CocktailClassifier(client, "gpt-4-1106-preview")
#classifier = CocktailClassifier(client, "gpt-3.5-turbo-1106")



categorized_cocktails = []
for cocktail in menu[:]:
    # Classify the cocktail
    category = classifier.classify_cocktail(cocktail)
    print(f"The cocktail {cocktail[:50]}... is classified as {category['category']}")

    # Check if the category is not "No Cocktail"
    if category['category'] != "No Cocktail":
        cocktail_dict = {
            "name": category['name'],
            "ingredients": category['ingredients'],
            "price": category['price'],
            "ingredient_notes": category['ingredient_notes'],  
            "tasting_notes": category['tasting_notes'],
            "category": category['category'],
        }
        categorized_cocktails.append(cocktail_dict)

# Save the categorized cocktails to the json file
with open('sample_cocktails.json', 'w') as f:
    json.dump(categorized_cocktails, f, indent=4)
