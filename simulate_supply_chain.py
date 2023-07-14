#Import libraries
import pandas as pd
import numpy as np
import random
from faker import Faker
from entity_generation import generate_business_entities
from datetime import datetime, timedelta
from tqdm import tqdm
import hashlib

#Take in User Input
entityCount = int(input("Enter how many business entities exist in the supply chain: "))
foodCount = int(input("Enter how many food items you would like to simulate: "))

#Load the core data
ftl_df = pd.read_excel('Data_Generation/GMU-DAEN690-FoodTraceability/ftl_items.xlsx', sheet_name='Sheet1')
entities_df = generate_business_entities(n=entityCount)
#Add GLNs to each location
entities_df['gln']=entities_df['companyPrefix']+'.'+str(random.randint(10000, 99999))


#Data Generation Functions
def generate_supply_chain(ftl_item):
    #Initialize the supply chain variables
    chain = []

    farm = 'farm'
    field_packed = 'fieldPacked'
    packaging_processor = 'packaging'
    food_processor = 'processor'
    kill = 'stop'
    lbr = 'landBasedReceiver'
    direct_sale = 'directToConsumer'
    seaFarm = 'seafoodFarm'
    agg = 'aggregator'
    rest = 'restaurant'
    grocNoFood = 'groceryNoTransform'
    grocFood = 'grocery'
    dist = 'distributor'
    whole = 'wholesaler'


    #Determine if the food will be an empty node item - do this after Zac sends the rest of the supply chain info

    #Farmed Product Supply Chain Route
    if ftl_item.Supply_Chain.values[0] == 'Farmed':
        chain.append(farm)
        #Determine if field packed or processed
        pack_int = random.randint(0,100)
        if pack_int >= 50:
            chain.append(field_packed)
        else:
            chain.append(packaging_processor)

    #Created Product Supply Chain Route
    elif ftl_item.Supply_Chain.values[0] == 'Created':
        chain.append(food_processor)
        if ftl_item.Category.values[0] == 'Cheese' or ftl_item.Category.values[0] == 'Nut Butters':
            rand = random.randint(0,100)
            if rand > 50:
                chain.append(food_processor)
            #Determine Cheese Continued Manufacturing Route
            if ftl_item.Category.values[0] == 'Nut Butters':
                if rand > 75:
                    chain.append(food_processor)
                else:
                    chain.append(kill)
            else:
                chain.append(kill)

    #Fish Supply Chain Route
    elif ftl_item.Category.values[0] == 'Seafood':

        #Caught fish Supply Chain Route
        if ftl_item.Supply_Chain.values[0] == 'Caught':
            chain.append(lbr)
            #Fill in the rest here

        #Aquaculture Supply Chain Route
        if ftl_item.Supply_Chain.values[0] == 'Aquaculture':
            chain.append(seaFarm)

        #Determine if the food will go to an aggregator
        rand = random.randint(0,100)
        if rand > 50:
            chain.append(agg)

        #Determine if the food goes through a kill step or continues to get processed
        chain.append(food_processor)

        rand = random.randint(0,100)
        if rand > 50:
            chain.append(food_processor)

            if rand > 75:
                chain.append(food_processor)

            else:
                chain.append(kill)

        else:
            chain.append(kill)

            
    if chain[-1] != kill:
        #Initialize the retail options
        retail_options = [rest, grocFood, grocNoFood]
        
        #Sale Route - this will be the same for every food
        sale_int = random.randint(0,100)
        #Determine if it is sold direct-to-consumer
        if sale_int <= 7:
            sale_int = random.randint(0,100)
            if sale_int <= 27:
                chain.append(direct_sale)
            else:
                chain.append(random.choice(retail_options))
        else:
        
            #If not, do the indirect sales route
            route_1 = random.randint(0,100)
            if route_1 <= 50:
                chain.append(dist)
                route_2 = random.randint(0,100)
                if route_2 <= 20:
                    chain.append(whole)
                else:
                    chain.append(random.choice(retail_options))
                
            else:
                chain.append(food_processor)
                route_2 = random.randint(0,100)
                if route_2 <= 50:
                    chain.append(dist)
                    route_2 = random.randint(0,100)
                    if route_2 <= 20:
                        chain.append(whole)
                    else:
                        chain.append(random.choice(retail_options))
                else:
                    route_2 = random.randint(0,100)
                    if route_2 <= 20:
                        chain.append(whole)
                    else:
                        chain.append(random.choice(retail_options))
            if chain[-1] == whole:
                route_int = random.randint(0,100)
                if route_int < 50:
                    chain.append(random.choice(retail_options))

    return chain

#Data Formatting Functions
def generate_reference_document_type_number(facility,event):
    reference_type_number = f"urn:epcglobal:epcis:{event}.{facility.companyPrefix}"
    return reference_type_number

def generate_traceability_lot_code(data,timestamp):
    hash_input = f"{data}{timestamp}"
    hash_value = hashlib.sha1(hash_input.encode()).hexdigest()
    lot_code = f"urn:epc:id:sgtin:{hash_value}"
    return lot_code

#CTE Functions 

field_name_list = ['Field',
              'Bed',
              'Acre',
              'Garden',
              'Grasslands',
              'Ranch',
              'Barn'
              ]

container_name_list = ['Pond',
                       'Pool',
                       'Tank',
                       'Cage']

def harvesting_cte(fake, ftl_item, farm, next_entity, field_name_list = field_name_list, container_name_list=container_name_list):
    #Determine date
    start_date = datetime.strptime('2023-06-01', '%Y-%m-%d')
    end_date = datetime.now()
    date_harvested = str(fake.date_between_dates(date_start=start_date, date_end=end_date))

    data_submitter = farm.businessName
    food_name = ftl_item.Food.values[0]
    quantity = fake.random_int(min=1, max=1000)
    recipient = next_entity.businessName
    unit_of_measure = fake.random_element(elements=('kg', 'g', 'lbs', 'Dozen'))
    farm_name = farm.businessName
    phone_number = farm.primaryPhone
    

    #Contamination
    cont_int = random.randint(0,6000)
    if cont_int == 1:
        contamination = 1
    else:
        contamination = 0 

    #Determine what field or container was used
    if ftl_item.Supply_Chain.values[0] == 'Farmed':
        field_name = random.choice(field_name_list) + ' ' + fake.random_letter() + str(random.randint(1,10))
        container = 'n/a'
    elif ftl_item.Supply_Chain.values[0] == 'Aquaculture':
        field_name = 'n/a'
        container = random.choice(container_name_list) + ' ' + str(random.randint(1,10))
    
    #Need to add location description of farm where it was harvested
    harvesting_info = {
        'dataSubmitter': data_submitter,
        'recipient' : recipient,
        'commodity': food_name,
        'quantity' : quantity,
        'unitOfMeasure' : unit_of_measure,
        'farmName' : farm_name,
        'fieldName' : field_name,
        'containerName' : container,
        'cteDate' : date_harvested,
        'phoneNumber' : phone_number,
        'contaminated' : contamination,  
        'gtin':farm.companyPrefix+'.'+str(random.randint(1000000, 9999999)),
        'sgln':farm.gln,
        'eventID':farm.gln+'.'+str(random.randint(1000000, 9999999)),
        'parentID':''
    }

    return harvesting_info

def cooling_cte(harvesting_info, ftl_item, facility, next_entity):

    data_submitter = facility.businessName
    food_name = ftl_item.Food.values[0]
    quantity = harvesting_info['quantity']
    recipient = next_entity.businessName
    unit_of_measure = harvesting_info['unitOfMeasure']
    farm_name = harvesting_info['dataSubmitter']
    cooler_location = facility.businessName
    date_cooled = harvesting_info['cteDate']
    phone_number = facility.primaryPhone
    contaminated = harvesting_info['contaminated']

    if contaminated == 0:
        if random.randint(0,6000) == 1:
            contaminated = 1
    
    #Need to add location description of farm where it was harvested
    cooling_info = {
        'dataSubmitter': data_submitter,
        'recipient' : recipient,
        'commodity': food_name,
        'quantity' : quantity,
        'unitOfMeasure' : unit_of_measure,
        'coolerLocation' : cooler_location,
        'cteDate' : date_cooled,
        'harvesterName' : farm_name,
        'phoneNumber' : phone_number,
        'contaminated' : contaminated, 
        'gtin':harvesting_info['gtin'],
        'sgln':harvesting_info['sgln'],
        'pgln':facility.gln,
        'eventID':facility.gln+'.'+str(random.randint(1000000, 9999999)),
        'parentID':harvesting_info['eventID']
    }

    return cooling_info

def packaging_cte(fake, harvesting_info, cooling_info, ftl_item, facility):
    # List of packaging types
    packaging_type = ['Box', 'Bag', 'Crate', 'Can', 'Bottle', 'Jar', 'Pouch', 'Carton']

    data_submitter = facility.businessName
    package_type = random.choice(packaging_type)
    quantity = fake.random_int(min=1, max=1000)
    unit_of_measure = fake.random_element(elements=('kg', 'g', 'lbs', 'Dozen'))
    packaging_date = str((datetime.strptime(cooling_info['cteDate'], '%Y-%m-%d') + timedelta(days=random.randint(0,3))).date())
    tLotData = data_submitter + ftl_item.Food.values[0] + str(quantity)
    traceability_lot_code = generate_traceability_lot_code(tLotData,packaging_date)
    product_description = harvesting_info['dataSubmitter'] + ' ' + harvesting_info['commodity'] + ', ' + str(fake.random_int(min=1, max= 50)) + unit_of_measure + ' case'
    contaminated = cooling_info['contaminated']

    if contaminated == 0:
        if random.randint(0,6000) == 1:
            contaminated = 1


    packaging_info = {
        'dataSubmitter': data_submitter,
        'commodity':ftl_item.Food.values[0],
        'dateFoodReceived' : packaging_date,
        'quantityReceived':harvesting_info['quantity'],
        'harvestingLocation':harvesting_info['dataSubmitter'],
        'harvestedField':harvesting_info['fieldName'], #For produce
        'harvestedContainer':harvesting_info['containerName'], #For Aquaculture
        'harvestedPhoneNumber':harvesting_info['phoneNumber'],
        'dateHarvested':harvesting_info['cteDate'],
        'coolingLocation':cooling_info['dataSubmitter'],
        'dateOfCooling':cooling_info['cteDate'],
        'traceabilityLotCode': traceability_lot_code,
        'productDescription':product_description,
        'quantity' : quantity,
        'unitOfMeasure':cooling_info['unitOfMeasure'],
        'packageType': package_type,
        'traceabilityLotCodeSourceLocation':facility.businessName,
        'cteDate' : packaging_date,
        'referenceDocumentTypeNumber': generate_reference_document_type_number(facility,'IP WO'),
        'contaminated':contaminated,
        'gtin':cooling_info['gtin'],
        'sgln':cooling_info['pgln'],
        'pgln':facility.gln,
        'eventID':facility.gln+'.'+str(random.randint(1000000, 9999999)),
        'parentID':cooling_info['eventID']
    }

    return packaging_info

def shipping_cte(previous_cte, next_entity, facility):

    shippedDate = str((datetime.strptime(previous_cte['cteDate'], '%Y-%m-%d') + timedelta(days=random.randint(0,3))).date())
    productDescription = previous_cte['productDescription']
    contaminated = previous_cte['contaminated']
    bizTransactionType = random.choice(['ASN','DESADV','BOL','SHP'])

    if contaminated == 0:
        if random.randint(0,6000) == 1:
            contaminated = 1

    shipping_info = {
        'dataSubmitter': facility.businessName,
        'traceabilityLotCode': previous_cte['traceabilityLotCode'],
        'quantity': previous_cte['quantity'],
        'unitOfMeasure':previous_cte['unitOfMeasure'],
        'productDescription': productDescription,
        'subsequentLocation': next_entity.businessName,
        'previousSourceLocation': previous_cte['dataSubmitter'],
        'cteDate': shippedDate,
        'traceabilityLotCodeSourceLocation': previous_cte['traceabilityLotCodeSourceLocation'],
        'referenceDocumentTypeNumber': generate_reference_document_type_number(facility,bizTransactionType),
        'contaminated':contaminated,
        'gtin':previous_cte['gtin'],
        'sgln':previous_cte['pgln'],
        'pgln':facility.gln,
        'eventID':facility.gln+'.'+str(random.randint(1000000, 9999999)),
        'parentID':previous_cte['eventID']
    }

    return shipping_info

def receiving_cte(previous_cte, facility):
    receivingDate = str((datetime.strptime(previous_cte['cteDate'], '%Y-%m-%d') + timedelta(days=random.randint(0,3))).date())

    contaminated = previous_cte['contaminated']
    bizTransactionType = random.choice(['BOL','RECADV','RECEIPT','RCV'])
    

    if contaminated == 0:
        if random.randint(0,6000) == 1:
            contaminated = 1

    receiving_info = {
        'dataSubmitter': facility.businessName,
        'traceabilityLotCode': previous_cte['traceabilityLotCode'],
        'quantity': previous_cte['quantity'],
        'unitOfMeasure':previous_cte['unitOfMeasure'],
        'productDescription': previous_cte['productDescription'],
        'previousSourceLocation': previous_cte['dataSubmitter'],
        'receivingLocation': facility.businessName,
        'cteDate': receivingDate,
        'traceabilityLotCodeSourceLocation': previous_cte['traceabilityLotCodeSourceLocation'],
        'referenceDocumentTypeNumber': generate_reference_document_type_number(facility,bizTransactionType),
        'contaminated':contaminated,
        'gtin':previous_cte['gtin'],
        'sgln':previous_cte['pgln'],
        'pgln':facility.gln,
        'eventID':facility.gln+'.'+str(random.randint(1000000, 9999999)),
        'parentID':previous_cte['eventID']
    }

    return receiving_info

#Transformation
def transformation_cte(previous_cte, ftl_item, facility):
    
    #creating universal variables
    quantity = random.randint(1,1000)
    quantityUsed = random.randint(quantity,2000)
    unitOfMeasure = random.choice([ 'oz', 'lbs', 'kg'])
    dataSubmitter = facility.businessName
    tLotData = dataSubmitter + ftl_item.Food.values[0] + str(quantity)
    
    #generating transformation date and lot codes - this is dependent on whether there was a previous cte or not
    try: 
        transformedDate = str((datetime.strptime(previous_cte['cteDate'], '%Y-%m-%d') + timedelta(days=random.randint(0,3))).date())
        traceabilityLotCode = generate_traceability_lot_code(tLotData,transformedDate)
        oldTraceabilityLotCode = previous_cte['traceabilityLotCode']
        oldProductDescription = previous_cte['productDescription']
        previousUnitOfMeasure = previous_cte['unitOfMeasure']
        oldGtin = previous_cte['gtin']
        sgln = previous_cte['pgln']
        eventID = facility.gln+'.'+str(random.randint(1000000, 9999999))
        parentID = previous_cte['eventID']

        
    except:
        start_date = datetime.strptime('06/01/2023', '%m/%d/%Y')
        end_date = datetime.now()
        transformedDate = str(fake.date_between(start_date=start_date, end_date=end_date))
        oldProductDescription = ''
        oldTraceabilityLotCode = generate_traceability_lot_code(dataSubmitter + ftl_item.Food.values[0] + str(random.randint(3000,10000)),start_date)
        traceabilityLotCode = generate_traceability_lot_code(tLotData,transformedDate)
        previousUnitOfMeasure = random.choice([ 'oz', 'lbs', 'kg'])
        oldGtin = ''
        sgln = facility.gln
        eventID = facility.gln+'.'+str(random.randint(1000000, 9999999))
        parentID = ''
    
    #transforming foods
    #fruit
    if ftl_item.Category.values[0] == 'Fruit': 
        shortDescription = "Fresh Cut " + ftl_item.Food.values[0]
    elif ftl_item.Category.values[0] == 'Melons': 
        shortDescription = "Fresh Cut " + ftl_item.Food.values[0]
    elif ftl_item.Category.values[0] == 'Tropical Tree Fruits': 
        shortDescription = "Fresh Cut " + ftl_item.Food.values[0]
    
    #nut butter
    elif ftl_item.Category.values[0] == 'Nut Butter':
        shortDescription = ftl_item.Food.values[0] + " Butter"
   
    #salads
    elif ftl_item.Category.values[0] == 'Shell Eggs':
        shortDescription = "Egg Salad"
    elif ftl_item.Category.values[0] == 'Crustaceans': 
        shortDescription = "Seafood Salad"
    elif ftl_item.Category.values[0] == 'Leafy greens (fresh)': 
        shortDescription = "Pasta Salad"
    elif ftl_item.Category.values[0] == 'Peppers': 
        shortDescription = "Pasta Salad"
    elif ftl_item.Category.values[0] == 'Tomatoes': 
        shortDescription = "Pasta Salad"
    elif ftl_item.Category.values[0] == 'Cucumbers (fresh)': 
        shortDescription = "Pasta Salad"
    elif ftl_item.Category.values[0] == 'Herbs (fresh)': 
        shortDescription = random.choice(['Egg Salad','Potato Salad','Pasta Salad','Seafood Salad']) 
    
    #fish
    elif ftl_item.Category.values[0] == 'Seafood':
        if random.randint(0,100) < 15:
            shortDescription = "Smoked " + ftl_item.Food.values[0]
        else:
            shortDescription = ftl_item.Food.values[0] + " filet"
    
    #remaining foods
    else:
        shortDescription = ''
    
    #generates product description dependent on whether food has been transformed previously 
    if shortDescription != '' :
        productDescription = facility.businessName+ ' ' + shortDescription + ', ' +str(quantity) + unitOfMeasure + ' case'
    else:
        productDescription = facility.businessName+ ' ' + ftl_item.Food.values[0] + ', ' +str(quantity) + unitOfMeasure + ' case'
    
    #Contamination
    try:
        contaminated = previous_cte['contaminated']
    except:
        contaminated = 0

    if contaminated == 0:
        if random.randint(0,6000) == 1:
            contaminated = 1

    bizTransactionType = random.choice(['TRF','TE','ADJUSTMENT'])
    
    transformation_info = {
        'dataSubmitter': dataSubmitter,
        'oldTraceabilityLotCode': oldTraceabilityLotCode,
        'oldProductDescription':oldProductDescription,
        'quantityUsed':quantityUsed,
        'previousUnitOfMeasure':previousUnitOfMeasure,
        'traceabilityLotCode': traceabilityLotCode,
        'traceabilityLotCodeSourceLocation': facility.businessName,
        'cteDate': transformedDate,
        'productDescription': productDescription,
        'quantity': quantity,
        'unitOfMeasure': unitOfMeasure,
        'referenceDocumentTypeNumber': generate_reference_document_type_number(facility,bizTransactionType),
        'contaminated':contaminated,
        'inputGtin':oldGtin,
        'gtin':facility.companyPrefix+'.'+str(random.randint(1000000, 9999999)),
        'sgln':sgln,
        'pgln':facility.gln,
        'shortDescription':shortDescription,
        'eventID':eventID,
        'parentID':parentID
    }

    return transformation_info

def first_land_based_receiver_cte(fake, ftl_item, facility):
    #Determine the dates of harvest and landing
    start_date = datetime.strptime('2023-06-01', '%Y-%m-%d')
    end_date = datetime.now()
    firstHarvestDate = fake.date_between_dates(date_start=start_date, date_end=end_date)
    secondHarvestDate = firstHarvestDate + timedelta(days=random.randint(2,10))

    dateLanded = secondHarvestDate + timedelta(days=random.randint(1,3))

    dataSubmitter =facility.businessName

    #Determine Harvest Location
    secondLine = 'Major Fishing Area ' + str(random.randint(1,10))

    pacific_states = ['WA','OR','CA','HI','AK']

    if facility.state in pacific_states:
        ocean = 'Pacific'
    else:
        ocean ='Atlantic'

    thirdLine = random.choice(['Northern', 'Southern', 'Central']) + ' ' + ocean 

    harvestDateAndLocation = str(firstHarvestDate) + ' - ' + str(secondHarvestDate) + '\n' + secondLine + '\n' + thirdLine

    #Determine the quantity and unit of measure
    quantity = random.randint(20,1000)
    unitOfMeasure = random.choice(['kg', 'lb'])

    #Determine the traceability lot code
    tLotData = dataSubmitter + ftl_item.Food.values[0] + str(quantity)
    traceability_lot_code = generate_traceability_lot_code(tLotData,str(dateLanded))

    #Contamination
    contaminated = 0
    if random.randint(0,2000) == 1:
        contaminated = 1


    first_land_based_receiver_info = {
        'dataSubmitter':dataSubmitter,
        'traceabilityLotCode':traceability_lot_code,
        'productDescription':ftl_item.Food.values[0],
        'quantity':quantity,
        'unitOfMeasure':unitOfMeasure,
        'harvestDateAndLocation':harvestDateAndLocation,
        'traceabilityLotCodeSourceLocation':facility.businessName,
        'cteDate':str(dateLanded),
        'referenceDocumentTypeNumber': generate_reference_document_type_number(facility,'LANDING'),
        'contaminated':contaminated,
        'gtin':facility.companyPrefix+'.'+str(random.randint(1000000, 9999999)),
        'sgln':facility.gln,
        'pgln':facility.gln,
        'eventID':facility.gln+'.'+str(random.randint(1000000, 9999999)),
        'parentID':''
    }

    return first_land_based_receiver_info

# Supply Chain Functions

def farm_function(fake, ftl_item, sc, entities, previous_cte, index):
    farm = entities.iloc[index]
    packaged_type = sc[sc.index('farm') + 1]

    try:
        next_entity = entities.iloc[index+1]

    except:
        next_entity = farm

    #Initialize the CTEs for the farm
    ctes = {}

    #Determine what the next entity is for the KDEs that happen on the farm
    if packaged_type == 'fieldPacked':
        ctes['harvesting'] = harvesting_cte(fake, ftl_item, farm, farm)
        ctes['cooling'] = cooling_cte(ctes['harvesting'], ftl_item, farm, farm)
        ctes['initialPackaging'] = packaging_cte(fake,ctes['harvesting'],ctes['cooling'],ftl_item,farm)
        ctes['shipping'] = shipping_cte(ctes['initialPackaging'],next_entity,farm)
    elif packaged_type == 'packaging':
        ctes['harvesting'] = harvesting_cte(fake, ftl_item, farm, next_entity)

    return ctes

def initial_fish_function(fake, ftl_item, sc, entities, previous_cte, index):
    category = ftl_item.Supply_Chain.values[0]

    ctes={}
    #Aquaculture route
    if category == 'Aquaculture':
        facility = entities.iloc[index]
        next_entity=facility
        ctes['harvesting'] = harvesting_cte(fake, ftl_item, facility, next_entity)
        ctes['cooling'] = cooling_cte(ctes['harvesting'], ftl_item, facility, next_entity)
        ctes['initialPackaging'] = packaging_cte(fake,ctes['harvesting'],ctes['cooling'],ftl_item,facility)

    #Wild Caught Route
    elif category =='Caught':
        facility = entities.iloc[index]
        ctes['firstLandBasedReceiving'] = first_land_based_receiver_cte(fake, ftl_item, facility)

    #Ship to the next entity
    last_cte = list(ctes.keys())[-1]
    ctes['shipping'] = shipping_cte(ctes[last_cte],next_entity=entities.iloc[index+1],facility=facility)

    return ctes 

def processing_plant_function(fake, ftl_item, sc, entities, previous_cte, index):

    facility = entities.iloc[index]
    try:
        next_entity = entities.iloc[index+1]
        kill = 0
    except:
        kill = 1

    # Initialize the CTEs for the processing plant
    ctes = {}

    #The path if it is a created product and the first step in the supply chain
    if index == 0:
        ctes['transformation'] = transformation_cte(previous_cte,ftl_item,facility)

    #The path if it is not the first step in the supply chain
    else:

        ctes['receiving'] = receiving_cte(previous_cte, facility)
        ctes['transformation'] = transformation_cte(ctes['receiving'], ftl_item, facility)

    #Determine if a kill step had happened, if not proceed
    if kill == 0:
        ctes['shipping'] = shipping_cte(ctes['transformation'], next_entity, facility)
    
    return ctes

def coolingpacking_function(fake, ftl_item, sc, entities, previous_cte, index):
    # Initialize the CTEs for the offsite cooling and packing facility
    facility = entities.iloc[index]

    try:
        next_entity = entities.iloc[index+1]
        kill = 0
    except:
        next_entity = 0
        kill = 1

    ctes = {}

    ctes['cooling'] = cooling_cte(previous_cte, ftl_item, facility, facility)
    ctes['initialPackaging'] = packaging_cte(fake,previous_cte,ctes['cooling'],ftl_item, facility)

    if kill == 0:
        ctes['shipping'] = shipping_cte(ctes['initialPackaging'], next_entity=next_entity, facility=facility)

    return ctes

def distributor_function(fake, ftl_item, sc, entities, previous_cte, index):
    facility = entities.iloc[index]
    next_entity = entities.iloc[index+1]

    # Initialize the CTEs for the processing plant
    ctes = {}

    ctes['receiving'] = receiving_cte(previous_cte, facility)

    ctes['shipping'] = shipping_cte(ctes['receiving'], next_entity, facility)

    return ctes

def wholesaler_function(fake, ftl_item, sc, entities, previous_cte, index):
    facility = entities.iloc[index]

    try:
        next_entity = entities.iloc[index+1]
        kill = 0

    except:
        kill = 1

    # Initialize the CTEs for the processing plant
    ctes = {}

    ctes['receiving'] = receiving_cte(previous_cte, facility)

    #Determine if there is going to be a transformation or not
    if random.randint(0,100) > 50:
        ctes['transformation'] = transformation_cte(ctes['receiving'], ftl_item, facility)

    if kill == 0:
        last_cte = list(ctes.keys())[-1]
        ctes['shipping'] = shipping_cte(ctes[last_cte], next_entity, facility)

    return ctes

def grocery_function(fake, ftl_item, sc, entities, previous_cte, index):
    facility = entities.iloc[index]

    # Initialize the CTEs for the processing plant
    ctes = {}

    ctes['receiving'] = receiving_cte(previous_cte, facility)

    #Determine if there is going to be a transformation or not
    if random.randint(0,100) < 10:
        ctes['transformation'] = transformation_cte(ctes['receiving'], ftl_item, facility)

    return ctes

def restaurant_function(fake, ftl_item, sc, entities, previous_cte, index):
    facility = entities.iloc[index]

    # Initialize the CTEs for the processing plant
    ctes = {}

    ctes['receiving'] = receiving_cte(previous_cte, facility)

    #Determine if there is going to be a transformation or not
    if random.randint(0,100) > 95:
        ctes['transformation'] = transformation_cte(ctes['receiving'], ftl_item, facility)

    return ctes

def grocery_no_transform_function(fake, ftl_item, sc, entities, previous_cte, index):
    facility = entities.iloc[index]

    # Initialize the CTEs for the processing plant
    ctes = {}

    ctes['receiving'] = receiving_cte(previous_cte, facility)

    return ctes

#Generate the data functions

def generate_data(ftl_df, entities_df, n=10000):
    fake = Faker()

    #Create a dictionary of the functions so that they can be called in the supply chain based on the type of entity
    functions_dict = {
        'farm':farm_function,
        'wholesaler':wholesaler_function,
        'grocery':grocery_function,
        'groceryNoTransform':grocery_no_transform_function,
        'distributor':distributor_function,
        'packaging':coolingpacking_function,
        'restaurant':restaurant_function,
        'processor':processing_plant_function,
        'landBasedReceiver':initial_fish_function,
        'seafoodFarm':initial_fish_function
    }

    all_ctes = []
    for _ in tqdm(range(n)):
        #Randomly select a food item and generate the supply chain
        food_item = ftl_df.sample()
        sc = generate_supply_chain(food_item)

        #Determine the entities for the supply chain
        indexes = []
        for entity_type in sc:
            try:
                entity = entities_df[entities_df.businessType == entity_type].sample().index.values[0]
                indexes.append(entity)
            except:
                pass

        entities = entities_df.iloc[indexes].reset_index(drop=True)

        #Run the function for each entity in the supply chain
        #Note: the input for each function will be (fake, food_item, sc, entities, previous_cte, index)
        #A standardized input makes it easy to iterate through and call each function
        #In plain language, it is calling an instance of faker, the current food_item, the supply chain, the entities in the supply chain, the most recent CTE, and the index
        ctes = []
        for index in entities.index:
            try:
                previous_cte_name = list(ctes[-1].keys())[-1]
                previous_cte = ctes[-1][previous_cte_name]
            except:
                previous_cte = []

            ctes.append(functions_dict[entities.iloc[index].businessType](fake, food_item, sc, entities,previous_cte,index))
        
            

        all_ctes.extend(ctes)

    return all_ctes

#Cross contaminate function
def cross_contaminate(dfs):
    cross_contamination_probability = random.choice([3,5,8])
    later_ctes = [
        'shipping',
        'receiving'
    ]

    for i in dfs['transformation'][dfs['transformation'].contaminated == 1].index:

        row = dfs['transformation'].iloc[i]
        facility = row.dataSubmitter

        #Determine dates of possible contamination
        try:
            start_date = datetime.strptime(str(row.cteDate),'%Y-%m-%d')
        except:
            start_date = row.cteDate
        try:
            end_date = datetime.strptime(dfs['shipping'][dfs['shipping'].traceabilityLotCode == row.traceabilityLotCode].cteDate)
        except:
            end_date = start_date + timedelta(days=3)

        #Filter the data for rows that were possibly impacted by the contamination
        filterData = dfs['transformation']
        filterData['cteDate'] = pd.to_datetime(filterData['cteDate'])
        impacted = filterData[(filterData.dataSubmitter == facility)&(filterData.cteDate >= start_date)&(filterData.cteDate <= end_date)]
        if len(impacted) > 0:

            #Determine if it will spread to the node or not
            infected = []
            infectedLots = []
            for record in impacted.index:
                if random.randint(0,10) < cross_contamination_probability:
                    infectedGroup = [record]
                    infectedLot = impacted.loc[record].traceabilityLotCode
                    infectedLots.append(infectedLot)
                    infectedGroup.extend(filterData[filterData.oldTraceabilityLotCode == infectedLot].index)
                    infected.extend(list(set(infectedGroup)))

            #Spread the infection to the rows
            dfs['transformation'].loc[infected,'contaminated'] = 1

            #Spread the infection to every row in all other CTEs that were impacted
            for cte in later_ctes:
                dfs[cte].loc[dfs[cte][dfs[cte].traceabilityLotCode.isin(infectedLots)].index,'contaminated'] = 1
    return dfs

#Create CSV files of the data
def create_dfs(data, create_csv = False):
    cte_data = {
        'harvesting' : [],
        'cooling' : [],
        'initialPackaging' : [],
        'firstLandBasedReceiving' : [],
        'shipping' : [],
        'receiving' : [],
        'transformation' : []
    }


    for entity in data:
        for type in list(entity.keys()):
            cte_data[type].append(entity[type]) 

    for event in list(cte_data.keys()):
        cte_data[event] = pd.DataFrame(cte_data[event])
    
    #Cross contaminate
    cte_data = cross_contaminate(cte_data)

    #Create a csv of data
    if create_csv == True:
        for event in list(cte_data.keys()):
            cte_data[event].to_csv(f'{event}.csv',index=False) #Uncomment this to create a csv

    return cte_data


fake = Faker()
data = generate_data(ftl_df, entities_df, n=foodCount)

#Cross-contaminate and create dfs
dfs = create_dfs(data,create_csv=True)