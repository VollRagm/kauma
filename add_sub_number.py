def add_numbers(assignment):
    arugments = assignment["arguments"]
    return {"sum": int(arugments["number1"]) + int(arugments["number2"])}

def subtract_numbers(assignment):
    arguments = assignment["arguments"]
    return {"difference": int(arguments["number1"]) - int(arguments["number2"])}
