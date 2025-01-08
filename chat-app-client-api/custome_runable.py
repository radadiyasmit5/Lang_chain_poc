from langchain.schema.runnable import Runnable
import requests

class MyApiRunnable(Runnable):
    print("hello")
    """A Runnable that calls a custom external API or internal service."""
    def invoke(self, input_data: dict,config=None) -> dict:
        # Suppose we have an external endpoint that expects a POST with JSON data
        response = requests.get("https://wft-geo-db.p.rapidapi.com/v1/geo/adminDivisions"
                                # , json=input_data
                                )
        print(response)
        return response.json()
