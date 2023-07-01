import random
from faker import Faker
import pandas as pd

#Set the possible entity types
entity_types = ['farm',
                'processor',
                'packaging',
                'grocery',
                'restaurant',
                'distributor',
                'wholesaler',
                'groceryNoTransform',
                'landBasedReceiver',
                'seafoodFarm'
                ]

#Generate the names for the different types of entities
def generate_farm_name():
    adjectives = ['Green', 'Sunny', 'Golden', 'Misty', 'Whispering', 'Breezy', 'Happy', 'Lucky', 'Peaceful']
    nouns = ['Meadows', 'Fields', 'Grove', 'Acres', 'Hills', 'Harvest', 'Valley', 'Orchard', 'Pastures']

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)

    farm_name = adjective + ' ' + noun + ' Farm'
    return farm_name

def generate_wholesaler_name():
    prefixes = ['Fresh', 'Prime', 'Select', 'Quality', 'Premium', 'Global', 'Gourmet', 'Best', 'Top', 'Wholesome']
    suffixes = ['Foods', 'Provisions', 'Supplies', 'Distributors', 'Wholesale', 'Imports', 'Market', 'Trading', 'Traders']

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)

    wholesaler_name = prefix + ' ' + suffix
    return wholesaler_name

def generate_grocery_name():
    prefixes = ['Fresh', 'Healthy', 'Natural', 'Gourmet', 'Tasty', 'Delicious', 'Organic', 'Wholesome', 'Premium', 'Fine']
    suffixes = ['Foods', 'Market', 'Grocery', 'Mart', 'Shop', 'Store', 'Bazaar', 'Corner', 'Emporium', 'Outlet']

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)

    retailer_name = prefix + ' ' + suffix
    return retailer_name

def generate_distributor_name():
    prefixes = ['Global', 'International', 'Premium', 'Quality', 'Reliable', 'Prime', 'Gourmet', 'Fine', 'Superior', 'Trusted']
    suffixes = ['Distributors', 'Distribution', 'Imports', 'Supply', 'Logistics', 'Wholesalers', 'Trade', 'Services', 'Exim', 'Network']

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)

    distributor_name = prefix + ' ' + suffix
    return distributor_name

def generate_packaging_company_name():
    prefixes = ['Eco', 'Green', 'Fresh', 'Quality', 'Premium', 'Global', 'Innovative', 'Advanced', 'Bio', 'Secure']
    suffixes = ['Pack', 'Packaging', 'Packs', 'Solutions', 'Wraps', 'Containers', 'Seal', 'Wrap', 'Encase', 'Box']

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)

    packaging_company_name = prefix + ' ' + suffix
    return packaging_company_name

def generate_restaurant_name():
    adjectives = ['Delicious', 'Tasty', 'Savory', 'Gourmet', 'Exquisite', 'Flavorful', 'Authentic', 'Fusion', 'Charming', 'Cozy']
    nouns = ['Bistro', 'Cuisine', 'Grill', 'Eatery', 'Cafe', 'Brasserie', 'Diner', 'Tavern', 'Kitchen', 'Restaurant']

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)

    restaurant_name = adjective + ' ' + noun
    return restaurant_name

def generate_food_processing_company_name():
    prefixes = ['Fresh', 'Natural', 'Pure', 'Premium', 'Quality', 'Global', 'Innovative', 'Healthy', 'Organic', 'Wholesome']
    suffixes = ['Foods', 'Processing', 'Kitchen', 'Cuisine', 'Provisions', 'Solutions', 'Manufacturing', 'Products', 'Industries', 'Operations']

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)

    company_name = prefix + ' ' + suffix
    return company_name

def generate_land_based_receiver_company_name():
    prefixes = ['Ocean', 'Sea', 'Marine', 'Coastal', 'Aqua', 'Wave', 'Deep', 'Harbor', 'Fresh', 'Tidal']
    suffixes = ['Seafoods', 'Fisheries', 'Maritime', 'Catches', 'Coast', 'Aquatics', 'Mariscos', 'Delights', 'Bay', 'Catchers']

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)

    company_name = prefix + ' ' + suffix
    return company_name

def generate_fish_farm_name():
    prefixes = ["Ocean", "Aqua", "Marine", "Sea", "Blue", "Nautical"]
    suffixes = ["Fish Farm", "Aquafarm", "Fishery", "Aquaculture", "Fish Haven"]

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)

    company_name = prefix + ' ' + suffix
    return company_name

#Function that generates a business entity record
def generate_entity_record(fake, entity_types=entity_types):
    #Randomly select the entity name type
    b_type = random.choice(entity_types)

    #Create a dictionary to call the generate name function based on the type of entity
    names_dict = {
        'farm':generate_farm_name,
        'wholesaler':generate_wholesaler_name,
        'grocery':generate_grocery_name,
        'groceryNoTransform':generate_grocery_name,
        'distributor':generate_distributor_name,
        'packaging':generate_packaging_company_name,
        'restaurant':generate_restaurant_name,
        'processor':generate_food_processing_company_name,
        'landBasedReceiver':generate_land_based_receiver_company_name,
        'seafoodFarm':generate_fish_farm_name
    }

    states_with_commercial_fishing = [
        "AK",  # Alaska
        "LA",  # Louisiana
        "WA",  # Washington
        "VA",  # Virginia
        "OR",  # Oregon
        "MD",  # Maryland
        "TX",  # Texas
        "FL",  # Florida
        "MA",  # Massachusetts
        "NC",  # North Carolina
        "ME",  # Maine
        "MS",  # Mississippi
        "CA",  # California
        "NJ",  # New Jersey
        "RI",  # Rhode Island
        "NY",  # New York
        "HI",  # Hawaii
        "GA",  # Georgia
        "AL",  # Alabama
        "SC",  # South Carolina
        "CT",  # Connecticut
        "NH",  # New Hampshire
        "DE",  # Delaware
    ]

    #Determine the state 
    if b_type == 'seafoodFarm' or b_type == 'landBasedReceiver':
        state = random.choice(states_with_commercial_fishing)
    else:
        state = fake.state_abbr()


    #Put the entity into a dictionary
    entity = {
        'businessType':b_type,
        'businessName':names_dict[b_type](),
        'primaryPhone':fake.basic_phone_number(),
        'streetAddress':fake.street_address(),
        'city':fake.city(),
        'state':state,
        'zip':fake.zipcode(),
        'companyPrefix':f"{random.choice(['06','07','08','09','10','11','12','13'])}{random.randint(10000, 99999)}"
    }

    return entity

#Create a function to generate however many business entities that the user chooses, the base amount is 10,000
def generate_business_entities(n=10000):
    fake = Faker()
    entities = []

    for _ in range(n):
        entities.append(generate_entity_record(fake))

    entities_df = pd.DataFrame(entities)
    return entities_df

