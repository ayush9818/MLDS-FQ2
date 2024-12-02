import json

def lambda_handler(event, context):
  try:
    #number1 = int(event['n1'])
    #number2 = int(event['n2'])
       
    print("call to add2...")
       
    params = event["queryStringParameters"]
      
    number1 = int(params["n1"])
    number2 = int(params["n2"])
        
    print("adding", number1, '+', number2)
        
    sum = number1 + number2
        
    print("sum:", sum)
       
    return {
      'statusCode': 200,
      'body': json.dumps(sum)
    }
   
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
