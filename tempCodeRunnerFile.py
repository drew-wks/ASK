with open("config/dummy_response.pkl", "rb") as file:
    dummy_response = pickle.load(file)
    print(dummy_response)